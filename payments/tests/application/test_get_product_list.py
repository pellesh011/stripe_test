from decimal import Decimal

import pytest

from payments.application.dto.product import GetProductListDTO, PaginationDTO
from payments.application.use_cases.product.get_product_list import (
    GetProductListUseCase,
)
from payments.domain.entities.currency import Currencies, Currency
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


def _build_use_case(products, product_prices):
    return GetProductListUseCase(products=products, product_prices=product_prices)


def _build_dto(currency: str | None, limit: int = 10, offset: int = 0):
    return GetProductListDTO(
        pagination=PaginationDTO(limit=limit, offset=offset),
        is_active=True,
        currency=currency,
    )


@pytest.mark.django_db
def test_execute_attaches_active_prices_in_currency(
    product_repo,
    product_price_repo,
    currency_repo,
    product,
    product_price,
    call,
):
    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency="eur")

    result = call(use_case.execute)(dto)

    assert len(result) == 1
    assert result[0].id == product.id
    assert len(result[0].prices) == 1
    assert result[0].prices[0].id == product_price.id
    assert result[0].prices[0].currency.currency == Currencies.EUR


@pytest.mark.django_db
def test_execute_filters_prices_by_currency(
    product_repo,
    product_price_repo,
    currency_repo,
    product,
    product_price,
    call,
):
    rub = Currency(currency=Currencies.RUB, coef=Decimal("1.00"))
    call(currency_repo.save)(rub)
    rub_price = ProductPrice(currency=rub, price=Decimal("5.00"), product=product)
    call(product_price_repo.save)(rub_price)

    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency="rub")

    result = call(use_case.execute)(dto)

    assert len(result) == 1
    assert len(result[0].prices) == 1
    assert result[0].prices[0].id == rub_price.id


@pytest.mark.django_db
def test_execute_currency_none_returns_all_active_prices(
    product_repo,
    product_price_repo,
    currency_repo,
    product,
    product_price,
    call,
):
    rub = Currency(currency=Currencies.RUB, coef=Decimal("1.00"))
    call(currency_repo.save)(rub)
    rub_price = ProductPrice(currency=rub, price=Decimal("5.00"), product=product)
    call(product_price_repo.save)(rub_price)

    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency=None)

    result = call(use_case.execute)(dto)

    assert len(result) == 1
    assert {price.id for price in result[0].prices} == {
        product_price.id,
        rub_price.id,
    }


@pytest.mark.django_db
def test_execute_excludes_inactive_prices(
    product_repo,
    product_price_repo,
    currency_repo,
    product,
    product_price,
    call,
):
    rub = Currency(currency=Currencies.RUB, coef=Decimal("1.00"))
    call(currency_repo.save)(rub)
    inactive_price = ProductPrice(currency=rub, price=Decimal("5.00"), product=product)
    inactive_price.set_active(False)
    call(product_price_repo.save)(inactive_price)

    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency=None)

    result = call(use_case.execute)(dto)

    assert len(result) == 1
    assert [price.id for price in result[0].prices] == [product_price.id]


@pytest.mark.django_db
def test_execute_product_without_price_in_requested_currency_has_no_prices(
    product_repo,
    product_price_repo,
    product,
    product_price,
    call,
):
    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency="rub")

    result = call(use_case.execute)(dto)

    assert len(result) == 1
    assert result[0].id == product.id
    assert result[0].prices == []


@pytest.mark.django_db
def test_execute_product_without_any_prices_has_empty_list(
    product_repo,
    product_price_repo,
    product,
    call,
):
    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency=None)

    result = call(use_case.execute)(dto)

    assert len(result) == 1
    assert result[0].id == product.id
    assert result[0].prices == []


@pytest.mark.django_db
def test_execute_applies_pagination_to_products(
    product_repo,
    product_price_repo,
    product,
    call,
):
    for index in range(4):
        entity = Product(name=f"Product {index}", is_active=True)
        call(product_repo.save)(entity)

    use_case = _build_use_case(product_repo, product_price_repo)
    first_page = call(use_case.execute)(_build_dto(currency=None, limit=3, offset=0))
    second_page = call(use_case.execute)(_build_dto(currency=None, limit=3, offset=3))

    assert len(first_page) == 3
    assert len(second_page) == 2

    first_ids = {item.id for item in first_page}
    second_ids = {item.id for item in second_page}
    assert first_ids.isdisjoint(second_ids)
    assert product.id in first_ids | second_ids


@pytest.mark.django_db
def test_execute_invalid_currency_raises_value_error(
    product_repo,
    product_price_repo,
    product,
    call,
):
    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency="xyz")

    with pytest.raises(ValueError):
        call(use_case.execute)(dto)
