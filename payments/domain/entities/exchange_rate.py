from decimal import Decimal
from enum import Enum

from payments.domain.exceptions import ExchangeRateValueError


class Currencies(Enum):
    USD = "usd"
    RUB = "rub"
    EUR = "eur"


class ExchangeRate:
    id: int | None
    base_currency: Currencies
    currency: Currencies
    coef: Decimal
    is_active: bool

    def __init__(
        self,
        currency: Currencies,
        coef: Decimal,
        is_active: bool = True,
        id: int | None = None,
    ):

        self.base_currency = Currencies.USD
        self.currency = currency
        self.coef = coef
        self.is_active = is_active
        self.id = id
        if self.coef < 0:
            raise ExchangeRateValueError()

        if self.base_currency == self.currency and self.coef != 1:
            raise ExchangeRateValueError()

    @classmethod
    def restore(
        cls,
        currency: Currencies,
        coef: Decimal,
        is_active: bool,
        id: int | None = None,
    ) -> ExchangeRate:
        return cls(currency=currency, coef=coef, is_active=is_active, id=id)
