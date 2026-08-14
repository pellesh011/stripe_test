from decimal import Decimal

import pytest

from payments.application.dto.checkout import CheckoutDTO
from payments.application.use_cases.order.checkout import CheckoutUseCase
from payments.domain.entities.cart import Cart, CartStatus
from payments.domain.entities.cart_item import CartItem
from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.entities.order import OrderStatus
from payments.domain.entities.payment_attempts import PaymentAttemptStatus
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice
from payments.domain.exceptions import (
    CartEmptyError,
    CartNotActiveError,
    DiscountNotActiveError,
    DiscountNotFoundError,
    EntityNotFoundError,
    ProductNotActiveError,
    ProductPriceNotActiveError,
)
from payments.infrastructure.database.models.payment_attempt import (
    PaymentAttemptModel,
)
from payments.infrastructure.database.uow import DjangoUnitOfWork
from payments.infrastructure.services.tax_selector import DefaultTaxSelector
from payments.tests.application.fakes import (
    CLIENT_SECRET,
    PAYMENT_INTENT_ID,
    FakePaymentGateway,
)


def _build_use_case(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway: FakePaymentGateway,
):
    return CheckoutUseCase(
        uow=DjangoUnitOfWork(),
        carts=cart_repo,
        orders=order_repo,
        order_items=order_item_repo,
        exchange_rates=exchange_rate_repo,
        discounts=discount_repo,
        tax_selector=DefaultTaxSelector(tax_repo),
        payments=payment_repo,
        payment_attempts=payment_attempt_repo,
        payment_providers=payment_provider_repo,
        payment_gateway=payment_gateway,
    )


def _build_dto(
    cart_id: int,
    provider_id: int,
    currency: str = "eur",
    discount: str | None = None,
):
    return CheckoutDTO(
        cart_id=cart_id,
        currency=currency,
        provider_id=provider_id,
        discount=discount,
    )


@pytest.mark.django_db
def test_execute_creates_order(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    cart,
    cart_item,
    exchange_rate,
    discount,
    tax,
    payment_provider,
):
    assert cart.id is not None
    assert payment_provider.id is not None
    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )
    dto = _build_dto(
        cart.id,
        payment_provider.id,
        discount=discount.name,
    )

    result = use_case.execute(dto)

    assert result.client_secret == CLIENT_SECRET
    assert len(payment_gateway.calls) == 1

    recorded_order, amount, currency = payment_gateway.calls[0]
    assert recorded_order.id is not None
    assert result.order_id == recorded_order.id
    assert result.amount == Decimal("10.80")
    assert result.currency is Currency.EUR
    assert recorded_order.currency is Currency.EUR
    assert recorded_order.status is OrderStatus.CREATED
    assert len(recorded_order.items) == 1
    assert recorded_order.items[0].price == Decimal("10.00")
    assert recorded_order.tax is not None
    assert recorded_order.tax.id == tax.id
    assert recorded_order.discount is not None
    assert recorded_order.discount.id == discount.id
    assert amount == Decimal("10.80")
    assert currency is Currency.EUR

    loaded_order = order_repo.get_by_id(recorded_order.id)
    assert len(loaded_order.items) == 1
    assert loaded_order.items[0].price == Decimal("10.00")
    assert loaded_order.items[0].exchange_rate.currency is Currency.EUR
    assert loaded_order.tax is not None
    assert loaded_order.tax.id == tax.id
    assert loaded_order.discount is not None
    assert loaded_order.discount.id == discount.id

    loaded_cart = cart_repo.get_by_id(cart.id)
    assert loaded_cart.status is CartStatus.CHECKOUT

    payment = payment_repo.get_by_order_id(recorded_order.id)
    assert payment.amount == Decimal("10.80")
    assert payment.currency is Currency.EUR

    attempts = payment_attempt_repo.get_by_payment_id(payment.id)
    assert len(attempts) == 1
    assert attempts[0].id is not None
    assert attempts[0].provider.id == payment_provider.id
    assert attempts[0].external_id == PAYMENT_INTENT_ID
    assert attempts[0].status is PaymentAttemptStatus.PROCESSING


