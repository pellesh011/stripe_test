from decimal import Decimal

import pytest

from payments.application.dto.buy_in_one_click import BuyInOneClickDTO
from payments.application.use_cases.order.buy_in_one_click import (
    BuyInOneClickUseCase,
)
from payments.domain.entities.cart import CartStatus
from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.order import OrderStatus
from payments.domain.entities.payment_attempts import PaymentAttemptStatus
from payments.domain.exceptions import (
    EntityNotFoundError,
    ProductNotActiveError,
)
from payments.infrastructure.database.uow import DjangoUnitOfWork
from payments.tests.application.fakes import (
    CLIENT_SECRET,
    PAYMENT_INTENT_ID,
    FakePaymentGateway,
)


def _build_use_case(
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
    payment_gateway: FakePaymentGateway,
):
    return BuyInOneClickUseCase(
        uow=DjangoUnitOfWork(),
        carts=cart_repo,
        cart_items=cart_item_repo,
        products=product_repo,
        product_prices=product_price_repo,
        orders=order_repo,
        order_items=order_item_repo,
        exchange_rates=exchange_rate_repo,
        discounts=discount_repo,
        taxes=tax_repo,
        payments=payment_repo,
        payment_attempts=payment_attempt_repo,
        payment_providers=payment_provider_repo,
        payment_gateway=payment_gateway,
    )


def _build_dto(
    product_id: int,
    product_price_id: int,
    currency: str = "eur",
):
    return BuyInOneClickDTO(
        product_id=product_id,
        product_price_id=product_price_id,
        currency=currency,
    )


@pytest.mark.django_db
def test_execute_creates_order_and_converts_cart(
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
    product,
    product_price,
    exchange_rate,
    payment_provider,
):
    assert product.id is not None
    assert product_price.id is not None
    assert payment_provider.id is not None

    use_case = _build_use_case(
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
    )

    result = use_case.execute(_build_dto(product.id, product_price.id))

    assert result == CLIENT_SECRET
    assert len(payment_gateway.calls) == 1

    recorded_order, amount, currency = payment_gateway.calls[0]
    assert recorded_order.id is not None
    assert recorded_order.status is OrderStatus.CREATED
    assert recorded_order.currency is Currency.EUR
    assert len(recorded_order.items) == 1
    assert recorded_order.items[0].product.id == product.id
    assert recorded_order.items[0].price == Decimal("11.00")
    assert amount == Decimal("11.00")
    assert currency is Currency.EUR

    loaded_cart = cart_repo.get_by_id(recorded_order.cart.id)
    assert loaded_cart.status is CartStatus.CONVERTED

    payment = payment_repo.get_by_order_id(recorded_order.id)
    assert payment.amount == Decimal("11.00")

    attempts = payment_attempt_repo.get_by_payment_id(payment.id)
    assert len(attempts) == 1
    assert attempts[0].provider.id == payment_provider.id
    assert attempts[0].external_id == PAYMENT_INTENT_ID
    assert attempts[0].status is PaymentAttemptStatus.PROCESSING


@pytest.mark.django_db
def test_execute_inactive_product_raises(
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
    product,
    product_price,
    exchange_rate,
    payment_provider,
):
    assert product.id is not None
    assert product_price.id is not None
    product.is_active = False
    product_repo.save(product)

    use_case = _build_use_case(
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
    )

    with pytest.raises(ProductNotActiveError):
        use_case.execute(_build_dto(product.id, product_price.id))

    assert payment_gateway.calls == []


@pytest.mark.django_db
def test_execute_no_provider_raises(
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
    product,
    product_price,
    exchange_rate,
):
    assert product.id is not None
    assert product_price.id is not None

    use_case = _build_use_case(
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
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(_build_dto(product.id, product_price.id))

    assert payment_gateway.calls == []