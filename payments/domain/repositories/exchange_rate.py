from abc import ABC, abstractmethod

from payments.domain.entities.exchange_rate import Currency, ExchangeRate


class ExchangeRateRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> ExchangeRate: ...

    @abstractmethod
    def get_active(
        self, limit: int = 10, offset: int = 0
    ) -> list[ExchangeRate]: ...

    @abstractmethod
    def get_active_by_code(self, currency: Currency) -> ExchangeRate: ...

    @abstractmethod
    def save(self, exchange_rate: ExchangeRate) -> None: ...
