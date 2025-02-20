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
from pharmacy.config import LOW_QTY_THRESHOLD, MAX_DISCOUNT_PERCENTAGE
from pharmacy.utills.enums import DiscrepancyTypeEnum, TransactionType, OrderStatusEnum


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
    updated_at = models.DateTimeField(auto_now=True)

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
        max_length=128,
        unique=True,
        validators=[validate_code128],
        null=True,
        blank=True,
    )
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    price_per_unit = models.FloatField()
    expiry_date = models.DateField(null=True, blank=True)
    entry_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

    # relationships
    product = models.ForeignKey(
        Product, related_name="stocks", on_delete=models.CASCADE
    )
    bought_from = models.ForeignKey(
        Distribution, related_name="stock", on_delete=models.SET_NULL, null=True
    )
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stocks",
        help_text="User who recorded the stocks.",
    )

    @property
    def total_price(self):
        return self.qty * self.price_per_unit

    @property
    def total_purchase_price(self):
        return self.qty * self.purchase_price

    @property
    def expected_profit(self):
        return self.total_price - self.total_purchase_price

    @property
    def total_profit_percent(self):
        return (self.expected_profit / self.total_purchase_price) * 100

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.barcode:
            self.barcode = Code128(str(self.id)).get_fullcode()
            super().save(*args, **kwargs)

    class Meta:
        ordering = ["-entry_date"]
        indexes = [models.Index(fields=["barcode"])]

    def __str__(self):
        return f"{self.id} - {self.product.name} - {self.qty}"


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, related_name="orders", on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(
        validators=[MinValueValidator(1)], decimal_places=2, max_digits=10
    )  # , null=True)
    total_after_disc = models.DecimalField(
        validators=[MinValueValidator(1)], decimal_places=2, max_digits=10
    )  # , null=True)
    status = models.CharField(
        choices=OrderStatusEnum.choices(), max_length=10, default="Pending"
    )
    stocks = models.ManyToManyField(Stock, through="StockOrder", related_name="orders")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )

    # def clean(self):
    #     if not self.pk and self.status != OrderStatusEnum.PENDING.value:
    #         raise ValidationError("New orders can only have status 'Pending'.")

    #     if self.pk:
    #         prev_status = Order.objects.get(pk=self.pk).status
    #         if prev_status != self.status:
    #             if (
    #                 prev_status == OrderStatusEnum.PENDING.value
    #                 and not self.status == OrderStatusEnum.COMPLETED.value
    #             ):
    #                 raise ValidationError(
    #                     "Pending orders status can only be updated to Completed"
    #                 )
    #             elif (
    #                 prev_status == OrderStatusEnum.COMPLETED.value
    #                 and not self.status == OrderStatusEnum.CANCELLED.value
    #             ):
    #                 raise ValidationError(
    #                     "Completed orders status can only be updated to Cancelled"
    #                 )
    #             elif prev_status == OrderStatusEnum.CANCELLED.value:
    #                 raise ValidationError("Cancelled orders status cannot be updated")

    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         prev_status = Order.objects.get(pk=self.pk).status
    #         if (
    #             prev_status == OrderStatusEnum.PENDING.value
    #             and self.status == OrderStatusEnum.COMPLETED.value
    #         ):
    #             for stock_order in self.stock_orders.all():
    #                 stock_order.stock.qty -= stock_order.quantity
    #                 stock_order.stock.save()
    #         elif (
    #             prev_status == OrderStatusEnum.COMPLETED.value
    #             and self.status == OrderStatusEnum.CANCELLED.value
    #         ):
    #             for stock_order in self.stock_orders.select_related("stock").all():
    #                 stock_order.stock.qty += stock_order.quantity
    #                 stock_order.stock.save()

    #     # Calculate total amount from stock
    #     self.total_amount = sum(
    #         stock_order.quantity * stock_order.stock.price_per_unit
    #         for stock_order in self.stock_orders.all()
    #     )

    #     # Ensure total_after_disc is not less than total_amount - total_amount * 12/100
    #     min_total_after_disc = self.total_amount - (
    #         self.total_amount * MAX_DISCOUNT_PERCENTAGE / 100
    #     )
    #     if self.total_after_disc < min_total_after_disc:
    #         raise ValidationError(
    #             f"Total after discount must not be less than {min_total_after_disc:.2f}"
    #         )
    #     if self.total_after_disc > self.total_amount:
    #         raise ValidationError(
    #             f"Total after discount must not be greater than total amount: {self.total_amount}"
    #         )

    #     super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.stocks}"


