from abc import ABC, abstractmethod

from payments.domain.entities.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Order: ...

    @abstractmethod
    def get_all(self) -> list[Order]: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...
