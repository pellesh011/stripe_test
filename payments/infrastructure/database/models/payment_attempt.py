from django.db import models

from payments.infrastructure.database.models.enums import PaymentAttemptStatusChoices


class PaymentAttemptModel(models.Model):
    external_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    provider = models.ForeignKey(
        "PaymentProviderModel",
        on_delete=models.PROTECT,
        related_name="payment_attempts",
    )

    payment = models.ForeignKey(
        "PaymentModel",
        on_delete=models.CASCADE,
        related_name="attempts",
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentAttemptStatusChoices,
        default=PaymentAttemptStatusChoices.CREATED,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
