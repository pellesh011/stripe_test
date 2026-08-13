import logging
from decimal import Decimal

import stripe

from payments.domain.entities.exchange_rate import (
    Currency,
    CurrencyMinorUnit,
)
from payments.domain.entities.order import Order
from payments.domain.exceptions import (
    PaymentAmountTooSmallError,
    PaymentClientSecretMissingError,
)
from payments.domain.services.payment_gateway import PaymentGateway, PaymentResult

logger = logging.getLogger(__name__)


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

        converted_amount = CurrencyMinorUnit.to_minor_units(amount, currency)
        try:
            intent = stripe.PaymentIntent.create(
                amount=converted_amount,
                currency=currency.value,
                metadata=metadata,
            )
        except stripe.InvalidRequestError as exc:
            if exc.param == "amount":
                logger.error(
                    "Amount is too small for payment: "
                    "order_id=%s amount=%s currency=%s error=%s converted_amount=%s",
                    order.id,
                    amount,
                    currency.value,
                    exc,
                    converted_amount,
                )
                raise PaymentAmountTooSmallError(str(exc)) from exc
            logger.exception(
                "Stripe InvalidRequestError while creating PaymentIntent: "
                "order_id=%s amount=%s currency=%s",
                order.id,
                amount,
                currency.value,
            )
            raise
        logger.info(
            "PaymentIntent created: order_id=%s intent_id=%s status=%s",
            order.id,
            intent.id,
            intent.status,
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
