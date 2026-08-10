from abc import ABC, abstractmethod

from payments.domain.entities.payment_attempts import PaymentAttempt


class PaymentAttemptRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> PaymentAttempt: ...

    @abstractmethod
    async def get_by_payment_id(self, payment_id: int) -> list[PaymentAttempt]: ...

    @abstractmethod
    async def save(self, payment_attempt: PaymentAttempt) -> None: ...
