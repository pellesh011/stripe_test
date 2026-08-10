from decimal import Decimal

from django.db import migrations


def seed_test_data(apps, schema_editor):
    PaymentProviderModel = apps.get_model("payments", "PaymentProviderModel")
    CurrencyModel = apps.get_model("payments", "CurrencyModel")
    ProductModel = apps.get_model("payments", "ProductModel")
    ProductPriceModel = apps.get_model("payments", "ProductPriceModel")

    PaymentProviderModel.objects.create(name="stripe")

    active_currencies = [
        ("usd", Decimal("1.00")),
        ("eur", Decimal("1.10")),
        ("rub", Decimal("0.012")),
    ]
    obsolete_currencies = [
        ("eur", Decimal("0.90")),
        ("rub", Decimal("0.010")),
    ]

    currencies = {}
    for code, coef in active_currencies:
        currencies[code] = CurrencyModel.objects.create(
            base_currency="usd",
            currency=code,
            coef=coef,
            is_active=True,
        )

    for code, coef in obsolete_currencies:
        CurrencyModel.objects.create(
            base_currency="usd",
            currency=code,
            coef=coef,
            is_active=False,
        )

    usd = currencies["usd"]

    products = {}
    for name in ("T-Shirt", "Mug", "Cap"):
        products[name] = ProductModel.objects.create(name=name)

    active_prices = {
        "T-Shirt": Decimal("39.99"),
        "Mug": Decimal("14.99"),
        "Cap": Decimal("24.99"),
    }
    for name, price in active_prices.items():
        ProductPriceModel.objects.create(
            product=products[name],
            currency=usd,
            price=price,
            is_active=True,
        )

    t_shirt = products["T-Shirt"]
    for price in (Decimal("19.99"), Decimal("24.99"), Decimal("29.99")):
        ProductPriceModel.objects.create(
            product=t_shirt,
            currency=usd,
            price=price,
            is_active=False,
        )


def remove_test_data(apps, schema_editor):
    PaymentProviderModel = apps.get_model("payments", "PaymentProviderModel")
    CurrencyModel = apps.get_model("payments", "CurrencyModel")
    ProductModel = apps.get_model("payments", "ProductModel")
    ProductPriceModel = apps.get_model("payments", "ProductPriceModel")

    PaymentProviderModel.objects.filter(name="stripe").delete()

    CurrencyModel.objects.filter(
        base_currency="usd",
        currency__in=["usd", "eur", "rub"],
    ).delete()

    ProductPriceModel.objects.filter(
        product__name__in=["T-Shirt", "Mug", "Cap"],
        currency__currency="usd",
    ).delete()

    ProductModel.objects.filter(
        name__in=["T-Shirt", "Mug", "Cap"],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0002_paymentprovidermodel_paymentmodel_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_test_data, remove_test_data),
    ]
