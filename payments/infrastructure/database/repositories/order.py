from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.order import Order
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.order import OrderRepository
from payments.infrastructure.database.models.order import OrderModel
from payments.infrastructure.database.repositories.loaders import build_order


class OrderRepositoryImpl(OrderRepository):
    async def get_by_id(self, id: int) -> Order:
        try:
            model = await OrderModel.objects.select_related(
                "cart__currency",
                "currency",
                "discount",
            ).aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return await build_order(model)

    async def save(self, order: Order) -> None:
        assert order.cart.id is not None
        assert order.currency.id is not None

        if order.discount is not None:
            assert order.discount.id is not None

        if order.id is None:
            model = await OrderModel.objects.acreate(
                cart_id=order.cart.id,
                currency_id=order.currency.id,
                discount_id=order.discount.id if order.discount is not None else None,
                status=order.status.value,
            )
            order.id = model.id
        else:
            await OrderModel.objects.filter(id=order.id).aupdate(
                cart_id=order.cart.id,
                currency_id=order.currency.id,
                discount_id=order.discount.id if order.discount is not None else None,
                status=order.status.value,
            )