class StockOrder(models.Model):
    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="stock_orders"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="stock_orders"
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         # If updating an existing StockOrder, adjust the stock quantity accordingly
    #         previous_quantity = StockOrder.objects.get(pk=self.pk).quantity
    #         new_quantity = self.quantity - previous_quantity
    #     else:
    #         # If creating a new StockOrder, simply decrement the stock quantity
    #         new_quantity = self.quantity

    #     if new_quantity > self.stock.qty:
    #         raise ValidationError("Ordered quantity cannot exceed available stock.")

    #     self.stock.qty -= new_quantity
    #     self.stock.save()

    #     super().save(*args, **kwargs)

    #     # Update the total amount in the order table
    #     self.order.total_amount = sum(
    #         stock_order.quantity * stock_order.stock.price_per_unit
    #         for stock_order in self.order.stock_orders.all()
    #     )
    #     self.order.save()

    # def delete(self, *args, **kwargs):
    #     # Restore the stock quantity when a StockOrder is deleted
    #     self.stock.qty += self.quantity
    #     self.stock.save()
    #     super().delete(*args, **kwargs)

    def __str__(self):
        return f"StockOrder {self.id} - Order {self.order.id} - Stock {self.stock.id}"


class InventoryDiscrepancy(models.Model):

    discrepancy_type = models.CharField(
        max_length=25,
        choices=DiscrepancyTypeEnum.choices(),
        help_text="Type of discrepancy (e.g., lost, expired, recovered, etc.).",
    )
    distribution = models.ForeignKey(
        Distribution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_discrepancies",
        help_text="Distribution related to the product of the stock (if applicable).",
    )

    stock = models.ForeignKey(
        Stock,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="discrepancies",
        help_text="Stock item related to the discrepancy (if applicable).",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount recovered in cash, if applicable.",
    )
    quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quantity of stock affected by the discrepancy (if applicable).",
    )
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_discrepancies",
        help_text="User who recorded the discrepancy.",
    )
    description = models.TextField(
        null=True, blank=True, help_text="Additional details about the discrepancy."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if (
            self.discrepancy_type == DiscrepancyTypeEnum.RECOVERED_CASH_APPROVAL.value
            or self.discrepancy_type == DiscrepancyTypeEnum.HOME_EXPENSE.value
        ) and (
            self.amount is None
            or self.amount <= 0
            or not self.distribution
            or self.quantity is not None
            or self.stock is not None
        ):
            raise ValidationError(
                "Amount and distribution must be provided for cash recovery and stock & quatity should not be provided."
            )
        if (
            self.discrepancy_type == DiscrepancyTypeEnum.RETURNED_SHORT_EXPIRY.value
            and (
                self.amount
                or not self.distribution
                or not self.quantity
                or self.quantity <= 0
                or self.stock is None
            )
        ):
            raise ValidationError(
                "Stock, quantity, and distribution must be provided for returned short expiry, and amount should not be provided."
            )

        elif self.discrepancy_type in [
            DiscrepancyTypeEnum.FREE.value,
            DiscrepancyTypeEnum.EXPIRED.value,
            DiscrepancyTypeEnum.LOST.value,
            DiscrepancyTypeEnum.DAMAGED.value,
        ] and (not self.stock or not self.quantity or self.amount or self.distribution):
            raise ValidationError(
                "Stock and quantity must be provided for 'free', 'expired', 'lost', or 'damaged' discrepancies, and amount and distribution should not be provided."
            )
        elif self.discrepancy_type == DiscrepancyTypeEnum.DONATED.value:
            if (self.amount and (self.stock or self.quantity)) or (
                not self.amount and (not self.stock or not self.quantity)
            ):
                raise ValidationError(
                    "Either provide stock and quantity, or amount, but not both for donation."
                )

        if self.quantity and self.stock and self.quantity > self.stock.qty:
            raise ValidationError("Quantity cannot exceed available stock.")

    def save(self, *args, **kwargs):
        self.full_clean()
        if (
            self.discrepancy_type
            in [
                DiscrepancyTypeEnum.FREE.value,
                DiscrepancyTypeEnum.EXPIRED.value,
                DiscrepancyTypeEnum.LOST.value,
                DiscrepancyTypeEnum.DAMAGED.value,
                DiscrepancyTypeEnum.RETURNED_SHORT_EXPIRY.value,
                DiscrepancyTypeEnum.DONATED.value,
            ]
            and not self.amount
        ):
            self.amount = self.quantity * self.stock.purchase_price
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Inventory Discrepancies"

    def __str__(self):
        return f"{self.discrepancy_type.capitalize()} - {self.created_at.date()} - {self.amount or self.quantity or 'N/A'}"


class CustomerTransaction(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_transactions",
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices(),
        help_text="Type of transaction (e.g., payment received, payment made).",
    )
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        party = self.order.customer or self.distribution
        party_name = party.name if party else "Unknown Party"
        return f"{self.transaction_type.title()} - {self.amount} - {party_name} ({self.created_at.date()})"

    def save(self, *args, **kwargs):
        if not self.order and not self.distribution:
            raise ValidationError(
                "Transaction must be associated with either a order or a distribution."
            )
        if self.order and self.distribution:
            raise ValidationError(
                "Transaction can only be associated with either a order or a distribution, not both."
            )

        if self.order:
            if self.transaction_type == TransactionType.PAYMENT_RECEIVED.value:
                self.order.customer.balance += self.amount
            elif self.transaction_type == TransactionType.PAYMENT_MADE.value:
                self.order.customer.balance -= self.amount
            self.order.customer.save()

        if self.distribution:
            if self.transaction_type == TransactionType.PAYMENT_RECEIVED.value:
                self.distribution.balance += self.amount
            elif self.transaction_type == TransactionType.PAYMENT_MADE.value:
                self.distribution.balance -= self.amount
            self.distribution.save()

        super().save(*args, **kwargs)


class DistributionTransaction(models.Model):

    order = models.ForeignKey(  # TODO convert to stock with many to many
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="distribution_transactions",
    )
    distribution = models.ForeignKey(
        Distribution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices(),
        help_text="Type of transaction (e.g., payment received, payment made).",
    )
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        party = self.order.customer or self.distribution
        party_name = party.name if party else "Unknown Party"
        return f"{self.transaction_type.title()} - {self.amount} - {party_name} ({self.created_at.date()})"

    def save(self, *args, **kwargs):
        if not self.order and not self.distribution:
            raise ValidationError(
                "Transaction must be associated with either a order or a distribution."
            )
        if self.order and self.distribution:
            raise ValidationError(
                "Transaction can only be associated with either a order or a distribution, not both."
            )

        if self.order:
            if self.transaction_type == TransactionType.PAYMENT_RECEIVED.value:
                self.order.customer.balance += self.amount
            elif self.transaction_type == TransactionType.PAYMENT_MADE.value:
                self.order.customer.balance -= self.amount
            self.order.customer.save()

        if self.distribution:
            if self.transaction_type == TransactionType.PAYMENT_RECEIVED.value:
                self.distribution.balance += self.amount
            elif self.transaction_type == TransactionType.PAYMENT_MADE.value:
                self.distribution.balance -= self.amount
            self.distribution.save()

        super().save(*args, **kwargs)
