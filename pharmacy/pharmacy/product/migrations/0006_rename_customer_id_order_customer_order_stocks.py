# Generated by Django 5.0.6 on 2024-07-11 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0005_productproxy_alter_stock_qty_order_stockorder"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="customer_id",
            new_name="customer",
        ),
        migrations.AddField(
            model_name="order",
            name="stocks",
            field=models.ManyToManyField(
                related_name="orders", through="product.StockOrder", to="product.stock"
            ),
        ),
    ]
