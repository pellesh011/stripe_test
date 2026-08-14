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
    "payment__order__cart",
    "payment__order__discount",
    "payment__order__tax",
)


class PaymentAttemptRepositoryImpl(PaymentAttemptRepository):
    def get_by_id(self, id: int) -> PaymentAttempt:
        try:
            model = PaymentAttemptModel.objects.select_related(
                *PAYMENT_ATTEMPT_SELECT_RELATED
            ).get(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return self._to_entity(model)

    def get_by_id_for_update(self, id: int) -> PaymentAttempt:
        locked = (
            PaymentAttemptModel.objects.select_for_update()
            .filter(id=id)
            .values_list("id", flat=True)
            .first()
        )
        if locked is None:
            raise EntityNotFoundError()
        try:
            model = PaymentAttemptModel.objects.select_related(
                *PAYMENT_ATTEMPT_SELECT_RELATED
            ).get(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return self._to_entity(model)

    def get_by_payment_id(
        self, payment_id: int, limit: int = 10, offset: int = 0
    ) -> list[PaymentAttempt]:
        qs = (
            PaymentAttemptModel.objects.filter(payment_id=payment_id)
            .select_related(*PAYMENT_ATTEMPT_SELECT_RELATED)
            .order_by("id")[offset : offset + limit]
        )
        return [self._to_entity(model) for model in qs]

    def get_by_order_id(self, order_id: int) -> list[PaymentAttempt]:
        qs = (
            PaymentAttemptModel.objects.filter(payment__order_id=order_id)
            .select_related(*PAYMENT_ATTEMPT_SELECT_RELATED)
            .order_by("-id")
        )
        return [self._to_entity(model) for model in qs]

    def _to_entity(self, model: PaymentAttemptModel) -> PaymentAttempt:
        provider = payment_provider_to_entity(model.provider)
        payment = build_payment(model.payment)
        return payment_attempt_to_entity(model, provider, payment)

    def get_all_by_external_id(self, external_id: str) -> list[PaymentAttempt]:
        qs = (
            PaymentAttemptModel.objects.filter(external_id=external_id)
            .select_related(*PAYMENT_ATTEMPT_SELECT_RELATED)
            .order_by("id")
        )
        return [self._to_entity(model) for model in qs]

    def save(self, payment_attempt: PaymentAttempt) -> None:
        assert payment_attempt.provider.id is not None
        assert payment_attempt.payment.id is not None

        if payment_attempt.id is None:
            model = PaymentAttemptModel.objects.create(
                external_id=payment_attempt.external_id,
                client_secret=payment_attempt.client_secret,
                provider_id=payment_attempt.provider.id,
                payment_id=payment_attempt.payment.id,
                status=payment_attempt.status.value,
                completed_at=payment_attempt.completed_at,
            )
            payment_attempt.id = model.id
        else:
            PaymentAttemptModel.objects.filter(id=payment_attempt.id).update(
                external_id=payment_attempt.external_id,
                client_secret=payment_attempt.client_secret,
                provider_id=payment_attempt.provider.id,
                payment_id=payment_attempt.payment.id,
                status=payment_attempt.status.value,
                completed_at=payment_attempt.completed_at,
            )
