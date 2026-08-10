from decimal import Decimal

import pytest

from payments.domain.entities.currency import Currencies, Currency
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id(currency_repo, currency, call):
    assert currency.id is not None
    loaded = call(currency_repo.get_by_id)(currency.id)
    assert loaded.id == currency.id
    assert loaded.currency == Currencies.EUR
    assert loaded.coef == Decimal("1.10")
    assert loaded.is_active is True


@pytest.mark.django_db
def test_get_by_id_not_found(currency_repo, call):
    with pytest.raises(EntityNotFoundError):
        call(currency_repo.get_by_id)(9999)


@pytest.mark.django_db
def test_get_active(currency_repo, currency, call):
    inactive = Currency(
        currency=Currencies.RUB,
        coef=Decimal("0.012"),
        is_active=False,
    )
    call(currency_repo.save)(inactive)

    active = call(currency_repo.get_active)()
    active_codes = {item.currency for item in active}

    assert Currencies.EUR in active_codes
    assert Currencies.RUB not in active_codes


@pytest.mark.django_db
def test_get_active_by_code(currency_repo, currency, call):
    loaded = call(currency_repo.get_active_by_code)(Currencies.EUR)
    assert loaded.currency == Currencies.EUR
    assert loaded.is_active is True


@pytest.mark.django_db
def test_get_active_by_code_not_found(currency_repo, currency, call):
    inactive = Currency(
        currency=Currencies.RUB,
        coef=Decimal("0.012"),
        is_active=False,
    )
    call(currency_repo.save)(inactive)

    with pytest.raises(EntityNotFoundError):
        call(currency_repo.get_active_by_code)(Currencies.RUB)


@pytest.mark.django_db
def test_save_create_assigns_id(currency_repo, call):
    entity = Currency(currency=Currencies.RUB, coef=Decimal("0.012"))
    assert entity.id is None

    call(currency_repo.save)(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_save_update(currency_repo, currency, call):
    assert currency.id is not None
    currency.coef = Decimal("1.20")

    call(currency_repo.save)(currency)

    loaded = call(currency_repo.get_by_id)(currency.id)
    assert loaded.coef == Decimal("1.20")
