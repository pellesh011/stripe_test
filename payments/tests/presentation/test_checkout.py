import json

import pytest
from django.test import Client
from django.urls import reverse

from payments.domain.entities.cart import CartStatus


@pytest.fixture
def client() -> Client:
    return Client()


def _post(client, payload):
    return client.post(
        reverse("cart-checkout"),
        data=json.dumps(payload),
        content_type="application/json",
    )


def _payload(cart_id, provider_id, **overrides):
    body = {
        "cart_id": cart_id,
        "currency": "eur",
        "provider_id": provider_id,
    }
    body.update(overrides)
    return body


@pytest.mark.django_db
def test_checkout_success(
    client,
    cart_repo,
    cart,
    cart_item,
    exchange_rate,
    discount,
    tax,
    payment_provider,
):
    response = _post(
        client,
        _payload(
            cart.id,
            payment_provider.id,
            discount=discount.name,
            tax_id=tax.id,
        ),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["currency"] == "eur"
    assert data["status"] == "created"
    assert data["subtotal"] == "11.00"
    assert data["tax_amount"] == "2.20"
    assert data["discount_amount"] == "1.10"
    assert data["total"] == "12.10"
    assert data["tax"] == {"id": tax.id, "name": "VAT", "rate": 20}
    assert data["discount"] == {
        "id": discount.id,
        "name": "Test Discount",
        "type": "percentage",
        "value": "10.00",
    }
    assert len(data["items"]) == 1
    assert data["items"][0]["price"] == "11.00"
    assert data["payment"]["id"] is not None
    assert data["payment"]["amount"] == "12.10"
    assert data["payment"]["currency"] == "eur"
    assert data["payment"]["status"] == "created"

    assert cart_repo.get_by_id(cart.id).status is CartStatus.CONVERTED


@pytest.mark.django_db
def test_checkout_without_optional_fields(
    client, cart, cart_item, exchange_rate, payment_provider
):
    response = _post(client, _payload(cart.id, payment_provider.id))

    assert response.status_code == 200
    data = response.json()
    assert data["tax"] is None
    assert data["discount"] is None
    assert data["total"] == "11.00"
    assert data["payment"]["amount"] == "11.00"


@pytest.mark.django_db
def test_checkout_get_returns_405(client):
    response = client.get(reverse("cart-checkout"))

    assert response.status_code == 405


@pytest.mark.django_db
def test_checkout_invalid_json_returns_400(client):
    response = client.post(
        reverse("cart-checkout"),
        data="{invalid",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.django_db
def test_checkout_missing_required_field_returns_400(client):
    response = _post(client, {"currency": "eur", "provider_id": 1})

    assert response.status_code == 400
    assert "cart_id" in response.json()["error"]


@pytest.mark.django_db
def test_checkout_invalid_provider_id_returns_400(client, cart):
    response = _post(client, _payload(cart.id, "abc"))

    assert response.status_code == 400
    assert "provider_id" in response.json()["error"]


@pytest.mark.django_db
def test_checkout_invalid_currency_returns_400(client, cart, payment_provider):
    response = _post(client, _payload(cart.id, payment_provider.id, currency="xyz"))

    assert response.status_code == 400
    assert "currency" in response.json()["error"]


@pytest.mark.django_db
def test_checkout_cart_not_found_returns_404(client, payment_provider):
    response = _post(client, _payload(9999, payment_provider.id))

    assert response.status_code == 404
    assert response.json() == {"error": "Entity not found"}


@pytest.mark.django_db
def test_checkout_empty_cart_returns_400(client, cart, payment_provider):
    response = _post(client, _payload(cart.id, payment_provider.id))

    assert response.status_code == 400
    assert response.json() == {"error": "Cart is empty"}


@pytest.mark.django_db
def test_checkout_inactive_cart_returns_400(
    client,
    cart_repo,
    cart,
    payment_provider,
):
    cart.status = CartStatus.CHECKOUT
    cart_repo.save(cart)

    response = _post(client, _payload(cart.id, payment_provider.id))

    assert response.status_code == 400
    assert response.json() == {"error": "Cart is not active"}


@pytest.mark.django_db
def test_checkout_discount_not_found_returns_404(
    client,
    cart_item,
    exchange_rate,
    payment_provider,
):
    assert cart_item.cart is not None
    response = _post(
        client,
        _payload(cart_item.cart.id, payment_provider.id, discount="missing"),
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Discount not found"}


@pytest.mark.django_db
def test_checkout_inactive_discount_returns_400(
    client,
    cart_item,
    exchange_rate,
    inactive_discount,
    payment_provider,
):
    assert cart_item.cart is not None
    response = _post(
        client,
        _payload(
            cart_item.cart.id,
            payment_provider.id,
            discount=inactive_discount.name,
        ),
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Discount is not active"}


@pytest.mark.django_db
def test_checkout_missing_exchange_rate_returns_404(
    client,
    cart_item,
    payment_provider,
):
    assert cart_item.cart is not None
    response = _post(
        client,
        _payload(cart_item.cart.id, payment_provider.id, currency="rub"),
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Entity not found"}


@pytest.mark.django_db
def test_checkout_provider_not_found_returns_404(client, cart_item, exchange_rate):
    assert cart_item.cart is not None
    response = _post(client, _payload(cart_item.cart.id, 9999))

    assert response.status_code == 404
    assert response.json() == {"error": "Entity not found"}
