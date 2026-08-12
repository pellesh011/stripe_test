from django.db import migrations, models


def payment_currency_fk_to_code(apps, schema_editor):
    PaymentModel = apps.get_model("payments", "PaymentModel")
    for payment in PaymentModel.objects.select_related("currency").iterator():
        payment.currency_code = payment.currency.currency
        payment.save(update_fields=["currency_code"])


def payment_currency_code_to_fk(apps, schema_editor):
    PaymentModel = apps.get_model("payments", "PaymentModel")
    ExchangeRateModel = apps.get_model("payments", "ExchangeRateModel")
    currencies_by_code: dict[str, object] = {}
    for exchange_rate in ExchangeRateModel.objects.filter(is_active=True):
        currencies_by_code.setdefault(exchange_rate.currency, exchange_rate)
    for payment in PaymentModel.objects.iterator():
        exchange_rate = currencies_by_code.get(payment.currency_code)
        payment.currency = exchange_rate
        payment.save(update_fields=["currency"])


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0011_orderitemmodel_exchange_rate_and_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentmodel",
            name="currency_code",
            field=models.CharField(default="usd", max_length=3),
            preserve_default=False,
        ),
        migrations.RunPython(
            payment_currency_fk_to_code,
            reverse_code=payment_currency_code_to_fk,
        ),
        migrations.RemoveField(
            model_name="paymentmodel",
            name="currency",
        ),
        migrations.RenameField(
            model_name="paymentmodel",
            old_name="currency_code",
            new_name="currency",
        ),
        migrations.AlterField(
            model_name="paymentmodel",
            name="currency",
            field=models.CharField(
                choices=[("usd", "USD"), ("rub", "RUB"), ("eur", "EUR")],
                default="usd",
                max_length=3,
            ),
        ),
    ]