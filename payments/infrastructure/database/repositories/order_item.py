from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.order_item import OrderItem
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.order_item import OrderItemRepository
from payments.infrastructure.database.models.order import OrderItemModel
from payments.infrastructure.database.repositories.loaders import (
    ORDER_ITEM_SELECT_RELATED,
)
from payments.infrastructure.database.repositories.mappers import order_item_to_entity


class OrderItemRepositoryImpl(OrderItemRepository):
    def get_by_id(self, id: int) -> OrderItem:
        try:
            model = OrderItemModel.objects.select_related(
                *ORDER_ITEM_SELECT_RELATED
            ).get(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return order_item_to_entity(model)

    def get_by_order_id(
        self, order_id: int, limit: int = 10, offset: int = 0
    ) -> list[OrderItem]:
        qs = (
            OrderItemModel.objects.filter(order_id=order_id)
            .select_related(*ORDER_ITEM_SELECT_RELATED)
            .order_by("id")[offset : offset + limit]
        )
        return [order_item_to_entity(model) for model in qs]

    def save(self, order_item: OrderItem) -> None:
        if order_item.order is None:
            raise ValueError("order_item must reference an order to be saved")

        assert order_item.order.id is not None
        assert order_item.product.id is not None
        assert order_item.product_price.id is not None
        assert order_item.exchange_rate.id is not None

        if order_item.id is None:
            model = OrderItemModel.objects.create(
                order_id=order_item.order.id,
                product_id=order_item.product.id,
                product_price_id=order_item.product_price.id,
                exchange_rate_id=order_item.exchange_rate.id,
                price=order_item.price,
            )
            order_item.id = model.id
        else:
            OrderItemModel.objects.filter(id=order_item.id).update(
                order_id=order_item.order.id,
                product_id=order_item.product.id,
                product_price_id=order_item.product_price.id,
                exchange_rate_id=order_item.exchange_rate.id,
                price=order_item.price,
            )

    def delete(self, order_item: OrderItem) -> None:
        assert order_item.id is not None
        OrderItemModel.objects.get(id=order_item.id).delete()
