# Generated by Django 5.0.6 on 2025-02-13 15:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_remove_customer_balance_customer_credit_amount"),
        ("product", "0020_stock_product_sto_barcode_5d0c4d_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="customertransaction",
            name="total_amount",
            field=models.DecimalField(decimal_places=2, default=100, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="distributiontransaction",
            name="total_amount",
            field=models.DecimalField(decimal_places=2, default=100, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customertransaction",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.customer",
            ),
        ),
        migrations.AlterField(
            model_name="customertransaction",
            name="transaction_type",
            field=models.CharField(
                choices=[
                    ("payment_received", "Payment Received"),
                    ("payment_made", "Payment Made"),
                    ("products_recieved", "Products Recieved"),
                ],
                help_text="Type of transaction (e.g., payment received, payment made).",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="distributiontransaction",
            name="transaction_type",
            field=models.CharField(
                choices=[
                    ("payment_received", "Payment Received"),
                    ("payment_made", "Payment Made"),
                    ("products_recieved", "Products Recieved"),
                ],
                help_text="Type of transaction (e.g., payment received, payment made).",
                max_length=20,
            ),
        ),
    ]
