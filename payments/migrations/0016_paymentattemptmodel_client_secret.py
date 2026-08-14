from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0015_stripewebhookeventmodel"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentattemptmodel",
            name="client_secret",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]