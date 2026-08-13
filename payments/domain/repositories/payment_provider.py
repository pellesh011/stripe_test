from abc import ABC, abstractmethod

from payments.domain.entities.payment_provider import PaymentProvider


class PaymentProviderRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> PaymentProvider: ...

    @abstractmethod
    def get_default(self) -> PaymentProvider: ...

    @abstractmethod
    def save(self, payment_provider: PaymentProvider) -> None: ...
