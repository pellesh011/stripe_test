from django.db import models

from payments.infrastructure.database.models.enums import (
    CurrencyChoices,
    OrderStatusChoices,
)
from payments.infrastructure.database.models.exchange_rate import ExchangeRateModel


class OrderModel(models.Model):
    cart = models.OneToOneField(
        "CartModel",
        on_delete=models.PROTECT,
        related_name="order",
    )

    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices,
        default=CurrencyChoices.USD,
    )

    discount = models.ForeignKey(
        "DiscountModel",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )

    tax = models.ForeignKey(
        "TaxModel",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=OrderStatusChoices,
        default=OrderStatusChoices.CREATED,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"#{self.pk}: {self.status} ({self.currency})"


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

    exchange_rate = models.ForeignKey(
        ExchangeRateModel,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    def __str__(self):
        return f"#{self.pk}: {self.product.name} x {self.price} {self.order.currency}"
