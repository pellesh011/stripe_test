import pytest
from django.test import Client
from django.urls import reverse

from payments.domain.entities.cart import Cart
from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.order import Order, OrderStatus


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.mark.django_db
def test_get_orders_returns_empty(client):
    response = client.get(reverse("order-list"))

    assert response.status_code == 200
    assert response.json() == {"orders": [], "total": 0}


@pytest.mark.django_db
def test_get_orders_returns_orders(client, order, order_item):
    assert order.id is not None
    assert order_item.id is not None

    response = client.get(reverse("order-list"))

    assert response.status_code == 200
    data = response.json()
    assert len(data["orders"]) == 1
    entry = data["orders"][0]
    assert entry["id"] == order.id
    assert entry["status"] == OrderStatus.CREATED.value
    assert entry["currency"] == "eur"
    assert entry["subtotal"] == "10.00"
    assert entry["discount_amount"] == "1.00"
    assert entry["tax_amount"] == "0.00"
    assert entry["total"] == "9.00"
    assert entry["discount"] == {
        "id": order.discount.id,
        "name": order.discount.name,
        "type": order.discount.type.value,
        "value": str(order.discount.value),
    }
    assert entry["tax"] is None
    assert isinstance(entry["created_at"], str)
    assert len(entry["items"]) == 1
    item = entry["items"][0]
    assert item["product_id"] == order_item.product.id
    assert item["product_name"] == order_item.product.name
    assert item["price"] == str(order_item.price)
    assert item["currency"] == order.currency.value
    assert item["product_price"]["id"] == order_item.product_price.id
    assert item["product_price"]["currency"] == order_item.product_price.currency.value
    assert item["product_price"]["price"] == str(order_item.product_price.price)


@pytest.mark.django_db
def test_get_orders_returns_tax_amount(client, order_repo, order, order_item, tax):
    assert order.id is not None
    order.add_tax(tax)
    order_repo.save(order)

    response = client.get(reverse("order-list"))

    assert response.status_code == 200
    entry = response.json()["orders"][0]
    assert entry["tax_amount"] == "1.80"
    assert entry["total"] == "10.80"
    assert entry["tax"] == {
        "id": tax.id,
        "name": tax.name,
        "rate": tax.rate,
    }


@pytest.mark.django_db
def test_get_orders_returns_payment_intent(
    client, payment_attempt_repo, payment_attempt
):
    assert payment_attempt.id is not None
    payment_attempt.external_id = "pi_test_123"
    payment_attempt.client_secret = "pi_test_123_secret_secret"
    payment_attempt_repo.save(payment_attempt)

    response = client.get(reverse("order-list"))

    assert response.status_code == 200
    entry = response.json()["orders"][0]
    assert entry["payment_intent"] == {
        "id": "pi_test_123",
        "client_secret": "pi_test_123_secret_secret",
    }


@pytest.mark.django_db
def test_get_orders_returns_payment_intent_null_without_attempt(client, order):
    assert order.id is not None

    response = client.get(reverse("order-list"))

    assert response.status_code == 200
    entry = response.json()["orders"][0]
    assert entry["payment_intent"] is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [
        OrderStatus.PAID,
        OrderStatus.CANCELLED,
        OrderStatus.COMPLETED,
        OrderStatus.REFUNDED,
    ],
)
def test_get_orders_does_not_return_payment_intent_for_finished_order(
    client, order_repo, order, payment_attempt_repo, payment_attempt, status
):
    assert order.id is not None
    assert payment_attempt.id is not None
    payment_attempt.external_id = "pi_test_123"
    payment_attempt.client_secret = "pi_test_123_secret_secret"
    payment_attempt_repo.save(payment_attempt)
    order.status = status
    order_repo.save(order)

    response = client.get(reverse("order-list"))

    assert response.status_code == 200
    entry = response.json()["orders"][0]
    assert entry["payment_intent"] is None


@pytest.mark.django_db
def test_post_returns_405(client):
    response = client.post(reverse("order-list"))

    assert response.status_code == 405


@pytest.mark.django_db
def test_get_orders_returns_total(client, order):
    assert order.id is not None

    response = client.get(reverse("order-list"))

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["orders"]) == 1


@pytest.mark.django_db
def test_get_orders_pagination_limit_and_offset(client, order_repo, cart_repo, order):
    assert order.id is not None
    for _ in range(4):
        cart = Cart()
        cart_repo.save(cart)
        entity = Order(currency=Currency.EUR, cart=cart)
        order_repo.save(entity)

    response = client.get(
        reverse("order-list"),
        {"limit": 2, "offset": 2},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["orders"]) == 2


@pytest.mark.django_db
def test_get_orders_pagination_defaults(client, order_repo, cart_repo, order):
    assert order.id is not None
    for _ in range(11):
        cart = Cart()
        cart_repo.save(cart)
        entity = Order(currency=Currency.EUR, cart=cart)
        order_repo.save(entity)

    response = client.get(reverse("order-list"))

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 12
    assert len(data["orders"]) == 10


@pytest.mark.django_db
def test_get_orders_offset_beyond_total_returns_empty(client, order):
    assert order.id is not None

    response = client.get(
        reverse("order-list"),
        {"limit": 10, "offset": 100},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["orders"] == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {"limit": "-1"},
        {"offset": "-5"},
        {"limit": "abc"},
        {"offset": "1.5"},
    ],
)
def test_get_orders_invalid_pagination_returns_400(client, params):
    response = client.get(reverse("order-list"), params)

    assert response.status_code == 400
