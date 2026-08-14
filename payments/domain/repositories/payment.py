from abc import ABC, abstractmethod

from payments.domain.entities.payment import Payment


class PaymentRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Payment: ...

    @abstractmethod
    def get_by_order_id(self, order_id: int) -> Payment: ...

    @abstractmethod
    def save(self, payment: Payment) -> None: ...

    @abstractmethod
    def delete(self, payment: Payment) -> None: ...
