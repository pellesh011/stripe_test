from django.conf import settings
from django.db import models

from payments.infrastructure.database.models.enums import (
    CurrencyChoices,
    PaymentStatusChoices,
)
from payments.infrastructure.database.models.order import OrderModel


class PaymentModel(models.Model):
    order = models.ForeignKey(
        OrderModel,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices,
        default=CurrencyChoices.USD,
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices,
        default=PaymentStatusChoices.CREATED,
    )
