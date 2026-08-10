from decimal import Decimal
from enum import Enum

from payments.domain.exceptions import CurrencyValueError


class Currencies(Enum):
    USD = "usd"
    RUB = "rub"
    EUR = "eur"


class Currency:
    base_currency: Currencies
    currency: Currencies
    coef: Decimal
    is_active: bool

    def __init__(self, currency: Currencies, coef: Decimal, is_active: bool = True):

        self.base_currency = Currencies.USD
        self.currency = currency
        self.coef = coef
        self.is_active = is_active
        if self.coef < 0:
            raise CurrencyValueError()

        if self.base_currency == self.currency and self.coef != 1:
            raise CurrencyValueError()
