import pytest

from payments.domain.entities.cart import Cart
from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.order import Order, OrderStatus
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id_not_found(order_repo):
    with pytest.raises(EntityNotFoundError):
        order_repo.get_by_id(9999)


@pytest.mark.django_db
def test_save_create_assigns_id(order_repo, cart):
    entity = Order(currency=Currency.EUR, cart=cart)
    assert entity.id is None

    order_repo.save(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_get_by_id_returns_order_with_cart(order_repo, order):
    assert order.id is not None
    loaded = order_repo.get_by_id(order.id)

    assert loaded.id == order.id
    assert loaded.cart.id == order.cart.id
    assert loaded.currency == order.currency
    assert loaded.status is OrderStatus.CREATED


@pytest.mark.django_db
def test_get_by_id_returns_order_with_discount(order_repo, order):
    assert order.id is not None
    assert order.discount is not None

    loaded = order_repo.get_by_id(order.id)

    assert loaded.discount is not None
    assert loaded.discount.id == order.discount.id
    assert loaded.discount.name == order.discount.name
    assert loaded.discount.value == order.discount.value


@pytest.mark.django_db
def test_get_by_id_returns_order_without_discount(order_repo, cart):
    entity = Order(currency=Currency.EUR, cart=cart)
    order_repo.save(entity)

    assert entity.id is not None
    loaded = order_repo.get_by_id(entity.id)

    assert loaded.discount is None


@pytest.mark.django_db
def test_save_update_status(order_repo, order):
    assert order.id is not None
    order.status = OrderStatus.PENDING_PAYMENT

    order_repo.save(order)

    loaded = order_repo.get_by_id(order.id)
    assert loaded.status is OrderStatus.PENDING_PAYMENT


@pytest.mark.django_db
def test_get_by_id_loads_items(order_repo, order, order_item):
    assert order.id is not None
    loaded = order_repo.get_by_id(order.id)

    assert len(loaded.items) == 1
    assert loaded.items[0].id == order_item.id
    assert loaded.items[0].product.name == order_item.product.name


@pytest.mark.django_db
def test_get_all_returns_empty(order_repo):
    assert order_repo.get_all() == []


@pytest.mark.django_db
def test_get_all_returns_orders(order_repo, order, cart_repo):
    second_cart = Cart()
    cart_repo.save(second_cart)
    assert second_cart.id is not None
    second = Order(currency=Currency.EUR, cart=second_cart)
    order_repo.save(second)

    result = order_repo.get_all()

    assert {item.id for item in result} == {order.id, second.id}


@pytest.mark.django_db
def test_get_all_pagination_limit_and_offset(order_repo, cart_repo, order):
    assert order.id is not None
    for _ in range(3):
        cart = Cart()
        cart_repo.save(cart)
        entity = Order(currency=Currency.EUR, cart=cart)
        order_repo.save(entity)

    result = order_repo.get_all(limit=2, offset=2)

    assert len(result) == 2


@pytest.mark.django_db
def test_count_returns_zero(order_repo):
    assert order_repo.count() == 0


@pytest.mark.django_db
def test_count_returns_total(order_repo, cart_repo, order):
    assert order.id is not None
    cart = Cart()
    cart_repo.save(cart)
    entity = Order(currency=Currency.EUR, cart=cart)
    order_repo.save(entity)

    assert order_repo.count() == 2
