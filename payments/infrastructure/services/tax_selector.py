from payments.domain.entities.tax import Tax
from payments.domain.repositories.tax import TaxRepository
from payments.domain.services.tax_selector import TaxSelector

DEFAULT_TAX_ID = 1


class DefaultTaxSelector(TaxSelector):
    def __init__(self, taxes: TaxRepository):
        self._taxes = taxes

    def select(self) -> Tax:
        return self._taxes.get_by_id(DEFAULT_TAX_ID)
