from abc import ABC, abstractmethod

from payments.domain.entities.discount import Discount


class DiscountRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Discount: ...

    @abstractmethod
    def get_active(self, limit: int = 10, offset: int = 0) -> list[Discount]: ...

    @abstractmethod
    def save(self, discount: Discount) -> None: ...
