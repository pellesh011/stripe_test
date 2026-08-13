from abc import ABC, abstractmethod

from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.product_price import ProductPrice


class ProductPriceRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> ProductPrice: ...

    @abstractmethod
    def get_active(self, limit: int = 10, offset: int = 0) -> list[ProductPrice]: ...

    @abstractmethod
    def get_active_by_product_id(self, product_id: int) -> ProductPrice: ...

    @abstractmethod
    def get_active_by_product_ids(
        self,
        product_ids: list[int],
        currency: Currency | None = None,
    ) -> list[ProductPrice]: ...

    @abstractmethod
    def save(self, product_price: ProductPrice) -> None: ...
