from abc import ABC, abstractmethod

from payments.domain.entities.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Order: ...

    @abstractmethod
    def get_all(self, limit: int = 10, offset: int = 0) -> list[Order]: ...

    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...
