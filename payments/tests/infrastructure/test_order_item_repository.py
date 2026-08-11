import pytest

from payments.domain.entities.cart import Cart
from payments.domain.entities.order import Order
from payments.domain.entities.order_item import OrderItem
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id_not_found(order_item_repo):
    with pytest.raises(EntityNotFoundError):
        order_item_repo.get_by_id(9999)


@pytest.mark.django_db
def test_save_requires_order(order_item_repo, product, product_price):
    entity = OrderItem(product=product, product_price=product_price)

    with pytest.raises(ValueError, match="order"):
        order_item_repo.save(entity)


@pytest.mark.django_db
def test_save_create_assigns_id(
    order_item_repo,
    order,
    product,
    product_price,
):
    entity = OrderItem(product=product, product_price=product_price, order=order)
    assert entity.id is None

    order_item_repo.save(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_get_by_id_returns_full_item(order_item_repo, order_item):
    assert order_item.id is not None
    loaded = order_item_repo.get_by_id(order_item.id)

    assert loaded.id == order_item.id
    assert loaded.product.name == order_item.product.name
    assert loaded.product_price.price == order_item.product_price.price


@pytest.mark.django_db
def test_get_by_order_id(order_item_repo, order_item, order):
    assert order.id is not None
    items = order_item_repo.get_by_order_id(order.id)

    assert len(items) == 1
    assert items[0].id == order_item.id


@pytest.mark.django_db
def test_get_by_order_id_pagination_limit_and_offset(
    order_item_repo,
    order_item,
    order,
    product,
    product_price,
):
    for _ in range(2):
        entity = OrderItem(product=product, product_price=product_price, order=order)
        order_item_repo.save(entity)

    assert order.id is not None
    first_page = order_item_repo.get_by_order_id(order.id, limit=2, offset=0)
    second_page = order_item_repo.get_by_order_id(order.id, limit=2, offset=2)

    assert len(first_page) == 2
    assert len(second_page) == 1

    first_ids = {item.id for item in first_page}
    second_ids = {item.id for item in second_page}
    assert first_ids.isdisjoint(second_ids)


@pytest.mark.django_db
def test_get_by_order_id_filters_by_order(
    order_item_repo,
    order_repo,
    cart_repo,
    order_item,
    order,
    product,
    product_price,
    call,
):
    other_cart = Cart(currency=order.currency)
    call(cart_repo.save)(other_cart)
    other_order = Order(currency=order.currency, cart=other_cart)
    order_repo.save(other_order)

    other_item = OrderItem(
        product=product,
        product_price=product_price,
        order=other_order,
    )
    order_item_repo.save(other_item)

    assert order.id is not None
    assert other_order.id is not None
    items = order_item_repo.get_by_order_id(order.id)
    other_items = order_item_repo.get_by_order_id(other_order.id)

    assert [item.id for item in items] == [order_item.id]
    assert [item.id for item in other_items] == [other_item.id]
