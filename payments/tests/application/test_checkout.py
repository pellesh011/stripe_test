from decimal import Decimal

import pytest

from payments.application.dto.checkout import CheckoutDTO
from payments.application.use_cases.order.checkout import CheckoutUseCase
from payments.domain.entities.cart import Cart, CartStatus
from payments.domain.entities.cart_item import CartItem
from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.order import OrderStatus
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
from payments.infrastructure.database.uow import DjangoUnitOfWork


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
):
    return CheckoutUseCase(
        uow=DjangoUnitOfWork(),
        carts=cart_repo,
        orders=order_repo,
        order_items=order_item_repo,
        exchange_rates=exchange_rate_repo,
        discounts=discount_repo,
        taxes=tax_repo,
        payments=payment_repo,
        payment_attempts=payment_attempt_repo,
        payment_providers=payment_provider_repo,
    )


def _build_dto(
    cart_id: int,
    provider_id: int,
    currency: str = "eur",
    discount: str | None = None,
    tax_id: int | None = None,
):
    return CheckoutDTO(
        cart_id=cart_id,
        currency=currency,
        provider_id=provider_id,
        discount=discount,
        tax_id=tax_id,
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
    )
    dto = _build_dto(
        cart.id,
        payment_provider.id,
        discount=discount.name,
        tax_id=tax.id,
    )

    result = use_case.execute(dto)

    assert result.id is not None
    assert result.currency is Currency.EUR
    assert result.status is OrderStatus.CREATED
    assert len(result.items) == 1
    assert result.items[0].price == Decimal("11.00")
    assert result.tax is not None
    assert result.tax.id == tax.id
    assert result.discount is not None
    assert result.discount.id == discount.id
    assert result.total() == Decimal("12.10")

    loaded_order = order_repo.get_by_id(result.id)
    assert len(loaded_order.items) == 1
    assert loaded_order.items[0].price == Decimal("11.00")
    assert loaded_order.items[0].exchange_rate.currency is Currency.EUR
    assert loaded_order.tax is not None
    assert loaded_order.tax.id == tax.id
    assert loaded_order.discount is not None
    assert loaded_order.discount.id == discount.id

    loaded_cart = cart_repo.get_by_id(cart.id)
    assert loaded_cart.status is CartStatus.CONVERTED

    payment = payment_repo.get_by_order_id(result.id)
    assert payment.amount == Decimal("12.10")
    assert payment.currency is Currency.EUR

    attempts = payment_attempt_repo.get_by_payment_id(payment.id)
    assert len(attempts) == 1
    assert attempts[0].id is not None
    assert attempts[0].provider.id == payment_provider.id


@pytest.mark.django_db
def test_execute_without_discount_and_tax(
    cart_repo,
    order_repo,
    order_item_repo,
    exchange_rate_repo,
    discount_repo,
    tax_repo,
    payment_repo,
    payment_attempt_repo,
    payment_provider_repo,
    cart,
    cart_item,
    exchange_rate,
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
    )
    dto = _build_dto(cart.id, payment_provider.id)

    result = use_case.execute(dto)

    assert result.discount is None
    assert result.tax is None
    assert result.total() == Decimal("11.00")

    payment = payment_repo.get_by_order_id(result.id)
    assert payment.amount == Decimal("11.00")


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
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(_build_dto(9999, 9999))


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
    )

    with pytest.raises(CartNotActiveError):
        use_case.execute(_build_dto(checkout_cart.id, payment_provider.id))


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
    )

    with pytest.raises(CartEmptyError):
        use_case.execute(_build_dto(cart.id, payment_provider.id))


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
    )

    with pytest.raises(ProductNotActiveError):
        use_case.execute(_build_dto(cart.id, payment_provider.id))


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
    )

    with pytest.raises(ProductPriceNotActiveError):
        use_case.execute(_build_dto(cart.id, payment_provider.id))


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
    cart_item,
    exchange_rate,
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
    )

    with pytest.raises(DiscountNotFoundError):
        use_case.execute(_build_dto(cart_id, payment_provider.id, discount="missing"))


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
    cart_item,
    exchange_rate,
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
    )

    with pytest.raises(DiscountNotActiveError):
        use_case.execute(
            _build_dto(
                cart_id,
                payment_provider.id,
                discount=inactive_discount.name,
            )
        )


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
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(_build_dto(cart_id, payment_provider.id, currency="rub"))


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
    cart_item,
    exchange_rate,
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
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(_build_dto(cart_id, 9999))
