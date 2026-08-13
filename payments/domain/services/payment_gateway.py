from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.order import Order


@dataclass(frozen=True)
class PaymentResult:
    id: str
    client_secret: str
    status: str


class PaymentGateway(ABC):
    @abstractmethod
    def create_payment(
        self,
        order: Order,
        amount: Decimal,
        currency: Currency,
    ) -> PaymentResult: ...
