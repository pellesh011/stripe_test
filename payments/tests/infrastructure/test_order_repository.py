import pytest

from payments.domain.entities.order import Order, OrderStatus
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id_not_found(order_repo, call):
    with pytest.raises(EntityNotFoundError):
        call(order_repo.get_by_id)(9999)


@pytest.mark.django_db
def test_save_create_assigns_id(order_repo, cart, currency, call):
    entity = Order(currency=currency, cart=cart)
    assert entity.id is None

    call(order_repo.save)(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_get_by_id_returns_order_with_cart(order_repo, order, call):
    assert order.id is not None
    loaded = call(order_repo.get_by_id)(order.id)

    assert loaded.id == order.id
    assert loaded.cart.id == order.cart.id
    assert loaded.currency.currency == order.currency.currency
    assert loaded.status is OrderStatus.CREATED


@pytest.mark.django_db
def test_save_update_status(order_repo, order, call):
    assert order.id is not None
    order.status = OrderStatus.PENDING_PAYMENT

    call(order_repo.save)(order)

    loaded = call(order_repo.get_by_id)(order.id)
    assert loaded.status is OrderStatus.PENDING_PAYMENT


@pytest.mark.django_db
def test_get_by_id_loads_items(order_repo, order, order_item, call):
    assert order.id is not None
    loaded = call(order_repo.get_by_id)(order.id)

    assert len(loaded.items) == 1
    assert loaded.items[0].id == order_item.id
    assert loaded.items[0].product.name == order_item.product.name
