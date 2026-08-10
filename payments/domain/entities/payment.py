from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from payments.domain.entities.currency import Currencies, Currency
from payments.domain.entities.order import Order
from payments.domain.exceptions import InvalidPaymentStatusTransition

class PaymentStatus(Enum):
    CREATED = "created"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

@dataclass
class Payment:
    id: int | None
    order: Order
    user: None
    amount: Decimal
    currency: Currency
    status: PaymentStatus

    def __init__(self, order: Order, amount: Decimal, currency: Currency, user = None, id: int|None = None):
        self.order = order
        self.amount = amount
        self.currency = currency
        self.user = user
        self.status = PaymentStatus.CREATED
        self.id = id

    def set_status(self, status: PaymentStatus):
        available_transitions = {
            PaymentStatus.CREATED: [
                PaymentStatus.PENDING,
                PaymentStatus.CANCELLED,
            ],
            PaymentStatus.PENDING: [
                PaymentStatus.PAID,
                PaymentStatus.FAILED,
                PaymentStatus.CANCELLED,
            ],
            PaymentStatus.PAID: [
                PaymentStatus.REFUNDED,
            ],
            PaymentStatus.FAILED: [
                PaymentStatus.PENDING,
            ],
            PaymentStatus.CANCELLED: [],
            PaymentStatus.REFUNDED: [],
        }

        available = available_transitions.get(self.status, [])

        if status not in available:
            raise InvalidPaymentStatusTransition()
        self.status = status

    @classmethod
    def restore(cls,id: int, order: Order, amount: Decimal, currency: Currency, user = None) -> Payment:
        return cls( id=id, order=order, amount=amount,currency=currency, user=user)