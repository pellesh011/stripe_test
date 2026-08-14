from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.order import Order
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.order import OrderRepository
from payments.infrastructure.database.models.order import OrderModel
from payments.infrastructure.database.repositories.loaders import build_order


class OrderRepositoryImpl(OrderRepository):
    def get_by_id(self, id: int) -> Order:
        try:
            model = OrderModel.objects.select_related(
                "cart",
                "discount",
                "tax",
            ).get(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return build_order(model)

    def get_all(self, limit: int = 10, offset: int = 0) -> list[Order]:
        models = OrderModel.objects.select_related(
            "cart",
            "discount",
            "tax",
        ).order_by("-created_at")[offset : offset + limit]
        return [build_order(model) for model in models]

    def count(self) -> int:
        return OrderModel.objects.count()

    def save(self, order: Order) -> None:
        assert order.cart.id is not None

        if order.discount is not None:
            assert order.discount.id is not None

        if order.tax is not None:
            assert order.tax.id is not None

        if order.id is None:
            model = OrderModel.objects.create(
                cart_id=order.cart.id,
                currency=order.currency.value,
                discount_id=order.discount.id if order.discount is not None else None,
                tax_id=order.tax.id if order.tax is not None else None,
                status=order.status.value,
            )
            order.id = model.id
        else:
            OrderModel.objects.filter(id=order.id).update(
                cart_id=order.cart.id,
                currency=order.currency.value,
                discount_id=order.discount.id if order.discount is not None else None,
                tax_id=order.tax.id if order.tax is not None else None,
                status=order.status.value,
            )

    def delete(self, order: Order) -> None:
        OrderModel.objects.get(id=order.id).delete()
