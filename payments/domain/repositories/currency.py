from abc import ABC, abstractmethod

from payments.domain.entities.currency import Currencies, Currency


class CurrencyRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Currency: ...

    @abstractmethod
    async def get_active(self, limit: int = 10, offset: int = 0) -> list[Currency]: ...

    @abstractmethod
    async def get_active_by_code(self, currency: Currencies) -> Currency: ...

    @abstractmethod
    async def save(self, currency: Currency) -> None: ...
