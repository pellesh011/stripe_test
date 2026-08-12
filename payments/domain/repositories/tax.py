from abc import ABC, abstractmethod

from payments.domain.entities.tax import Tax


class TaxRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Tax: ...

    @abstractmethod
    def save(self, tax: Tax) -> None: ...
