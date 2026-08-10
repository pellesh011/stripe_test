from abc import ABC, abstractmethod

from payments.domain.entities.product_price import ProductPrice


class ProductPriceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> ProductPrice: ...

    @abstractmethod
    async def get_active(self) -> list[ProductPrice]: ...

    @abstractmethod
    async def get_active_by_product_id(self, product_id: int) -> ProductPrice: ...

    @abstractmethod
    async def save(self, product_price: ProductPrice) -> None: ...
