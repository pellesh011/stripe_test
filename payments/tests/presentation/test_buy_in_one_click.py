import json
from unittest.mock import patch

import pytest
from django.test import Client
from django.urls import reverse


@pytest.fixture
def client() -> Client:
    return Client()


def _post(client, payload):
    return client.post(
        reverse("buy-in-one-click"),
        data=json.dumps(payload),
        content_type="application/json",
    )


def _payload(product_id, product_price_id, **overrides):
    body = {
        "product_id": product_id,
        "product_price_id": product_price_id,
        "currency": "eur",
    }
    body.update(overrides)
    return body


@pytest.mark.django_db
@patch("stripe.PaymentIntent.create")
def test_buy_in_one_click_success(
    mock_create,
    client,
    product,
    product_price,
    exchange_rate,
    payment_provider,
):
    mock_create.return_value.id = "pi_test_123"
    mock_create.return_value.client_secret = "cs_test_secret"
    mock_create.return_value.status = "requires_payment_method"
    assert product.id is not None
    assert product_price.id is not None

    response = _post(client, _payload(product.id, product_price.id))

    assert response.status_code == 200
    assert response.json() == {"client_secret": "cs_test_secret"}


@pytest.mark.django_db
def test_buy_in_one_click_get_returns_405(client):
    response = client.get(reverse("buy-in-one-click"))

    assert response.status_code == 405


@pytest.mark.django_db
def test_buy_in_one_click_invalid_json_returns_400(client):
    response = client.post(
        reverse("buy-in-one-click"),
        data="{invalid",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.django_db
def test_buy_in_one_click_missing_required_field_returns_400(
    client, product_price
):
    response = _post(client, {"product_price_id": product_price.id})

    assert response.status_code == 400
    assert "product_id" in response.json()["error"]


@pytest.mark.django_db
def test_buy_in_one_click_invalid_product_id_returns_400(client, product_price):
    response = _post(client, _payload("abc", product_price.id))

    assert response.status_code == 400
    assert "product_id" in response.json()["error"]


@pytest.mark.django_db
def test_buy_in_one_click_invalid_currency_returns_400(client, product, product_price):
    assert product.id is not None
    assert product_price.id is not None
    response = _post(
        client,
        _payload(product.id, product_price.id, currency="xyz"),
    )

    assert response.status_code == 400
    assert "currency" in response.json()["error"]


@pytest.mark.django_db
def test_buy_in_one_click_product_not_found_returns_404(client):
    response = _post(client, _payload(9999, 9999))

    assert response.status_code == 404
    assert response.json() == {"error": "Entity not found"}


@pytest.mark.django_db
def test_buy_in_one_click_no_provider_returns_404(
    client, product, product_price
):
    assert product.id is not None
    assert product_price.id is not None
    response = _post(client, _payload(product.id, product_price.id))

    assert response.status_code == 404
    assert response.json() == {"error": "Entity not found"}