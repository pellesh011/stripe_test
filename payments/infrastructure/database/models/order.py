from django.db import models

from payments.infrastructure.database.models.cart import CartModel
from payments.infrastructure.database.models.currency import CurrencyModel
from payments.infrastructure.database.models.enums import OrderStatusChoices


class OrderModel(models.Model):
    cart = models.OneToOneField(
        "CartModel",
        on_delete=models.PROTECT,
        related_name="order",
    )

    currency = models.ForeignKey(
        "CurrencyModel",
        on_delete=models.PROTECT,
        related_name="orders",
    )

    status = models.CharField(
        max_length=30,
        choices=OrderStatusChoices,
        default=OrderStatusChoices.CREATED,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

class OrderItemModel(models.Model):
    order = models.ForeignKey(
        OrderModel,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "ProductModel",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    product_price = models.ForeignKey(
        "ProductPriceModel",
        on_delete=models.PROTECT,
        related_name="order_items",
    )