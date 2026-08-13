from decimal import Decimal
from enum import Enum

from payments.domain.exceptions import ExchangeRateValueError


class Currency(Enum):
    USD = "usd"
    RUB = "rub"
    EUR = "eur"
    JPY = "jpy"


class CurrencyMinorUnit:
    _multipliers = {
        Currency.USD: 100,
        Currency.EUR: 100,
        Currency.RUB: 100,
        Currency.JPY: 1,
    }

    @classmethod
    def get_multiplier(cls, currency: Currency) -> int:
        return cls._multipliers[currency]

    @classmethod
    def to_minor_units(
        cls,
        amount: Decimal | int | float,
        currency: Currency,
    ) -> int:
        return int(
            amount * cls.get_multiplier(currency)
        )


class ExchangeRate:
    _id: int | None
    _base_currency: Currency
    _currency: Currency
    _coef: Decimal
    _is_active: bool

    __slots__ = (
        "_base_currency",
        "_coef",
        "_currency",
        "_id",
        "_is_active",
    )

    def __init__(
        self,
        currency: Currency,
        coef: Decimal,
        is_active: bool = True,
        id: int | None = None,
    ):
        base_currency = Currency.USD

        if coef < 0:
            raise ExchangeRateValueError()

        if base_currency == currency and coef != 1:
            raise ExchangeRateValueError()

        object.__setattr__(self, "_id", id)
        object.__setattr__(self, "_base_currency", base_currency)
        object.__setattr__(self, "_currency", currency)
        object.__setattr__(self, "_coef", coef)
        object.__setattr__(self, "_is_active", is_active)

    def __setattr__(self, name, value):
        if name == "id":
            object.__setattr__(self, "_id", value)
        else:
            raise AttributeError(f"{type(self).__name__}.{name} is immutable")

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def base_currency(self) -> Currency:
        return self._base_currency

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def coef(self) -> Decimal:
        return self._coef

    @property
    def is_active(self) -> bool:
        return self._is_active

    def set_id(self, id: int) -> None:
        if self._id is not None:
            raise ValueError("ExchangeRate id is already set")

        object.__setattr__(self, "_id", id)

    def set_active(self, is_active: bool) -> None:
        object.__setattr__(self, "_is_active", is_active)

    @classmethod
    def restore(
        cls,
        currency: Currency,
        coef: Decimal,
        is_active: bool,
        id: int | None = None,
    ) -> ExchangeRate:
        return cls(
            currency=currency,
            coef=coef,
            is_active=is_active,
            id=id,
        )
