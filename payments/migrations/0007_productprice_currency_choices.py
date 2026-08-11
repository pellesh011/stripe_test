import django.db.models.deletion
from django.db import migrations, models


def product_price_currency_fk_to_code(apps, schema_editor):
    ProductPriceModel = apps.get_model("payments", "ProductPriceModel")
    for product_price in ProductPriceModel.objects.select_related("currency").iterator():
        product_price.currency_code = product_price.currency.currency
        product_price.save(update_fields=["currency_code"])


def product_price_currency_code_to_fk(apps, schema_editor):
    ProductPriceModel = apps.get_model("payments", "ProductPriceModel")
    CurrencyModel = apps.get_model("payments", "CurrencyModel")
    currencies_by_code: dict[str, object] = {}
    for currency in CurrencyModel.objects.filter(is_active=True):
        currencies_by_code.setdefault(currency.currency, currency)
    for product_price in ProductPriceModel.objects.iterator():
        currency = currencies_by_code.get(product_price.currency_code)
        product_price.currency = currency
        product_price.save(update_fields=["currency"])


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0006_ordermodel_discount"),
    ]

    operations = [
        migrations.AddField(
            model_name="productpricemodel",
            name="currency_code",
            field=models.CharField(default="usd", max_length=3),
            preserve_default=False,
        ),
        migrations.RunPython(
            product_price_currency_fk_to_code,
            reverse_code=product_price_currency_code_to_fk,
        ),
        migrations.RemoveField(
            model_name="productpricemodel",
            name="currency",
        ),
        migrations.RenameField(
            model_name="productpricemodel",
            old_name="currency_code",
            new_name="currency",
        ),
        migrations.AlterField(
            model_name="productpricemodel",
            name="currency",
            field=models.CharField(
                choices=[("usd", "USD"), ("rub", "RUB"), ("eur", "EUR")],
                default="usd",
                max_length=3,
            ),
        ),
    ]
