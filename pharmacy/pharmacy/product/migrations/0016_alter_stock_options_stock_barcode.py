# Generated by Django 5.0.6 on 2025-01-23 15:33

import pharmacy.product.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0015_alter_order_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="stock",
            options={"ordering": ["-entry_date"]},
        ),
        migrations.AddField(
            model_name="stock",
            name="barcode",
            field=models.CharField(
                default=123,
                max_length=128,
                unique=True,
                validators=[pharmacy.product.models.validate_code128],
            ),
            preserve_default=False,
        ),
    ]
