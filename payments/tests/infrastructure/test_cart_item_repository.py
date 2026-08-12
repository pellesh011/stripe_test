import pytest

from payments.domain.entities.cart import Cart
from payments.domain.entities.cart_item import CartItem
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id_not_found(cart_item_repo):
    with pytest.raises(EntityNotFoundError):
        cart_item_repo.get_by_id(9999)


@pytest.mark.django_db
def test_save_requires_cart(cart_item_repo, product, product_price):
    entity = CartItem(product=product, product_price=product_price)

    with pytest.raises(ValueError, match="cart"):
        cart_item_repo.save(entity)


@pytest.mark.django_db
def test_save_create_assigns_id(
    cart_item_repo,
    cart,
    product,
    product_price,
):
    entity = CartItem(product=product, product_price=product_price, cart=cart)
    assert entity.id is None

    cart_item_repo.save(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_get_by_id_returns_full_item(cart_item_repo, cart_item):
    assert cart_item.id is not None
    loaded = cart_item_repo.get_by_id(cart_item.id)

    assert loaded.id == cart_item.id
    assert loaded.product.name == cart_item.product.name
    assert loaded.product_price.price == cart_item.product_price.price


@pytest.mark.django_db
def test_get_by_cart_id(cart_item_repo, cart_item, cart):
    assert cart.id is not None
    items = cart_item_repo.get_by_cart_id(cart.id)

    assert len(items) == 1
    assert items[0].id == cart_item.id


@pytest.mark.django_db
def test_get_by_cart_id_pagination_limit_and_offset(
    cart_item_repo,
    cart_item,
    cart,
    product,
    product_price,
):
    for _ in range(2):
        entity = CartItem(product=product, product_price=product_price, cart=cart)
        cart_item_repo.save(entity)

    assert cart.id is not None
    first_page = cart_item_repo.get_by_cart_id(cart.id, limit=2, offset=0)
    second_page = cart_item_repo.get_by_cart_id(cart.id, limit=2, offset=2)

    assert len(first_page) == 2
    assert len(second_page) == 1

    first_ids = {item.id for item in first_page}
    second_ids = {item.id for item in second_page}
    assert first_ids.isdisjoint(second_ids)


@pytest.mark.django_db
def test_get_by_cart_id_filters_by_cart(
    cart_item_repo,
    cart_repo,
    cart_item,
    cart,
    product,
    product_price,
):
    other_cart = Cart()
    cart_repo.save(other_cart)

    other_item = CartItem(product=product, product_price=product_price, cart=other_cart)
    cart_item_repo.save(other_item)

    assert cart.id is not None
    assert other_cart.id is not None
    items = cart_item_repo.get_by_cart_id(cart.id)
    other_items = cart_item_repo.get_by_cart_id(other_cart.id)

    assert [item.id for item in items] == [cart_item.id]
    assert [item.id for item in other_items] == [other_item.id]
