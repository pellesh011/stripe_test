from decimal import Decimal

import pytest

from payments.domain.entities.exchange_rate import Currencies, ExchangeRate
from payments.domain.exceptions import ExchangeRateValueError


def test_exchange_rate_create():
    test_exchange_rate = ExchangeRate(currency=Currencies.EUR, coef=Decimal(1.1))
    assert test_exchange_rate.currency.value == "eur"


def test_exchange_rate_create_wrong_coef_for_same_currency():
    with pytest.raises(ExchangeRateValueError):
        ExchangeRate(currency=Currencies.USD, coef=Decimal(1.1))


def test_exchange_rate_create_wrong_coef():
    with pytest.raises(ExchangeRateValueError):
        ExchangeRate(currency=Currencies.USD, coef=Decimal(-1.0))
