from django.db import models

from payments.infrastructure.database.models.enums import CurrencyChoices


class ExchangeRateModel(models.Model):
    base_currency = models.CharField(
        max_length=3, choices=CurrencyChoices, default=CurrencyChoices.USD
    )
    currency = models.CharField(max_length=3, choices=CurrencyChoices)
    coef = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"#{self.pk}: {self.base_currency}→{self.currency} = {self.coef}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["currency", "base_currency"],
                condition=models.Q(is_active=True),
                name="unique_active_exchange_rate",
            ),
        ]
