from decimal import Decimal

import pytest

from payments.domain.entities.exchange_rate import Currencies
from payments.domain.entities.product_price import ProductPrice
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id(product_price_repo, product_price, call):
    assert product_price.id is not None
    loaded = call(product_price_repo.get_by_id)(product_price.id)
    assert loaded.id == product_price.id
    assert loaded.price == Decimal("10.00")
    assert loaded.product.id == product_price.product.id
    assert loaded.currency == Currencies.EUR
    assert loaded.is_active is True


@pytest.mark.django_db
def test_get_by_id_not_found(product_price_repo, call):
    with pytest.raises(EntityNotFoundError):
        call(product_price_repo.get_by_id)(9999)


@pytest.mark.django_db
def test_get_active(product_price_repo, product_price, product, call):
    inactive = ProductPrice(
        currency=Currencies.EUR, price=Decimal("5.00"), product=product
    )
    inactive.set_active(False)
    call(product_price_repo.save)(inactive)

    active = call(product_price_repo.get_active)()
    active_ids = {item.id for item in active}

    assert product_price.id in active_ids
    assert inactive.id not in active_ids


@pytest.mark.django_db
def test_get_active_pagination_limit_and_offset(
    product_price_repo,
    product,
    product_price,
    call,
):
    for enum in (Currencies.RUB, Currencies.USD):
        entity = ProductPrice(currency=enum, price=Decimal("5.00"), product=product)
        call(product_price_repo.save)(entity)

    first_page = call(product_price_repo.get_active)(limit=2, offset=0)
    second_page = call(product_price_repo.get_active)(limit=2, offset=2)

    assert len(first_page) == 2
    assert len(second_page) == 1

    first_ids = {item.id for item in first_page}
    second_ids = {item.id for item in second_page}
    assert first_ids.isdisjoint(second_ids)
    assert product_price.id in first_ids | second_ids


@pytest.mark.django_db
def test_get_active_by_product_id(product_price_repo, product_price, call):
    assert product_price.product.id is not None
    loaded = call(product_price_repo.get_active_by_product_id)(product_price.product.id)
    assert loaded.id == product_price.id


@pytest.mark.django_db
def test_get_active_by_product_id_not_found(
    product_price_repo,
    inactive_product,
    call,
):
    assert inactive_product.id is not None
    with pytest.raises(EntityNotFoundError):
        call(product_price_repo.get_active_by_product_id)(inactive_product.id)


@pytest.mark.django_db
def test_get_active_by_product_ids_filters_by_currency(
    product_price_repo,
    product,
    product_price,
    call,
):
    assert product.id is not None
    rub_price = ProductPrice(
        currency=Currencies.RUB, price=Decimal("5.00"), product=product
    )
    call(product_price_repo.save)(rub_price)

    prices = call(product_price_repo.get_active_by_product_ids)(
        [product.id],
        currency=Currencies.RUB,
    )

    assert [price.id for price in prices] == [rub_price.id]


@pytest.mark.django_db
def test_get_active_by_product_ids_returns_active_only(
    product_price_repo,
    product,
    product_price,
    call,
):
    assert product.id is not None
    inactive = ProductPrice(
        currency=Currencies.RUB, price=Decimal("5.00"), product=product
    )
    inactive.set_active(False)
    call(product_price_repo.save)(inactive)

    prices = call(product_price_repo.get_active_by_product_ids)([product.id])

    assert [price.id for price in prices] == [product_price.id]


@pytest.mark.django_db
def test_get_active_by_product_ids_multiple_products(
    product_price_repo,
    product,
    product_price,
    call,
):
    second_price = ProductPrice(
        currency=Currencies.RUB, price=Decimal("7.00"), product=product
    )
    call(product_price_repo.save)(second_price)

    assert product.id is not None
    prices = call(product_price_repo.get_active_by_product_ids)([product.id])

    assert {price.id for price in prices} == {product_price.id, second_price.id}


@pytest.mark.django_db
def test_save_create_assigns_id(product_price_repo, product, call):
    entity = ProductPrice(
        currency=Currencies.EUR, price=Decimal("3.99"), product=product
    )
    assert entity.id is None

    call(product_price_repo.save)(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_save_update(product_price_repo, product_price, call):
    assert product_price.id is not None
    product_price.price = Decimal("12.50")
    product_price.set_active(False)

    call(product_price_repo.save)(product_price)

    loaded = call(product_price_repo.get_by_id)(product_price.id)
    assert loaded.price == Decimal("12.50")
    assert loaded.is_active is False
