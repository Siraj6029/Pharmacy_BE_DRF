# Generated by Django 5.0.6 on 2024-07-10 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_company_contact_number_alter_company_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="contact_number",
            field=models.CharField(default=None, max_length=15, null=True),
        ),
    ]