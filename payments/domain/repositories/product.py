from abc import ABC, abstractmethod

from payments.domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Product: ...

    @abstractmethod
    async def get_active(self, limit: int = 10, offset: int = 0) -> list[Product]: ...

    @abstractmethod
    async def save(self, product: Product) -> None: ...
