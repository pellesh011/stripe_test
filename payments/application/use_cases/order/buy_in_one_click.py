from payments.application.dto.buy_in_one_click import BuyInOneClickDTO
from payments.application.dto.cart import AddToCartDTO
from payments.application.dto.checkout import CheckoutDTO
from payments.application.use_cases.cart.add_to_cart import AddToCartUseCase
from payments.application.use_cases.order.checkout import CheckoutUseCase
from payments.domain.repositories.cart import CartRepository
from payments.domain.repositories.cart_item import CartItemRepository
from payments.domain.repositories.discount import DiscountRepository
from payments.domain.repositories.exchange_rate import ExchangeRateRepository
from payments.domain.repositories.order import OrderRepository
from payments.domain.repositories.order_item import OrderItemRepository
from payments.domain.repositories.payment import PaymentRepository
from payments.domain.repositories.payment_attempt import PaymentAttemptRepository
from payments.domain.repositories.payment_provider import PaymentProviderRepository
from payments.domain.repositories.product import ProductRepository
from payments.domain.repositories.product_price import ProductPriceRepository
from payments.domain.repositories.tax import TaxRepository
from payments.domain.repositories.uow import UnitOfWork
from payments.domain.services.payment_gateway import PaymentGateway


class BuyInOneClickUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        carts: CartRepository,
        cart_items: CartItemRepository,
        products: ProductRepository,
        product_prices: ProductPriceRepository,
        orders: OrderRepository,
        order_items: OrderItemRepository,
        exchange_rates: ExchangeRateRepository,
        discounts: DiscountRepository,
        taxes: TaxRepository,
        payments: PaymentRepository,
        payment_attempts: PaymentAttemptRepository,
        payment_providers: PaymentProviderRepository,
        payment_gateway: PaymentGateway,
    ):
        self._payment_providers = payment_providers
        self._add_to_cart = AddToCartUseCase(
            uow=uow,
            carts=carts,
            cart_items=cart_items,
            products=products,
            product_prices=product_prices,
        )
        self._checkout = CheckoutUseCase(
            uow=uow,
            carts=carts,
            orders=orders,
            order_items=order_items,
            exchange_rates=exchange_rates,
            discounts=discounts,
            taxes=taxes,
            payments=payments,
            payment_attempts=payment_attempts,
            payment_providers=payment_providers,
            payment_gateway=payment_gateway,
        )

    def execute(self, data: BuyInOneClickDTO) -> str:
        provider = self._payment_providers.get_default()
        assert provider.id is not None

        cart_item = self._add_to_cart.execute(
            AddToCartDTO(
                product_id=data.product_id,
                product_price_id=data.product_price_id,
                cart_id=None,
            )
        )
        assert cart_item.cart is not None
        assert cart_item.cart.id is not None

        client_secret = self._checkout.execute(
            CheckoutDTO(
                cart_id=cart_item.cart.id,
                currency=data.currency,
                provider_id=provider.id,
            )
        )

        return client_secret