from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.discount import Discount
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.discount import DiscountRepository
from payments.infrastructure.database.models.discount import DiscountModel
from payments.infrastructure.database.repositories.mappers import discount_to_entity


class DiscountRepositoryImpl(DiscountRepository):
    async def get_by_id(self, id: int) -> Discount:
        try:
            model = await DiscountModel.objects.aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return discount_to_entity(model)

    async def get_active(self) -> list[Discount]:
        return [
            discount_to_entity(model)
            async for model in DiscountModel.objects.filter(is_active=True)
        ]

    async def save(self, discount: Discount) -> None:
        if discount.id is None:
            model = await DiscountModel.objects.acreate(
                name=discount.name,
                type=discount.type.value,
                value=discount.value,
                is_active=discount.is_active,
            )
            discount.id = model.id
        else:
            await DiscountModel.objects.filter(id=discount.id).aupdate(
                name=discount.name,
                type=discount.type.value,
                value=discount.value,
                is_active=discount.is_active,
            )
