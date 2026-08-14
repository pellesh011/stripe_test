from django.db import models

from payments.infrastructure.database.models.enums import CurrencyChoices


class ProductModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"#{self.pk}: {self.name}"


class ProductPriceModel(models.Model):
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices,
        default=CurrencyChoices.USD,
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    is_active = models.BooleanField(
        default=True,
    )

    product = models.ForeignKey(
        ProductModel, on_delete=models.PROTECT, related_name="prices"
    )

    def __str__(self):
        return f"#{self.pk}: {self.price} {self.currency}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "currency"],
                condition=models.Q(is_active=True),
                name="unique_active_product_currency_price",
            ),
        ]
