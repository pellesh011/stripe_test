from abc import ABC, abstractmethod

from payments.domain.entities.payment_provider import PaymentProvider


class PaymentProviderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> PaymentProvider: ...

    @abstractmethod
    async def save(self, payment_provider: PaymentProvider) -> None: ...
