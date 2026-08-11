from abc import ABC, abstractmethod
from types import TracebackType

from payments.domain.repositories.order import OrderRepository
from payments.domain.repositories.order_item import OrderItemRepository
from payments.domain.repositories.payment import PaymentRepository
from payments.domain.repositories.payment_attempt import PaymentAttemptRepository


class UnitOfWork(ABC):
    orders: OrderRepository
    order_items: OrderItemRepository
    payments: PaymentRepository
    payment_attempts: PaymentAttemptRepository

    @abstractmethod
    def __enter__(self) -> UnitOfWork: ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
