import pytest

from payments.application.dto.cart import AddToCartDTO
from payments.application.use_cases.cart.add_to_cart import AddToCartUseCase
from payments.domain.entities.cart import Cart, CartStatus
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice
from payments.domain.exceptions import (
    CartNotActiveError,
    EntityNotFoundError,
    ProductNotActiveError,
    ProductPriceNotActiveError,
)


def _build_use_case(cart_repo, cart_item_repo, product_repo, product_price_repo):
    return AddToCartUseCase(
        carts=cart_repo,
        cart_items=cart_item_repo,
        products=product_repo,
        product_prices=product_price_repo,
    )


def _build_dto(product_id: int, product_price_id: int, cart_id: int | None = None):
    return AddToCartDTO(
        product_id=product_id,
        product_price_id=product_price_id,
        cart_id=cart_id,
    )


@pytest.mark.django_db
def test_execute_creates_new_cart(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    product,
    product_price,
    call,
):
    use_case = _build_use_case(
        cart_repo, cart_item_repo, product_repo, product_price_repo
    )
    dto = _build_dto(product.id, product_price.id, cart_id=None)

    result = call(use_case.execute)(dto)

    assert result.id is not None
    assert result.cart is not None
    assert result.cart.id is not None
    assert result.product.id == product.id
    assert result.product_price.id == product_price.id

    loaded_cart = call(cart_repo.get_by_id)(result.cart.id)
    assert len(loaded_cart.items) == 1
    assert loaded_cart.items[0].id == result.id

    loaded_item = call(cart_item_repo.get_by_id)(result.id)
    assert loaded_item.product.id == product.id
    assert loaded_item.product_price.id == product_price.id


@pytest.mark.django_db
def test_execute_adds_to_existing_cart(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    cart,
    product,
    product_price,
    call,
):
    use_case = _build_use_case(
        cart_repo, cart_item_repo, product_repo, product_price_repo
    )
    dto = _build_dto(product.id, product_price.id, cart_id=cart.id)

    result = call(use_case.execute)(dto)

    assert result.cart is not None
    assert result.cart.id == cart.id

    loaded_cart = call(cart_repo.get_by_id)(cart.id)
    assert len(loaded_cart.items) == 1
    assert loaded_cart.items[0].id == result.id


@pytest.mark.django_db
def test_execute_product_not_found(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    product_price,
    call,
):
    use_case = _build_use_case(
        cart_repo, cart_item_repo, product_repo, product_price_repo
    )
    dto = _build_dto(9999, product_price.id)

    with pytest.raises(EntityNotFoundError):
        call(use_case.execute)(dto)


@pytest.mark.django_db
def test_execute_product_price_not_found(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    product,
    call,
):
    use_case = _build_use_case(
        cart_repo, cart_item_repo, product_repo, product_price_repo
    )
    dto = _build_dto(product.id, 9999)

    with pytest.raises(EntityNotFoundError):
        call(use_case.execute)(dto)


@pytest.mark.django_db
def test_execute_inactive_product_raises(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    product_price,
    call,
):
    inactive = Product(name="Inactive Product", is_active=False)
    call(product_repo.save)(inactive)
    assert inactive.id is not None

    use_case = _build_use_case(
        cart_repo, cart_item_repo, product_repo, product_price_repo
    )
    dto = _build_dto(inactive.id, product_price.id)

    with pytest.raises(ProductNotActiveError):
        call(use_case.execute)(dto)


@pytest.mark.django_db
def test_execute_inactive_product_price_raises(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    product,
    product_price,
    call,
):
    price = ProductPrice(
        currency=product_price.currency,
        price=product_price.price,
        product=product,
    )
    price.set_active(False)
    call(product_price_repo.save)(price)
    assert price.id is not None

    use_case = _build_use_case(
        cart_repo, cart_item_repo, product_repo, product_price_repo
    )
    dto = _build_dto(product.id, price.id)

    with pytest.raises(ProductPriceNotActiveError):
        call(use_case.execute)(dto)


@pytest.mark.django_db
def test_execute_cart_not_found(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    product,
    product_price,
    call,
):
    use_case = _build_use_case(
        cart_repo, cart_item_repo, product_repo, product_price_repo
    )
    dto = _build_dto(product.id, product_price.id, cart_id=9999)

    with pytest.raises(EntityNotFoundError):
        call(use_case.execute)(dto)


@pytest.mark.django_db
def test_execute_cart_not_active_raises(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    product,
    product_price,
    call,
):
    checkout_cart = Cart()
    call(cart_repo.save)(checkout_cart)
    checkout_cart.status = CartStatus.CHECKOUT
    call(cart_repo.save)(checkout_cart)

    use_case = _build_use_case(
        cart_repo, cart_item_repo, product_repo, product_price_repo
    )
    dto = _build_dto(product.id, product_price.id, cart_id=checkout_cart.id)

    with pytest.raises(CartNotActiveError):
        call(use_case.execute)(dto)


@pytest.mark.django_db
def test_execute_price_of_other_product_raises(
    cart_repo,
    cart_item_repo,
    product_repo,
    product_price_repo,
    product,
    product_price,
    call,
):
    other_product = Product(name="Other Product", is_active=True)
    call(product_repo.save)(other_product)
    assert other_product.id is not None

    use_case = _build_use_case(
        cart_repo, cart_item_repo, product_repo, product_price_repo
    )
    dto = _build_dto(other_product.id, product_price.id)

    with pytest.raises(EntityNotFoundError):
        call(use_case.execute)(dto)
