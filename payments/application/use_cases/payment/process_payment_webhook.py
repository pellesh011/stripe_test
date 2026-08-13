import logging

from payments.application.dto.payment_webhook import PaymentWebhookDTO
from payments.domain.entities.order import OrderStatus
from payments.domain.entities.payment import Payment, PaymentStatus
from payments.domain.entities.payment_attempts import (
    PaymentAttempt,
    PaymentAttemptStatus,
)
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.order import OrderRepository
from payments.domain.repositories.payment import PaymentRepository
from payments.domain.repositories.payment_attempt import PaymentAttemptRepository
from payments.domain.repositories.uow import UnitOfWork

logger = logging.getLogger(__name__)

SUPPORTED_EVENT_TYPES = frozenset(
    {
        "payment_intent.succeeded",
        "payment_intent.payment_failed",
        "payment_intent.canceled",
    }
)


class ProcessPaymentWebhookUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        payment_attempts: PaymentAttemptRepository,
        payments: PaymentRepository,
        orders: OrderRepository,
    ):
        self.uow = uow
        self.payment_attempts = payment_attempts
        self.payments = payments
        self.orders = orders

    def execute(self, data: PaymentWebhookDTO) -> None:
        if data.event_type not in SUPPORTED_EVENT_TYPES:
            logger.info(
                "Ignoring unsupported webhook event: event_id=%s",
                data.event_id,
            )
            return

        with self.uow:
            attempts = self.payment_attempts.get_all_by_external_id(
                data.payment_intent_id
            )
            if not attempts:
                raise EntityNotFoundError()

            if any(
                attempt.status
                in {PaymentAttemptStatus.SUCCEEDED, PaymentAttemptStatus.CANCELLED}
                for attempt in attempts
            ):
                logger.info(
                    "Payment already finished, ignoring webhook: "
                    "event_id=%s intent_id=%s",
                    data.event_id,
                    data.payment_intent_id,
                )
                return

            attempt = next(
                (
                    item
                    for item in attempts
                    if item.status
                    in {PaymentAttemptStatus.CREATED, PaymentAttemptStatus.PROCESSING}
                ),
                None,
            )

            if attempt is None:
                source = attempts[0]
                payment = source.payment
                if payment.status is PaymentStatus.FAILED:
                    payment.set_status(PaymentStatus.PENDING)
                attempt = PaymentAttempt(
                    provider=source.provider,
                    payment=payment,
                )
                attempt.external_id = data.payment_intent_id
                self.payment_attempts.save(attempt)

            payment = attempt.payment
            order = payment.order

            if data.event_type == "payment_intent.succeeded":
                attempt.mark_succeeded()
                self._pay(payment)
                order.status = OrderStatus.PAID
            elif data.event_type == "payment_intent.payment_failed":
                attempt.mark_failed()
                self._fail(payment)
            elif data.event_type == "payment_intent.canceled":
                attempt.mark_cancelled()
                self._cancel(payment)

            self.payment_attempts.save(attempt)
            self.payments.save(payment)
            self.orders.save(order)

        logger.info(
            "Processed Stripe webhook: event_id=%s event_type=%s intent_id=%s",
            data.event_id,
            data.event_type,
            data.payment_intent_id,
        )

    @staticmethod
    def _pay(payment: Payment) -> None:
        if payment.status is PaymentStatus.CREATED:
            payment.set_status(PaymentStatus.PENDING)
        payment.set_status(PaymentStatus.PAID)

    @staticmethod
    def _fail(payment: Payment) -> None:
        if payment.status is PaymentStatus.CREATED:
            payment.set_status(PaymentStatus.PENDING)
        payment.set_status(PaymentStatus.FAILED)

    @staticmethod
    def _cancel(payment: Payment) -> None:
        if payment.status in {PaymentStatus.CREATED, PaymentStatus.PENDING}:
            payment.set_status(PaymentStatus.CANCELLED)
