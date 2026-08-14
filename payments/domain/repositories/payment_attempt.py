from abc import ABC, abstractmethod

from payments.domain.entities.payment_attempts import PaymentAttempt


class PaymentAttemptRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> PaymentAttempt: ...

    @abstractmethod
    def get_by_payment_id(
        self, payment_id: int, limit: int = 10, offset: int = 0
    ) -> list[PaymentAttempt]: ...

    @abstractmethod
    def get_by_order_id(self, order_id: int) -> list[PaymentAttempt]: ...

    @abstractmethod
    def get_by_id_for_update(self, id: int) -> PaymentAttempt: ...

    @abstractmethod
    def get_all_by_external_id(self, external_id: str) -> list[PaymentAttempt]: ...

    @abstractmethod
    def save(self, payment_attempt: PaymentAttempt) -> None: ...
