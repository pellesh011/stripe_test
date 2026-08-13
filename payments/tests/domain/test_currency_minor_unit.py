from decimal import Decimal

from payments.domain.entities.exchange_rate import Currency, CurrencyMinorUnit


def test_get_multiplier():
    assert CurrencyMinorUnit.get_multiplier(Currency.USD) == 100
    assert CurrencyMinorUnit.get_multiplier(Currency.EUR) == 100
    assert CurrencyMinorUnit.get_multiplier(Currency.RUB) == 100
    assert CurrencyMinorUnit.get_multiplier(Currency.JPY) == 1


def test_to_minor_units_with_float():
    assert CurrencyMinorUnit.to_minor_units(10.50, Currency.USD) == 1050


def test_to_minor_units_with_decimal():
    assert CurrencyMinorUnit.to_minor_units(Decimal("10.50"), Currency.EUR) == 1050


def test_to_minor_units_with_jpy():
    assert CurrencyMinorUnit.to_minor_units(100, Currency.JPY) == 100