@pytest.mark.django_db
def test_execute_without_discount_applies_default_tax(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    cart,
    cart_item,
    exchange_rate,
    tax,
    payment_provider,
):
    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )
    dto = _build_dto(cart.id, payment_provider.id)

    result = use_case.execute(dto)

    assert result.client_secret == CLIENT_SECRET
    assert len(payment_gateway.calls) == 1

    recorded_order, amount, currency = payment_gateway.calls[0]
    assert recorded_order.discount is None
    assert recorded_order.tax is not None
    assert recorded_order.tax.id == 1
    assert result.order_id == recorded_order.id
    assert result.amount == Decimal("12.00")
    assert result.currency is Currency.EUR
    assert amount == Decimal("12.00")
    assert currency is Currency.EUR

    payment = payment_repo.get_by_order_id(recorded_order.id)
    assert payment.amount == Decimal("12.00")


@pytest.mark.django_db
def test_execute_gateway_failure_keeps_attempt_created(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    cart,
    cart_item,
    exchange_rate,
    tax,
    payment_provider,
):
    def failing_create_payment(*args, **kwargs):
        raise RuntimeError("provider unavailable")

    payment_gateway.create_payment = failing_create_payment
    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    with pytest.raises(RuntimeError):
        use_case.execute(_build_dto(cart.id, payment_provider.id))

    attempt = PaymentAttemptModel.objects.filter(
        payment__order__cart_id=cart.id
    ).values("external_id", "status")
    assert len(attempt) == 1
    assert attempt[0]["external_id"] is None
    assert attempt[0]["status"] == PaymentAttemptStatus.CREATED.value


@pytest.mark.django_db
def test_execute_cart_not_found(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
):
    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(_build_dto(9999, 9999))

    assert payment_gateway.calls == []


@pytest.mark.django_db
def test_execute_cart_not_active(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    payment_provider,
):
    checkout_cart = Cart()
    cart_repo.save(checkout_cart)
    checkout_cart.status = CartStatus.CHECKOUT
    cart_repo.save(checkout_cart)
    assert checkout_cart.id is not None

    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    with pytest.raises(CartNotActiveError):
        use_case.execute(_build_dto(checkout_cart.id, payment_provider.id))

    assert payment_gateway.calls == []


@pytest.mark.django_db
def test_execute_empty_cart(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    cart,
    payment_provider,
):
    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    with pytest.raises(CartEmptyError):
        use_case.execute(_build_dto(cart.id, payment_provider.id))

    assert payment_gateway.calls == []


@pytest.mark.django_db
def test_execute_inactive_product(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    payment_provider,
):
    inactive = Product(name="Inactive Product", is_active=False)
    product_repo.save(inactive)
    price = ProductPrice(
        currency=Currency.EUR,
        price=Decimal("10.00"),
        product=inactive,
    )
    product_price_repo.save(price)

    cart = Cart()
    cart_repo.save(cart)
    cart_item_repo.save(CartItem(product=inactive, product_price=price, cart=cart))
    assert cart.id is not None
    assert payment_provider.id is not None

    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    with pytest.raises(ProductNotActiveError):
        use_case.execute(_build_dto(cart.id, payment_provider.id))

    assert payment_gateway.calls == []


@pytest.mark.django_db
def test_execute_inactive_product_price(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    payment_provider,
):
    product = Product(name="Active Product", is_active=True)
    product_repo.save(product)
    price = ProductPrice(
        currency=Currency.EUR,
        price=Decimal("10.00"),
        product=product,
    )
    price.set_active(False)
    product_price_repo.save(price)

    cart = Cart()
    cart_repo.save(cart)
    cart_item_repo.save(CartItem(product=product, product_price=price, cart=cart))
    assert cart.id is not None
    assert payment_provider.id is not None

    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    with pytest.raises(ProductPriceNotActiveError):
        use_case.execute(_build_dto(cart.id, payment_provider.id))

    assert payment_gateway.calls == []


@pytest.mark.django_db
def test_execute_discount_not_found(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    cart_item,
    exchange_rate,
    tax,
    payment_provider,
):
    assert cart_item.cart is not None
    cart_id = cart_item.cart.id
    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    with pytest.raises(DiscountNotFoundError):
        use_case.execute(_build_dto(cart_id, payment_provider.id, discount="missing"))

    assert payment_gateway.calls == []


