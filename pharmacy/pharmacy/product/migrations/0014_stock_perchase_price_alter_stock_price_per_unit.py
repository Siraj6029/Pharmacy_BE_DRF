# Generated by Django 5.0.6 on 2025-01-09 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0013_order_created_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="stock",
            name="perchase_price",
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="stock",
            name="price_per_unit",
            field=models.FloatField(),
        ),
    ]
