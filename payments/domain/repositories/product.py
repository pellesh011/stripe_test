from abc import ABC, abstractmethod

from payments.domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Product: ...

    @abstractmethod
    def get_active(self, limit: int = 10, offset: int = 0) -> list[Product]: ...

    @abstractmethod
    def save(self, product: Product) -> None: ...
