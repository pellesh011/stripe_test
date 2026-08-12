from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.discount import Discount
from payments.domain.exceptions import (
    DiscountNotActiveError,
    DiscountNotFoundError,
    EntityNotFoundError,
)
from payments.domain.repositories.discount import DiscountRepository
from payments.infrastructure.database.models.discount import DiscountModel
from payments.infrastructure.database.repositories.mappers import discount_to_entity


class DiscountRepositoryImpl(DiscountRepository):
    def get_by_id(self, id: int) -> Discount:
        try:
            model = DiscountModel.objects.get(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return discount_to_entity(model)

    def get_active(self, limit: int = 10, offset: int = 0) -> list[Discount]:
        qs = DiscountModel.objects.filter(is_active=True).order_by("id")[
            offset : offset + limit
        ]
        return [discount_to_entity(model) for model in qs]

    def get_active_by_name(self, name: str) -> Discount:
        try:
            model = DiscountModel.objects.get(name=name)
        except ObjectDoesNotExist:
            raise DiscountNotFoundError() from None
        if not model.is_active:
            raise DiscountNotActiveError()
        return discount_to_entity(model)

    def save(self, discount: Discount) -> None:
        if discount.id is None:
            model = DiscountModel.objects.create(
                name=discount.name,
                type=discount.type.value,
                value=discount.value,
                is_active=discount.is_active,
            )
            discount.id = model.id
        else:
            DiscountModel.objects.filter(id=discount.id).update(
                name=discount.name,
                type=discount.type.value,
                value=discount.value,
                is_active=discount.is_active,
            )
