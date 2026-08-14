from django.db import models


class StripeWebhookEventModel(models.Model):
    event_id = models.CharField(
        max_length=255,
        unique=True,
    )

    event_type = models.CharField(
        max_length=255,
    )

    status = models.CharField(
        max_length=32,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"#{self.pk}: {self.event_type} ({self.event_id})"
