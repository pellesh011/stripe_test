import pytest
from django.test import Client
from django.urls import reverse

from payments.domain.entities.order import OrderStatus


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.mark.django_db
def test_get_orders_returns_empty(client):
    response = client.get(reverse("order-list"))

    assert response.status_code == 200
    assert response.json() == {"orders": []}


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
    assert entry["total"] == "9.00"
    assert len(entry["items"]) == 1
    item = entry["items"][0]
    assert item["product_id"] == order_item.product.id
    assert item["product_name"] == order_item.product.name
    assert item["price"] == str(order_item.price)
    assert item["currency"] == order_item.product_price.currency.value


@pytest.mark.django_db
def test_post_returns_405(client):
    response = client.post(reverse("order-list"))

    assert response.status_code == 405
