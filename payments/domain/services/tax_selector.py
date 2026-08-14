from abc import ABC, abstractmethod

from payments.domain.entities.tax import Tax


class TaxSelector(ABC):
    @abstractmethod
    def select(self) -> Tax: ...
