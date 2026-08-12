from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0009_ordermodel_currency_choices"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="CurrencyModel",
            new_name="ExchangeRateModel",
        ),
        migrations.RemoveConstraint(
            model_name="exchangeratemodel",
            name="unique_active_currency",
        ),
        migrations.AddConstraint(
            model_name="exchangeratemodel",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_active", True)),
                fields=("currency", "base_currency"),
                name="unique_active_exchange_rate",
            ),
        ),
    ]
