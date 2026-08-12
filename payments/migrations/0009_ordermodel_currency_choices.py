from django.db import migrations, models


def order_currency_fk_to_code(apps, schema_editor):
    OrderModel = apps.get_model("payments", "OrderModel")
    for order in OrderModel.objects.select_related("currency").iterator():
        order.currency_code = order.currency.currency
        order.save(update_fields=["currency_code"])


def order_currency_code_to_fk(apps, schema_editor):
    OrderModel = apps.get_model("payments", "OrderModel")
    CurrencyModel = apps.get_model("payments", "CurrencyModel")
    currencies_by_code: dict[str, object] = {}
    for currency in CurrencyModel.objects.filter(is_active=True):
        currencies_by_code.setdefault(currency.currency, currency)
    for order in OrderModel.objects.iterator():
        currency = currencies_by_code.get(order.currency_code)
        order.currency = currency
        order.save(update_fields=["currency"])


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0008_remove_cartmodel_currency"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordermodel",
            name="currency_code",
            field=models.CharField(default="usd", max_length=3),
            preserve_default=False,
        ),
        migrations.RunPython(
            order_currency_fk_to_code,
            reverse_code=order_currency_code_to_fk,
        ),
        migrations.RemoveField(
            model_name="ordermodel",
            name="currency",
        ),
        migrations.RenameField(
            model_name="ordermodel",
            old_name="currency_code",
            new_name="currency",
        ),
        migrations.AlterField(
            model_name="ordermodel",
            name="currency",
            field=models.CharField(
                choices=[("usd", "USD"), ("rub", "RUB"), ("eur", "EUR")],
                default="usd",
                max_length=3,
            ),
        ),
    ]
