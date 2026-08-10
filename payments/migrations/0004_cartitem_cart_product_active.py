import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0003_seed_test_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="productmodel",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="cartitemmodel",
            name="cart",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="items",
                to="payments.cartmodel",
            ),
            preserve_default=False,
        ),
    ]
