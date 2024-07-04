from django.db import models
from pharmacy.core.models import Company, Formula, Distribution
from .choices import ProductTypeChoices


class Product(models.Model):
    # PRODUCT_TYPE_CHOICES = [
    #     ("TAB", "Tablets"),
    #     ("SYP", "Syrup"),
    #     ("CR", "Cream"),
    #     ("CAP", "Capsule"),
    #     ("INJ", "Injection"),
    #     ("DRO", "Drops"),
    #     ("DRI", "Drips"),
    #     ("SEC", "Sechet"),
    #     ("OTH", "Others"),
    # ]

    name = models.CharField(max_length=255)
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    formula = models.ForeignKey(
        Formula, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    distribution = models.ForeignKey(
        Distribution, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    price_per_unit = models.IntegerField()
    product_type = models.CharField(
        max_length=3, choices=ProductTypeChoices.get_choices()
    )
    avg_qty = models.IntegerField()
    per_pack = models.IntegerField(default=1)
    desctiption = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Stock(models.Model):
    qty = models.IntegerField()
    product = models.ForeignKey(
        Product, related_name="stocks", on_delete=models.CASCADE
    )
    expiry_date = models.DateField(null=True, blank=True)
    entry_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.qty}"
