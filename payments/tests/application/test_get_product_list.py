from decimal import Decimal

import pytest

from payments.application.dto.product import GetProductListDTO, PaginationDTO
from payments.application.use_cases.product.get_product_list import (
    GetProductListUseCase,
)
from payments.domain.entities.currency import Currencies, Currency
from payments.domain.entities.product_price import ProductPrice
from payments.infrastructure.database.uow import DjangoUnitOfWork


def _build_use_case(products, product_prices):
    return GetProductListUseCase(
        products=products,
        product_prices=product_prices,
        uow=DjangoUnitOfWork(products),
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
    dto = GetProductListDTO(
        pagination=PaginationDTO(),
        is_active=True,
        currency="eur",
    )

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
    dto = GetProductListDTO(
        pagination=PaginationDTO(),
        is_active=True,
        currency="rub",
    )

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
    dto = GetProductListDTO(
        pagination=PaginationDTO(),
        is_active=True,
        currency=None,
    )

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
    dto = GetProductListDTO(
        pagination=PaginationDTO(),
        is_active=True,
        currency=None,
    )

    result = call(use_case.execute)(dto)

    assert len(result) == 1
    assert [price.id for price in result[0].prices] == [product_price.id]
