from django.db import models

from payments.infrastructure.database.models.enums import CartStatusChoices
from payments.infrastructure.database.models.product import (
    ProductModel,
    ProductPriceModel,
)


class CartModel(models.Model):
    status = models.CharField(
        max_length=20,
        choices=CartStatusChoices,
        default=CartStatusChoices.ACTIVE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"#{self.pk}: {self.status}"


class CartItemModel(models.Model):
    cart = models.ForeignKey(
        CartModel,
        on_delete=models.PROTECT,
        related_name="items",
    )
    product = models.ForeignKey(
        ProductModel,
        on_delete=models.PROTECT,
        related_name="cart_items",
    )
    product_price = models.ForeignKey(
        ProductPriceModel,
        on_delete=models.PROTECT,
        related_name="cart_items",
    )

    def __str__(self):
        price = f"{self.product_price.price} {self.product_price.currency}"
        return f"#{self.pk}: {self.product.name} x {price}"
