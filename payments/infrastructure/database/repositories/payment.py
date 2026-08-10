from payments.domain.entities.payment import Payment
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.payment import PaymentRepository
from payments.infrastructure.database.models.payment import PaymentModel
from payments.infrastructure.database.repositories.loaders import build_payment

PAYMENT_SELECT_RELATED = (
    "currency",
    "order__cart__currency",
    "order__currency",
)


class PaymentRepositoryImpl(PaymentRepository):
    async def _get_or_none(self, **filters) -> PaymentModel | None:
        return (
            await PaymentModel.objects.select_related(*PAYMENT_SELECT_RELATED)
            .filter(**filters)
            .order_by("-id")
            .afirst()
        )

    async def get_by_id(self, id: int) -> Payment:
        model = await self._get_or_none(id=id)
        if model is None:
            raise EntityNotFoundError()
        return await build_payment(model)

    async def get_by_order_id(self, order_id: int) -> Payment:
        model = await self._get_or_none(order_id=order_id)
        if model is None:
            raise EntityNotFoundError()
        return await build_payment(model)

    async def save(self, payment: Payment) -> None:
        assert payment.order.id is not None
        assert payment.currency.id is not None

        if payment.id is None:
            model = await PaymentModel.objects.acreate(
                order_id=payment.order.id,
                amount=payment.amount,
                currency_id=payment.currency.id,
                status=payment.status.value,
            )
            payment.id = model.id
        else:
            await PaymentModel.objects.filter(id=payment.id).aupdate(
                order_id=payment.order.id,
                amount=payment.amount,
                currency_id=payment.currency.id,
                status=payment.status.value,
            )
