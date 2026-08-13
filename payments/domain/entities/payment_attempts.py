from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from payments.domain.entities.payment import Payment
from payments.domain.entities.payment_provider import PaymentProvider
from payments.domain.exceptions import IdentificatorError


class PaymentAttemptStatus(Enum):
    CREATED = "created"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PaymentAttempt:
    id: int | None
    external_id: str | None
    provider: PaymentProvider
    payment: Payment
    status: PaymentAttemptStatus
    created_at: datetime
    completed_at: datetime | None

    def __init__(
        self,
        provider: PaymentProvider,
        payment: Payment,
        *,
        status: PaymentAttemptStatus = PaymentAttemptStatus.CREATED,
    ):
        self.id = None
        self.external_id = None
        self.provider = provider
        self.payment = payment
        self.status = status
        self.created_at = datetime.now(UTC)
        self.completed_at = None

    @classmethod
    def restore(
        cls,
        id: int,
        external_id: str | None,
        provider: PaymentProvider,
        payment: Payment,
        status: PaymentAttemptStatus,
        created_at: datetime,
        completed_at: datetime | None,
    ) -> PaymentAttempt:
        attempt = cls(
            provider=provider,
            payment=payment,
            status=status,
        )

        attempt.id = id
        attempt.external_id = external_id
        attempt.created_at = created_at
        attempt.completed_at = completed_at

        return attempt

    def _set_status(self, status: PaymentAttemptStatus) -> None:
        self.status = status

        if status in {
            PaymentAttemptStatus.SUCCEEDED,
            PaymentAttemptStatus.FAILED,
            PaymentAttemptStatus.CANCELLED,
        }:
            self.completed_at = datetime.now(UTC)

    def mark_processing(self) -> None:
        self._set_status(PaymentAttemptStatus.PROCESSING)

    def mark_succeeded(self) -> None:
        self._set_status(PaymentAttemptStatus.SUCCEEDED)

    def mark_failed(self) -> None:
        self._set_status(PaymentAttemptStatus.FAILED)

    def mark_cancelled(self) -> None:
        self._set_status(PaymentAttemptStatus.CANCELLED)

    def get_id(self) -> int:
        if self.id is None:
            raise IdentificatorError()
        return self.id
