from decimal import Decimal

import pytest

from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id(exchange_rate_repo, exchange_rate):
    assert exchange_rate.id is not None
    loaded = exchange_rate_repo.get_by_id(exchange_rate.id)
    assert loaded.id == exchange_rate.id
    assert loaded.currency == Currency.EUR
    assert loaded.coef == Decimal("1.10")
    assert loaded.is_active is True


@pytest.mark.django_db
def test_get_by_id_not_found(exchange_rate_repo):
    with pytest.raises(EntityNotFoundError):
        exchange_rate_repo.get_by_id(9999)


@pytest.mark.django_db
def test_get_active(exchange_rate_repo, exchange_rate):
    inactive = ExchangeRate(
        currency=Currency.RUB,
        coef=Decimal("0.012"),
        is_active=False,
    )
    exchange_rate_repo.save(inactive)

    active = exchange_rate_repo.get_active()
    active_codes = {item.currency for item in active}

    assert Currency.EUR in active_codes
    assert Currency.RUB not in active_codes


@pytest.mark.django_db
def test_get_active_pagination_limit_and_offset(
    exchange_rate_repo, exchange_rate
):
    for enum in (Currency.RUB, Currency.USD):
        entity = ExchangeRate(currency=enum, coef=Decimal("1.00"))
        exchange_rate_repo.save(entity)

    first_page = exchange_rate_repo.get_active(limit=2, offset=0)
    second_page = exchange_rate_repo.get_active(limit=2, offset=2)

    assert len(first_page) == 2
    assert len(second_page) == 1

    first_ids = {item.id for item in first_page}
    second_ids = {item.id for item in second_page}
    assert first_ids.isdisjoint(second_ids)
    assert exchange_rate.id in first_ids | second_ids


@pytest.mark.django_db
def test_get_active_by_code(exchange_rate_repo, exchange_rate):
    loaded = exchange_rate_repo.get_active_by_code(Currency.EUR)
    assert loaded.currency == Currency.EUR
    assert loaded.is_active is True


@pytest.mark.django_db
def test_get_active_by_code_not_found(exchange_rate_repo, exchange_rate):
    inactive = ExchangeRate(
        currency=Currency.RUB,
        coef=Decimal("0.012"),
        is_active=False,
    )
    exchange_rate_repo.save(inactive)

    with pytest.raises(EntityNotFoundError):
        exchange_rate_repo.get_active_by_code(Currency.RUB)


@pytest.mark.django_db
def test_save_create_assigns_id(exchange_rate_repo):
    entity = ExchangeRate(currency=Currency.RUB, coef=Decimal("0.012"))
    assert entity.id is None

    exchange_rate_repo.save(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_save_update(exchange_rate_repo, exchange_rate):
    assert exchange_rate.id is not None
    exchange_rate.coef = Decimal("1.20")

    exchange_rate_repo.save(exchange_rate)

    loaded = exchange_rate_repo.get_by_id(exchange_rate.id)
    assert loaded.coef == Decimal("1.20")
