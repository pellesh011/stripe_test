from decimal import Decimal

import stripe

from payments.domain.entities.exchange_rate import (
    Currency,
    CurrencyMinorUnit,
)
from payments.domain.entities.order import Order
from payments.domain.exceptions import PaymentClientSecretMissingError
from payments.domain.services.payment_gateway import PaymentGateway, PaymentResult


class StripePaymentGateway(PaymentGateway):
    def __init__(self, api_key: str) -> None:
        stripe.api_key = api_key

    def create_payment(
        self,
        order: Order,
        amount: Decimal,
        currency: Currency,
    ) -> PaymentResult:
        metadata = {
            "order_id": str(order.id),
        }
        if order.discount is not None:
            metadata["discount_id"] = str(order.discount.id)
        if order.tax is not None:
            metadata["tax_id"] = str(order.tax.id)

        intent =  stripe.PaymentIntent.create(
            amount=CurrencyMinorUnit.to_minor_units(amount, currency),
            currency=currency.value,
            metadata=metadata,
        )
        if intent.client_secret is None:
            raise PaymentClientSecretMissingError(
                f"PaymentIntent {intent.id} has no client_secret"
            )
        return PaymentResult(
            id=intent.id,
            client_secret=intent.client_secret,
            status=intent.status,
        )
