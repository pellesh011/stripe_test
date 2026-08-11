from django.db import models

from payments.infrastructure.database.models.enums import DiscountTypeChoices


class DiscountModel(models.Model):
    name = models.CharField(max_length=255)

    type = models.CharField(
        max_length=20,
        choices=DiscountTypeChoices.choices,
    )

    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    is_active = models.BooleanField(default=True)
