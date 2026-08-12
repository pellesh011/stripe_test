from abc import ABC, abstractmethod

from payments.domain.entities.discount import Discount


class DiscountRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Discount: ...

    @abstractmethod
    async def get_active(self, limit: int = 10, offset: int = 0) -> list[Discount]: ...

    @abstractmethod
    async def save(self, discount: Discount) -> None: ...