@pytest.mark.django_db
def test_execute_inactive_discount(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    cart_item,
    exchange_rate,
    tax,
    inactive_discount,
    payment_provider,
):
    assert cart_item.cart is not None
    cart_id = cart_item.cart.id
    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    with pytest.raises(DiscountNotActiveError):
        use_case.execute(
            _build_dto(
                cart_id,
                payment_provider.id,
                discount=inactive_discount.name,
            )
        )

    assert payment_gateway.calls == []


@pytest.mark.django_db
def test_execute_exchange_rate_not_found(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    cart_item,
    payment_provider,
):
    assert cart_item.cart is not None
    cart_id = cart_item.cart.id
    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(_build_dto(cart_id, payment_provider.id, currency="rub"))

    assert payment_gateway.calls == []


@pytest.mark.django_db
def test_execute_provider_not_found(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    cart_item,
    exchange_rate,
    tax,
):
    assert cart_item.cart is not None
    cart_id = cart_item.cart.id
    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(_build_dto(cart_id, 9999))

    assert payment_gateway.calls == []


@pytest.mark.django_db
def test_execute_converts_items_in_different_currencies(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    exchange_rate_repo,
    order_repo,
    order_item_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    tax,
    payment_provider,
):
    rub_product = Product(name="Rub Product", is_active=True)
    product_repo.save(rub_product)
    rub_price = ProductPrice(
        currency=Currency.RUB,
        price=Decimal("100.00"),
        product=rub_product,
    )
    product_price_repo.save(rub_price)

    usd_product = Product(name="Usd Product", is_active=True)
    product_repo.save(usd_product)
    usd_price = ProductPrice(
        currency=Currency.USD,
        price=Decimal("10.00"),
        product=usd_product,
    )
    product_price_repo.save(usd_price)

    cart = Cart()
    cart_repo.save(cart)
    cart_item_repo.save(
        CartItem(product=rub_product, product_price=rub_price, cart=cart)
    )
    cart_item_repo.save(
        CartItem(product=usd_product, product_price=usd_price, cart=cart)
    )

    rub_rate = ExchangeRate(
        base_currency=Currency.EUR,
        currency=Currency.RUB,
        coef=Decimal("0.01"),
    )
    exchange_rate_repo.save(rub_rate)
    usd_rate = ExchangeRate(
        base_currency=Currency.EUR,
        currency=Currency.USD,
        coef=Decimal("0.85"),
    )
    exchange_rate_repo.save(usd_rate)

    assert cart.id is not None
    assert payment_provider.id is not None
    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    result = use_case.execute(_build_dto(cart.id, payment_provider.id))

    assert result.client_secret == CLIENT_SECRET
    recorded_order, amount, currency = payment_gateway.calls[0]
    assert currency is Currency.EUR
    assert amount == Decimal("11.40")
    assert result.order_id == recorded_order.id
    assert result.amount == Decimal("11.40")
    assert result.currency is Currency.EUR
    assert len(recorded_order.items) == 2
    prices_by_currency = {
        item.product_price.currency: item.price for item in recorded_order.items
    }
    assert prices_by_currency[Currency.RUB] == Decimal("1.00")
    assert prices_by_currency[Currency.USD] == Decimal("8.50")


@pytest.mark.django_db
def test_execute_missing_exchange_rate_for_item_raises(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    exchange_rate_repo,
    order_repo,
    order_item_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    payment_gateway,
    payment_provider,
):
    rub_product = Product(name="Rub Only Product", is_active=True)
    product_repo.save(rub_product)
    rub_price = ProductPrice(
        currency=Currency.RUB,
        price=Decimal("100.00"),
        product=rub_product,
    )
    product_price_repo.save(rub_price)

    cart = Cart()
    cart_repo.save(cart)
    cart_item_repo.save(
        CartItem(product=rub_product, product_price=rub_price, cart=cart)
    )

    self_rate = ExchangeRate(
        base_currency=Currency.EUR,
        currency=Currency.EUR,
        coef=Decimal("1"),
    )
    exchange_rate_repo.save(self_rate)

    assert cart.id is not None
    assert payment_provider.id is not None
    use_case = _build_use_case(
        cart_repo,
        order_repo,
        order_item_repo,
        exchange_rate_repo,
        discount_repo,
        tax_repo,
        payment_repo,
        payment_attempt_repo,
        payment_provider_repo,
        payment_gateway,
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(_build_dto(cart.id, payment_provider.id))

    assert payment_gateway.calls == []
