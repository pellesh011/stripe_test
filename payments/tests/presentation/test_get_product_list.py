from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse

from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


@pytest.fixture
def client() -> Client:
    return Client()


def _url(currency=None, limit=None, offset=None) -> str:
    params = {}
    if currency is not None:
        params["currency"] = currency
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    path = reverse("product-list")
    if params:
        path += "?" + "&".join(f"{key}={value}" for key, value in params.items())
    return path


@pytest.mark.django_db
def test_get_products_returns_prices_in_requested_currency(
    client, product, product_price
):
    response = client.get(_url(currency="eur"))

    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) == 1
    payload = data["products"][0]
    assert payload["id"] == product.id
    assert payload["name"] == product.name
    assert payload["is_active"] is True
    assert len(payload["prices"]) == 1
    assert payload["prices"][0]["id"] == product_price.id
    assert payload["prices"][0]["currency"] == "eur"
    assert payload["prices"][0]["price"] == "10.00"


@pytest.mark.django_db
def test_get_products_without_currency_returns_all_active_prices(
    client, product, product_price, product_price_repo
):
    rub_price = ProductPrice(
        currency=Currency.RUB, price=Decimal("5.00"), product=product
    )
    product_price_repo.save(rub_price)

    response = client.get(_url())

    assert response.status_code == 200
    data = response.json()
    assert {price["id"] for price in data["products"][0]["prices"]} == {
        product_price.id,
        rub_price.id,
    }


@pytest.mark.django_db
def test_get_products_returns_fallback_price_when_currency_not_found(
    client, product, product_price
):
    response = client.get(_url(currency="rub"))

    assert response.status_code == 200
    data = response.json()
    assert data["products"][0]["prices"][0]["id"] == product_price.id


@pytest.mark.django_db
def test_get_products_invalid_currency_returns_400(client):
    response = client.get(_url(currency="xyz"))

    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {"limit": "abc"},
        {"offset": "abc"},
        {"limit": "-1"},
        {"offset": "-5"},
    ],
)
def test_get_products_invalid_pagination_returns_400(client, params):
    path = reverse("product-list")
    query = "&".join(f"{key}={value}" for key, value in params.items())
    response = client.get(f"{path}?{query}")

    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.django_db
def test_get_products_applies_pagination(client, product, product_repo):
    for index in range(4):
        product_repo.save(Product(name=f"Product {index}", is_active=True))

    first_page = client.get(_url(limit=3, offset=0)).json()["products"]
    second_page = client.get(_url(limit=3, offset=3)).json()["products"]

    assert len(first_page) == 3
    assert len(second_page) == 2
    first_ids = {item["id"] for item in first_page}
    second_ids = {item["id"] for item in second_page}
    assert first_ids.isdisjoint(second_ids)
    assert product.id in first_ids | second_ids


@pytest.mark.django_db
def test_get_products_excludes_inactive_products(client, inactive_product):
    response = client.get(_url())

    assert response.status_code == 200
    assert response.json()["products"] == []


@pytest.mark.django_db
def test_get_products_empty_database_returns_empty_list(client):
    response = client.get(_url())

    assert response.status_code == 200
    assert response.json()["products"] == []
