from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.order_item import OrderItem
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.order_item import OrderItemRepository
from payments.infrastructure.database.models.order import OrderItemModel
from payments.infrastructure.database.repositories.loaders import (
    CART_ITEM_SELECT_RELATED,
)
from payments.infrastructure.database.repositories.mappers import order_item_to_entity


class OrderItemRepositoryImpl(OrderItemRepository):
    async def get_by_id(self, id: int) -> OrderItem:
        try:
            model = await OrderItemModel.objects.select_related(
                *CART_ITEM_SELECT_RELATED
            ).aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return order_item_to_entity(model)

    async def get_by_order_id(
        self, order_id: int, limit: int = 10, offset: int = 0
    ) -> list[OrderItem]:
        qs = (
            OrderItemModel.objects.filter(order_id=order_id)
            .select_related(*CART_ITEM_SELECT_RELATED)
            .order_by("id")[offset : offset + limit]
        )
        return [order_item_to_entity(model) async for model in qs]

    async def save(self, order_item: OrderItem) -> None:
        if order_item.order is None:
            raise ValueError("order_item must reference an order to be saved")

        assert order_item.order.id is not None
        assert order_item.product.id is not None
        assert order_item.product_price.id is not None

        if order_item.id is None:
            model = await OrderItemModel.objects.acreate(
                order_id=order_item.order.id,
                product_id=order_item.product.id,
                product_price_id=order_item.product_price.id,
            )
            order_item.id = model.id
        else:
            await OrderItemModel.objects.filter(id=order_item.id).aupdate(
                order_id=order_item.order.id,
                product_id=order_item.product.id,
                product_price_id=order_item.product_price.id,
            )
