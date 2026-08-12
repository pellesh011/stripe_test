from payments.domain.entities.payment import Payment
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.payment import PaymentRepository
from payments.infrastructure.database.models.payment import PaymentModel
from payments.infrastructure.database.repositories.loaders import build_payment

PAYMENT_SELECT_RELATED = (
    "order__cart",
    "order__discount",
)


class PaymentRepositoryImpl(PaymentRepository):
    def _get_or_none(self, **filters) -> PaymentModel | None:
        return (
            PaymentModel.objects.select_related(*PAYMENT_SELECT_RELATED)
            .filter(**filters)
            .order_by("-id")
            .first()
        )

    def get_by_id(self, id: int) -> Payment:
        model = self._get_or_none(id=id)
        if model is None:
            raise EntityNotFoundError()
        return build_payment(model)

    def get_by_order_id(self, order_id: int) -> Payment:
        model = self._get_or_none(order_id=order_id)
        if model is None:
            raise EntityNotFoundError()
        return build_payment(model)

    def save(self, payment: Payment) -> None:
        assert payment.order.id is not None

        if payment.id is None:
            model = PaymentModel.objects.create(
                order_id=payment.order.id,
                amount=payment.amount,
                currency=payment.currency.value,
                status=payment.status.value,
            )
            payment.id = model.id
        else:
            PaymentModel.objects.filter(id=payment.id).update(
                order_id=payment.order.id,
                amount=payment.amount,
                currency=payment.currency.value,
                status=payment.status.value,
            )
