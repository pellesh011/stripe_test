from decimal import Decimal

import pytest

from payments.domain.entities.currency import Currencies, Currency
from payments.domain.exceptions import CurrencyValueError


def test_currency_create():
    test_currency = Currency(currency=Currencies.EUR, coef=Decimal(1.1))
    assert test_currency.currency.value == "eur"


def test_currency_create_wrong_coef_for_same_currency():
    with pytest.raises(CurrencyValueError):
        Currency(currency=Currencies.USD, coef=Decimal(1.1))


def test_currency_create_wrong_coef():
    with pytest.raises(CurrencyValueError):
        Currency(currency=Currencies.USD, coef=Decimal(-1.0))
