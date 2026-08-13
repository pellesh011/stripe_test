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
    def get_by_id(self, id: int) -> PaymentProvider:
        try:
            model = PaymentProviderModel.objects.get(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return payment_provider_to_entity(model)

    def get_default(self) -> PaymentProvider:
        model = PaymentProviderModel.objects.order_by("id").first()
        if model is None:
            raise EntityNotFoundError() from None
        return payment_provider_to_entity(model)

    def save(self, payment_provider: PaymentProvider) -> None:
        if payment_provider.id is None:
            model = PaymentProviderModel.objects.create(
                name=payment_provider.name,
            )
            payment_provider.id = model.id
        else:
            PaymentProviderModel.objects.filter(id=payment_provider.id).update(
                name=payment_provider.name,
            )
