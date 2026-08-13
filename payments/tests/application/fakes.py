from decimal import Decimal

from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.order import Order
from payments.domain.services.payment_gateway import PaymentGateway, PaymentResult

CLIENT_SECRET = "cs_test_secret"
PAYMENT_INTENT_ID = "pi_test_123"
PAYMENT_STATUS = "requires_payment_method"


class FakePaymentGateway(PaymentGateway):
    def __init__(self) -> None:
        self.calls: list[tuple[Order, Decimal, Currency]] = []

    def create_payment(
        self,
        order: Order,
        amount: Decimal,
        currency: Currency,
    ) -> PaymentResult:
        self.calls.append((order, amount, currency))
        return PaymentResult(
            id=PAYMENT_INTENT_ID,
            client_secret=CLIENT_SECRET,
            status=PAYMENT_STATUS,
        )
