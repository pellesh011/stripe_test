from abc import ABC, abstractmethod

from payments.domain.entities.order_item import OrderItem


class OrderItemRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> OrderItem: ...

    @abstractmethod
    def get_by_order_id(
        self, order_id: int, limit: int = 10, offset: int = 0
    ) -> list[OrderItem]: ...

    @abstractmethod
    def save(self, order_item: OrderItem) -> None: ...

    @abstractmethod
    def delete(self, order_item: OrderItem) -> None: ...
