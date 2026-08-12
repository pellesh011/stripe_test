from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.tax import Tax
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.tax import TaxRepository
from payments.infrastructure.database.models.tax import TaxModel
from payments.infrastructure.database.repositories.mappers import tax_to_entity


class TaxRepositoryImpl(TaxRepository):
    def get_by_id(self, id: int) -> Tax:
        try:
            model = TaxModel.objects.get(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return tax_to_entity(model)

    def save(self, tax: Tax) -> None:
        if tax.id is None:
            model = TaxModel.objects.create(
                name=tax.name,
                rate=tax.rate,
            )
            tax.id = model.id
        else:
            TaxModel.objects.filter(id=tax.id).update(
                name=tax.name,
                rate=tax.rate,
            )
