# Generated by Django 5.0.6 on 2024-12-04 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0010_alter_order_total_after_disc_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="market_item",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="order",
            name="total_after_disc",
            field=models.DecimalField(decimal_places=2, default=22, max_digits=99999),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="order",
            name="total_amount",
            field=models.DecimalField(decimal_places=2, default=22, max_digits=99999),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="product",
            name="product_type",
            field=models.CharField(
                choices=[
                    ("TAB", "Tablets"),
                    ("SYP", "Syrup"),
                    ("CREAM", "Cream"),
                    ("CAP", "Capsule"),
                    ("INJ", "Injection"),
                    ("DROPS", "Drops"),
                    ("DRIP", "Drips"),
                    ("SECHET", "Sechet"),
                    ("SAOP", "Saop"),
                    ("T/PASTE", "T/Paste"),
                    ("OINTMENT", "Ointment"),
                    ("LOTION", "Lotion"),
                    ("B/CREAM", "B/Cream"),
                    ("OTH", "Others"),
                ],
                max_length=10,
            ),
        ),
    ]
