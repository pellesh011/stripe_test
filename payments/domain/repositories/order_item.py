from abc import ABC, abstractmethod

from payments.domain.entities.order_item import OrderItem


class OrderItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> OrderItem: ...

    @abstractmethod
    async def get_by_order_id(
        self, order_id: int, limit: int = 10, offset: int = 0
    ) -> list[OrderItem]: ...

    @abstractmethod
    async def save(self, order_item: OrderItem) -> None: ...
