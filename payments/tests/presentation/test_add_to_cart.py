import json

import pytest
from django.test import Client
from django.urls import reverse

from payments.domain.entities.cart import Cart, CartStatus


@pytest.fixture
def client() -> Client:
    return Client()


def _post(client, payload):
    return client.post(
        reverse("cart-add"),
        data=json.dumps(payload),
        content_type="application/json",
    )


def _payload(product_id, product_price_id, cart_id, **overrides):
    body = {
        "product_id": product_id,
        "product_price_id": product_price_id,
        "cart_id": cart_id,
    }
    body.update(overrides)
    return body


@pytest.mark.django_db
def test_add_to_cart_success(client, cart, product, product_price):
    assert product.id is not None
    assert product_price.id is not None
    assert cart.id is not None

    response = _post(client, _payload(product.id, product_price.id, cart.id))

    assert response.status_code == 200
    data = response.json()
    assert data["cart"]["id"] == cart.id
    assert data["cart"]["status"] == CartStatus.ACTIVE.value
    assert len(data["cart"]["items"]) == 1
    item = data["cart"]["items"][0]
    assert item["product_id"] == product.id
    assert item["product_name"] == product.name
    assert item["product_price_id"] == product_price.id
    assert item["currency"] == product_price.currency.value
    assert item["price"] == str(product_price.price)


@pytest.mark.django_db
def test_add_to_cart_get_returns_405(client):
    response = client.get(reverse("cart-add"))

    assert response.status_code == 405


@pytest.mark.django_db
def test_add_to_cart_invalid_json_returns_400(client):
    response = client.post(
        reverse("cart-add"),
        data="{invalid",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.django_db
def test_add_to_cart_missing_field_returns_400(client, cart, product_price):
    assert product_price.id is not None
    assert cart.id is not None
    response = _post(client, {"product_price_id": product_price.id, "cart_id": cart.id})

    assert response.status_code == 400
    assert "product_id" in response.json()["error"]


@pytest.mark.django_db
def test_add_to_cart_invalid_product_id_returns_400(client, cart, product_price):
    assert product_price.id is not None
    assert cart.id is not None
    response = _post(client, _payload("abc", product_price.id, cart.id))

    assert response.status_code == 400
    assert "product_id" in response.json()["error"]


@pytest.mark.django_db
def test_add_to_cart_product_not_found_returns_404(client, cart):
    assert cart.id is not None
    response = _post(client, _payload(9999, 9999, cart.id))

    assert response.status_code == 404
    assert response.json() == {"error": "Entity not found"}


@pytest.mark.django_db
def test_add_to_cart_cart_not_active_returns_400(
    client, cart_repo, product, product_price
):
    assert product.id is not None
    assert product_price.id is not None
    checkout_cart = Cart()
    cart_repo.save(checkout_cart)
    assert checkout_cart.id is not None
    checkout_cart.status = CartStatus.CHECKOUT
    cart_repo.save(checkout_cart)

    response = _post(client, _payload(product.id, product_price.id, checkout_cart.id))

    assert response.status_code == 400
    assert response.json() == {"error": "Cart is not active"}
