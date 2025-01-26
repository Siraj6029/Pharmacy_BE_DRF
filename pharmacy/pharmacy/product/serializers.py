from rest_framework import serializers
from .models import Product, Stock, StockOrder, Order
from pharmacy.core.models import Company, Distribution, Formula
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
        read_only_fields = ["id", "stocks"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["bought_from"] = instance.bought_from.name
        return data


class ProductDetailSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), source="company", write_only=True
    )
    distribution_id = serializers.PrimaryKeyRelatedField(
        queryset=Distribution.objects.all(),
        source="distribution",
        write_only=True,
        required=False,
        allow_null=True,
    )
    formula_id = serializers.PrimaryKeyRelatedField(
        queryset=Formula.objects.all(), source="formula", write_only=True
    )

    company = CompanySerializer(read_only=True)
    distribution = DistributionSerializer(read_only=True)
    formula = FormulaSerializer(read_only=True)
    stocks = StockSerializer(many=True, required=False, read_only=True)
    total_qty = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product  # changed from ProductProxy
        fields = "__all__"
        extra_kwargs = {
            # "password": {"write_only": True, "required": False},
            "stocks": {"read_only": True, "required": False},
            "distribution_id": {"required": False},
            # "username": {"required": True},
        }


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
