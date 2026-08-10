from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.payment_provider import PaymentProvider
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.payment_provider import PaymentProviderRepository
from payments.infrastructure.database.models.payment_provider import (
    PaymentProviderModel,
)
from payments.infrastructure.database.repositories.mappers import (
    payment_provider_to_entity,
)


class PaymentProviderRepositoryImpl(PaymentProviderRepository):
    async def get_by_id(self, id: int) -> PaymentProvider:
        try:
            model = await PaymentProviderModel.objects.aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return payment_provider_to_entity(model)

    async def save(self, payment_provider: PaymentProvider) -> None:
        if payment_provider.id is None:
            model = await PaymentProviderModel.objects.acreate(
                name=payment_provider.name,
            )
            payment_provider.id = model.id
        else:
            await PaymentProviderModel.objects.filter(id=payment_provider.id).aupdate(
                name=payment_provider.name,
            )
