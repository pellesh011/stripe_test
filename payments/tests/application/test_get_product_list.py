from decimal import Decimal

import pytest

from payments.application.dto.product import GetProductListDTO, PaginationDTO
from payments.application.use_cases.product.get_product_list import (
    GetProductListUseCase,
)
from payments.domain.entities.exchange_rate import Currency
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
    product,
    product_price,
):
    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency="eur")

    result = use_case.execute(dto)

    assert len(result) == 1
    assert result[0].id == product.id
    assert len(result[0].prices) == 1
    assert result[0].prices[0].id == product_price.id
    assert result[0].prices[0].currency == Currency.EUR


@pytest.mark.django_db
def test_execute_filters_prices_by_currency(
    product_repo,
    product_price_repo,
    product,
    product_price,
):
    rub_price = ProductPrice(
        currency=Currency.RUB, price=Decimal("5.00"), product=product
    )
    product_price_repo.save(rub_price)

    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency="rub")

    result = use_case.execute(dto)

    assert len(result) == 1
    assert len(result[0].prices) == 1
    assert result[0].prices[0].id == rub_price.id


@pytest.mark.django_db
def test_execute_currency_none_returns_all_active_prices(
    product_repo,
    product_price_repo,
    product,
    product_price,
):
    rub_price = ProductPrice(
        currency=Currency.RUB, price=Decimal("5.00"), product=product
    )
    product_price_repo.save(rub_price)

    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency=None)

    result = use_case.execute(dto)

    assert len(result) == 1
    assert {price.id for price in result[0].prices} == {
        product_price.id,
        rub_price.id,
    }


@pytest.mark.django_db
def test_execute_excludes_inactive_prices(
    product_repo,
    product_price_repo,
    product,
    product_price,
):
    inactive_price = ProductPrice(
        currency=Currency.RUB, price=Decimal("5.00"), product=product
    )
    inactive_price.set_active(False)
    product_price_repo.save(inactive_price)

    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency=None)

    result = use_case.execute(dto)

    assert len(result) == 1
    assert [price.id for price in result[0].prices] == [product_price.id]


@pytest.mark.django_db
def test_execute_product_without_price_in_requested_currency_has_no_prices(
    product_repo,
    product_price_repo,
    product,
    product_price,
):
    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency="rub")

    result = use_case.execute(dto)

    assert len(result) == 1
    assert result[0].id == product.id
    assert result[0].prices == []


@pytest.mark.django_db
def test_execute_product_without_any_prices_has_empty_list(
    product_repo,
    product_price_repo,
    product,
):
    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency=None)

    result = use_case.execute(dto)

    assert len(result) == 1
    assert result[0].id == product.id
    assert result[0].prices == []


@pytest.mark.django_db
def test_execute_applies_pagination_to_products(
    product_repo,
    product_price_repo,
    product,
):
    for index in range(4):
        entity = Product(name=f"Product {index}", is_active=True)
        product_repo.save(entity)

    use_case = _build_use_case(product_repo, product_price_repo)
    first_page = use_case.execute(_build_dto(currency=None, limit=3, offset=0))
    second_page = use_case.execute(_build_dto(currency=None, limit=3, offset=3))

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
):
    use_case = _build_use_case(product_repo, product_price_repo)
    dto = _build_dto(currency="xyz")

    with pytest.raises(ValueError):
        use_case.execute(dto)
