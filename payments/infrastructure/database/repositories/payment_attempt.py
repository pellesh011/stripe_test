from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.payment_attempts import PaymentAttempt
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.payment_attempt import PaymentAttemptRepository
from payments.infrastructure.database.models.payment_attempt import (
    PaymentAttemptModel,
)
from payments.infrastructure.database.repositories.loaders import build_payment
from payments.infrastructure.database.repositories.mappers import (
    payment_attempt_to_entity,
    payment_provider_to_entity,
)

PAYMENT_ATTEMPT_SELECT_RELATED = (
    "provider",
    "payment__currency",
    "payment__order__cart__currency",
    "payment__order__currency",
    "payment__order__discount",
)


class PaymentAttemptRepositoryImpl(PaymentAttemptRepository):
    async def get_by_id(self, id: int) -> PaymentAttempt:
        try:
            model = await PaymentAttemptModel.objects.select_related(
                *PAYMENT_ATTEMPT_SELECT_RELATED
            ).aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return await self._to_entity(model)

    async def get_by_payment_id(
        self, payment_id: int, limit: int = 10, offset: int = 0
    ) -> list[PaymentAttempt]:
        qs = (
            PaymentAttemptModel.objects.filter(payment_id=payment_id)
            .select_related(*PAYMENT_ATTEMPT_SELECT_RELATED)
            .order_by("id")[offset : offset + limit]
        )
        return [await self._to_entity(model) async for model in qs]

    async def _to_entity(self, model: PaymentAttemptModel) -> PaymentAttempt:
        provider = payment_provider_to_entity(model.provider)
        payment = await build_payment(model.payment)
        return payment_attempt_to_entity(model, provider, payment)

    async def save(self, payment_attempt: PaymentAttempt) -> None:
        assert payment_attempt.provider.id is not None
        assert payment_attempt.payment.id is not None

        if payment_attempt.id is None:
            model = await PaymentAttemptModel.objects.acreate(
                external_id=payment_attempt.external_id,
                provider_id=payment_attempt.provider.id,
                payment_id=payment_attempt.payment.id,
                status=payment_attempt.status.value,
                completed_at=payment_attempt.completed_at,
            )
            payment_attempt.id = model.id
        else:
            await PaymentAttemptModel.objects.filter(id=payment_attempt.id).aupdate(
                external_id=payment_attempt.external_id,
                provider_id=payment_attempt.provider.id,
                payment_id=payment_attempt.payment.id,
                status=payment_attempt.status.value,
                completed_at=payment_attempt.completed_at,
            )
