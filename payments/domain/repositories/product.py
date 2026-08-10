from abc import ABC, abstractmethod

from payments.domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Product:
        ...

    @abstractmethod
    async def save(self, order: Product) -> None:
        ...