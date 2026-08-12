from abc import ABC, abstractmethod

from payments.domain.entities.tax import Tax


class TaxRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Tax: ...

    @abstractmethod
    async def save(self, tax: Tax) -> None: ...
