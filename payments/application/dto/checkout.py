from dataclasses import dataclass
from decimal import Decimal

from payments.domain.entities.exchange_rate import Currency


@dataclass(frozen=True)
class CheckoutDTO:
    cart_id: int
    currency: str
    provider_id: int | None = None
    discount: str | None = None


@dataclass(frozen=True)
class CheckoutResult:
    order_id: int
    amount: Decimal
    currency: Currency
    client_secret: str
