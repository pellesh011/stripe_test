from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.tax import Tax
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.tax import TaxRepository
from payments.infrastructure.database.models.tax import TaxModel
from payments.infrastructure.database.repositories.mappers import tax_to_entity


class TaxRepositoryImpl(TaxRepository):
    async def get_by_id(self, id: int) -> Tax:
        try:
            model = await TaxModel.objects.aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return tax_to_entity(model)

    async def save(self, tax: Tax) -> None:
        if tax.id is None:
            model = await TaxModel.objects.acreate(
                name=tax.name,
                rate=tax.rate,
            )
            tax.id = model.id
        else:
            await TaxModel.objects.filter(id=tax.id).aupdate(
                name=tax.name,
                rate=tax.rate,
            )
