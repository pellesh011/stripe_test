from abc import ABC, abstractmethod

from payments.domain.entities.order import Order


class OrderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Order: ...

    @abstractmethod
    async def save(self, order: Order) -> None: ...
