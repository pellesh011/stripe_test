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
    assert loaded.base_currency == Currency.EUR
    assert loaded.coef == Decimal("1")
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
def test_get_active_pagination_limit_and_offset(exchange_rate_repo, exchange_rate):
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
    loaded = exchange_rate_repo.get_all_active_by_code(Currency.EUR)
    assert [item.currency for item in loaded] == [Currency.EUR]
    assert all(item.is_active for item in loaded)


@pytest.mark.django_db
def test_get_active_by_code_filters_by_base_currency(exchange_rate_repo, exchange_rate):
    other = ExchangeRate(
        base_currency=Currency.USD,
        currency=Currency.RUB,
        coef=Decimal("0.012"),
    )
    exchange_rate_repo.save(other)

    loaded = exchange_rate_repo.get_all_active_by_code(Currency.EUR)

    assert [item.currency for item in loaded] == [Currency.EUR]


@pytest.mark.django_db
def test_get_active_by_code_returns_empty_when_none(exchange_rate_repo, exchange_rate):
    loaded = exchange_rate_repo.get_all_active_by_code(Currency.RUB)

    assert loaded == []


@pytest.mark.django_db
def test_get_active_by_code_ignores_inactive(exchange_rate_repo, exchange_rate):
    inactive = ExchangeRate(
        base_currency=Currency.EUR,
        currency=Currency.RUB,
        coef=Decimal("0.012"),
        is_active=False,
    )
    exchange_rate_repo.save(inactive)

    loaded = exchange_rate_repo.get_all_active_by_code(Currency.EUR)

    assert [item.currency for item in loaded] == [Currency.EUR]


@pytest.mark.django_db
def test_save_create_assigns_id(exchange_rate_repo):
    entity = ExchangeRate(currency=Currency.RUB, coef=Decimal("0.012"))
    assert entity.id is None

    exchange_rate_repo.save(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_save_update(exchange_rate_repo, exchange_rate):
    assert exchange_rate.id is not None
    with pytest.raises(AttributeError):
        exchange_rate.coef = Decimal("1.20")
    exchange_rate.set_active(False)
    exchange_rate_repo.save(exchange_rate)

    loaded = exchange_rate_repo.get_by_id(exchange_rate.id)
    assert loaded.is_active is False
