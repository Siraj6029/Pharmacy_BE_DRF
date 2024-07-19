from django.db import models
from pharmacy.core.models import Company, Formula, Distribution, Customer
from .choices import ProductTypeChoices
from django.db.models import Sum
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Product(models.Model):

    name = models.CharField(max_length=255, unique=True)
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
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class ProductProxy(Product):
    class Meta:
        proxy = True
        ordering = ["name"]

    def __str__(self):
        return f"Proxy: {self.name}"

    @property
    def total_qty(self):
        return self.stocks.aggregate(total_qty=Sum("qty"))["total_qty"] or 0


class Stock(models.Model):
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    product = models.ForeignKey(
        Product, related_name="stocks", on_delete=models.CASCADE
    )
    expiry_date = models.DateField(null=True, blank=True)
    entry_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.product.name} - {self.qty}"


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, related_name="orders", on_delete=models.SET_NULL, null=True
    )
    date = models.DateTimeField(default=timezone.now)
    discount = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        null=True,
        default=None,
    )
    total_amount = models.DecimalField(max_digits=99999, decimal_places=2, null=True)
    status = models.CharField(
        choices=[
            ("Pending", "Pending"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled"),
        ],
        max_length=9,
        default="Completed",
    )
    stocks = models.ManyToManyField(Stock, through="StockOrder", related_name="orders")

    def __str__(self):
        return f"{self.stocks}"


class StockOrder(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"StockOrder {self.id} - Order {self.order.id} - Stock {self.stock.id}"
