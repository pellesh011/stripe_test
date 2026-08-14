from decimal import Decimal

from payments.application.dto.checkout import CheckoutDTO, CheckoutResult
from payments.domain.entities.cart import Cart, CartStatus
from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.entities.order import Order
from payments.domain.entities.order_item import OrderItem
from payments.domain.entities.payment import Payment
from payments.domain.entities.payment_attempts import (
    PaymentAttempt,
    PaymentAttemptStatus,
)
from payments.domain.exceptions import (
    CartEmptyError,
    CartNotActiveError,
    EntityNotFoundError,
    ProductNotActiveError,
    ProductPriceNotActiveError,
)
from payments.domain.repositories.cart import CartRepository
from payments.domain.repositories.discount import DiscountRepository
from payments.domain.repositories.exchange_rate import ExchangeRateRepository
from payments.domain.repositories.order import OrderRepository
from payments.domain.repositories.order_item import OrderItemRepository
from payments.domain.repositories.payment import PaymentRepository
from payments.domain.repositories.payment_attempt import PaymentAttemptRepository
from payments.domain.repositories.payment_provider import PaymentProviderRepository
from payments.domain.repositories.uow import UnitOfWork
from payments.domain.services.payment_gateway import PaymentGateway
from payments.domain.services.tax_selector import TaxSelector


class CheckoutUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        carts: CartRepository,
        orders: OrderRepository,
        order_items: OrderItemRepository,
        exchange_rates: ExchangeRateRepository,
        discounts: DiscountRepository,
        tax_selector: TaxSelector,
        payments: PaymentRepository,
        payment_attempts: PaymentAttemptRepository,
        payment_providers: PaymentProviderRepository,
        payment_gateway: PaymentGateway,
    ):
        self.uow = uow
        self.carts = carts
        self.orders = orders
        self.order_items = order_items
        self.exchange_rates = exchange_rates
        self.discounts = discounts
        self.tax_selector = tax_selector
        self.payments = payments
        self.payment_attempts = payment_attempts
        self.payment_providers = payment_providers
        self.payment_gateway = payment_gateway

    def execute(self, data: CheckoutDTO) -> CheckoutResult:
        currency = Currency(data.currency)

        with self.uow:
            cart = self.carts.get_by_id_for_update(data.cart_id)
            self._validate(cart)

            exchange_rates = self.exchange_rates.get_all_active_by_code(currency)
            order = self._create_order(
                cart,
                currency,
                exchange_rates,
            )

            order.add_tax(self.tax_selector.select())

            if data.discount is not None:
                order.add_discount(
                    self.discounts.get_active_by_name(data.discount),
                )

            self.orders.save(order)

            for item in order.items:
                self.order_items.save(item)

            cart.status = CartStatus.CHECKOUT
            self.carts.save(cart)

            payment = Payment(
                order=order,
                amount=order.total(),
                currency=order.currency,
            )
            self.payments.save(payment)

            provider = (
                self.payment_providers.get_by_id(data.provider_id)
                if data.provider_id is not None
                else self.payment_providers.get_default()
            )

            payment_attempt = PaymentAttempt(
                provider=provider,
                payment=payment,
                status=PaymentAttemptStatus.CREATED,
            )
            self.payment_attempts.save(payment_attempt)

        payment_intent = self.payment_gateway.create_payment(
            order,
            order.total(),
            order.currency,
        )

        with self.uow:
            payment_attempt = self.payment_attempts.get_by_id_for_update(
                payment_attempt.get_id(),
            )

            payment_attempt.external_id = payment_intent.id
            payment_attempt.status = PaymentAttemptStatus.PROCESSING

            self.payment_attempts.save(payment_attempt)

        assert order.id is not None
        return CheckoutResult(
            order_id=order.id,
            amount=order.total(),
            currency=order.currency,
            client_secret=payment_intent.client_secret,
        )

    @staticmethod
    def _validate(cart: Cart) -> None:
        if cart.status is not CartStatus.ACTIVE:
            raise CartNotActiveError()
        if not cart.items:
            raise CartEmptyError()
        for item in cart.items:
            if not item.product.is_active:
                raise ProductNotActiveError()
            if not item.product_price.is_active:
                raise ProductPriceNotActiveError()

    @staticmethod
    def _create_order(
        cart: Cart,
        currency: Currency,
        exchange_rates: list[ExchangeRate],
    ) -> Order:
        order = Order(currency=currency, cart=cart)
        for cart_item in cart.items:
            exchange_rate = next(
                (
                    rate
                    for rate in exchange_rates
                    if rate.base_currency == currency
                    and rate.currency == cart_item.product_price.currency
                ),
                None,
            )
            if exchange_rate is None:
                raise EntityNotFoundError()
            price = (cart_item.product_price.price * exchange_rate.coef).quantize(
                Decimal("0.01")
            )
            order.add(
                OrderItem(
                    product=cart_item.product,
                    product_price=cart_item.product_price,
                    exchange_rate=exchange_rate,
                    price=price,
                    order=order,
                )
            )
        return order
