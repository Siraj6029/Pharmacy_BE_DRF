from django.db import models
from pharmacy.core.models import Company, Formula, Distribution, Customer
from .choices import ProductTypeChoices
from django.db.models import Sum, Q
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from barcode import Code128
from barcode.errors import BarcodeError
from django.core.exceptions import ValidationError
from datetime import date
from ..config import LOW_QTY_THRESHOLD


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
    product_type = models.CharField(
        max_length=10, choices=ProductTypeChoices.get_choices()
    )
    avg_qty = models.IntegerField()
    per_pack = models.IntegerField(default=1)
    market_item = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    @property
    def total_qty(self):
        # Get today's date
        today = date.today()

        # Include stocks where expiry_date is null, 0, or greater than today's date
        return (
            self.stocks.filter(
                Q(expiry_date__gte=today) | Q(expiry_date__isnull=True)
            ).aggregate(total_qty=Sum("qty"))["total_qty"]
            or 0
        )

    @property
    def total_qty_expired(self):
        # Get today's date
        today = date.today()

        # Include stocks where expiry_date is less than today's date
        return (
            self.stocks.filter(expiry_date__lt=today).aggregate(total_qty=Sum("qty"))[
                "total_qty"
            ]
            or 0
        )

    @property
    def total_qty_short_expired(self):
        # Get today's date
        today = date.today()
        six_months_later = today + timezone.timedelta(days=180)

        # Include stocks where expiry_date is less than today's date
        return (
            self.stocks.filter(
                expiry_date__gte=today, expiry_date__lt=six_months_later
            ).aggregate(total_qty=Sum("qty"))["total_qty"]
            or 0
        )

    @property
    def total_qty_expired_and_short_expired(self):
        # Get today's date
        today = date.today()
        six_months_later = today + timezone.timedelta(days=180)

        # Include stocks where expiry_date is less than today's date
        return (
            self.stocks.filter(expiry_date__lt=six_months_later).aggregate(
                total_qty=Sum("qty")
            )["total_qty"]
            or 0
        )

    @property
    def is_active(self):
        return self.avg_qty > 0

    @property
    def required_qty(self):
        rqd_qty = self.avg_qty - self.total_qty
        if rqd_qty < 0:
            return 0
        return rqd_qty

    @property
    def required_low_qty(self):
        if self.avg_qty < 5:
            return self.required_qty
        rqd_qty = int((self.avg_qty * LOW_QTY_THRESHOLD) - self.total_qty)
        if rqd_qty < 0:
            return 0
        return rqd_qty

    def __str__(self):
        return self.name


def validate_code128(barcode):
    try:
        Code128(barcode)
    except BarcodeError:
        raise ValidationError("Invalid Code128 barcode.")


class Stock(models.Model):
    barcode = models.CharField(
        max_length=128, unique=True, validators=[validate_code128]
    )
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    price_per_unit = models.FloatField()
    expiry_date = models.DateField(null=True, blank=True)
    entry_date = models.DateTimeField(auto_now=True)
    perchase_price = models.FloatField()

    # relationships
    product = models.ForeignKey(
        Product, related_name="stocks", on_delete=models.CASCADE
    )
    bought_from = models.ForeignKey(
        Distribution, related_name="stock", on_delete=models.SET_NULL, null=True
    )

    @property
    def total_price(self):
        return self.qty * self.price_per_unit

    @property
    def total_purchase_price(self):
        return self.qty * self.perchase_price

    @property
    def total_profit(self):
        return self.total_price - self.total_purchase_price

    @property
    def total_profit_percent(self):
        return (self.total_profit / self.total_purchase_price) * 100

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.barcode:
            self.barcode = Code128(str(self.id), add_checksum=True).get_fullcode()
            super().save(*args, **kwargs)

    class Meta:
        ordering = ["-entry_date"]

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
    total_amount = models.DecimalField(
        max_digits=99999, decimal_places=2
    )  # , null=True)
    total_after_disc = models.DecimalField(
        max_digits=99999, decimal_places=2
    )  # , null=True)
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
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.stocks}"


class StockOrder(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    def save(self, *args, **kwargs):
        if self.quantity > self.stock.qty:
            raise ValidationError("Ordered quantity cannot exceed available stock.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"StockOrder {self.id} - Order {self.order.id} - Stock {self.stock.id}"
