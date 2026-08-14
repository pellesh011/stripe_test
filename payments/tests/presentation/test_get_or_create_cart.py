import pytest
from django.test import Client
from django.urls import reverse

from payments.domain.entities.cart import CartStatus


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.mark.django_db
def test_get_creates_cart(client):
    response = client.get(reverse("cart-get-or-create"))

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["cart"]["id"], int)
    assert data["cart"]["status"] == CartStatus.ACTIVE.value
    assert data["cart"]["items"] == []


@pytest.mark.django_db
def test_get_returns_existing_active_cart(client, cart):
    assert cart.id is not None

    response = client.get(reverse("cart-get-or-create"))

    assert response.status_code == 200
    data = response.json()
    assert data["cart"]["id"] == cart.id
    assert data["cart"]["status"] == CartStatus.ACTIVE.value


@pytest.mark.django_db
def test_get_returns_cart_items(client, cart, cart_item):
    assert cart.id is not None

    response = client.get(reverse("cart-get-or-create"))

    assert response.status_code == 200
    data = response.json()
    assert data["cart"]["id"] == cart.id
    assert len(data["cart"]["items"]) == 1
    item = data["cart"]["items"][0]
    assert item["id"] == cart_item.id
    assert item["product_id"] == cart_item.product.id
    assert item["product_name"] == cart_item.product.name
    assert item["product_price_id"] == cart_item.product_price.id
    assert item["currency"] == cart_item.product_price.currency.value
    assert item["price"] == str(cart_item.product_price.price)


@pytest.mark.django_db
def test_post_returns_405(client):
    response = client.post(reverse("cart-get-or-create"))

    assert response.status_code == 405
