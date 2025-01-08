from rest_framework import serializers
from .models import Product, Stock, ProductProxy, StockOrder, Order
from pharmacy.core.serializers import (
    CompanySerializer,
    DistributionSerializer,
    FormulaSerializer,
)
from django.db.models import Sum
from pharmacy.core.serializers import CustomerSerializer


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class ProductDetailSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    distribution = DistributionSerializer(read_only=True)
    formula = FormulaSerializer(read_only=True)
    stocks = StockSerializer(many=True)
    total_qty = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductProxy
        fields = "__all__"


class StockOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockOrder
        fields = ["stock", "quantity"]


class StockOrderSerializer(serializers.ModelSerializer):
    product = serializers.ReadOnlyField(source="stock.product.name")
    # price_per_unit = serializers.ReadOnlyField(source="stock.product.price_per_unit")
    price_per_unit = serializers.ReadOnlyField(source="stock.price_per_unit")

    class Meta:
        model = StockOrder
        fields = "__all__"


class OrderCreateSerializer(serializers.ModelSerializer):
    stock_order = StockOrderCreateSerializer(many=True)
    total_amount = serializers.DecimalField(
        max_digits=99999, decimal_places=2, read_only=True
    )
    total_after_disc = serializers.DecimalField(
        max_digits=99999, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["id"]

    def create(self, validated_data: dict):
        stock_order_data = validated_data.pop("stock_order")
        order = Order.objects.create(**validated_data)
        total_amount = 0
        for stock_order in stock_order_data:
            stock: Stock = stock_order["stock"]
            quantity: int = stock_order["quantity"]
            if stock.qty < quantity:
                raise serializers.ValidationError(
                    f"Insufficient quantity for stock: {stock.product.name}, Available: {stock.qty}"
                )
            StockOrder.objects.create(stock=stock, quantity=quantity, order=order)

            total_amount += stock.price_per_unit * quantity

            stock.qty -= quantity
            stock.save()

        if order.discount:
            total_after_disc = total_amount * ((100 - order.discount) / 100)
        else:
            total_after_disc = total_amount
        order.total_amount = total_amount
        order.total_after_disc = total_after_disc
        order.save()
        return order


class OrderDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    stock_orders = StockOrderSerializer(many=True, source="stockorder_set")

    class Meta:
        model = Order
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"  # Alternatively, you can list specific fields
