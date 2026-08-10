from django.db import models

from payments.infrastructure.database.models.currency import CurrencyModel

class ProductModel(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True
    )

class ProductPriceModel(models.Model):
    currency = models.ForeignKey(
        CurrencyModel,
        on_delete=models.PROTECT,
        related_name="product_prices",
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    is_active = models.BooleanField(
        default=True,
    )

    product = models.ForeignKey(
        ProductModel, 
        on_delete=models.PROTECT,
        related_name="prices"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "currency"],
                condition=models.Q(is_active=True),
                name="unique_active_product_currency_price",
            ),
        ]
