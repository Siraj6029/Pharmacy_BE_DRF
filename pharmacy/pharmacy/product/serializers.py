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
from .. import config
from pharmacy.user.serializers import UserSerializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"  # Alternatively, you can list specific fields


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"
        read_only_fields = ["id", "entry_date", "updated_at"]


class StockWithDistName(StockSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["bought_from"] = instance.bought_from.name
        return data


class StockCRUDSerializer(StockSerializer):
    product = ProductSerializer(read_only=True)
    bought_from = DistributionSerializer(read_only=True)


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
    stocks = StockWithDistName(many=True, required=False, read_only=True)
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


class StockOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockOrder
        fields = "__all__"


class CreateStockOrder(serializers.ModelSerializer):
    class Meta:
        model = StockOrder
        fields = "__all__"
        extra_kwargs = {"order": {"required": False}}


# class StockOrderSerializer(serializers.ModelSerializer):
#     product = serializers.ReadOnlyField(source="stock.product.name")
#     # price_per_unit = serializers.ReadOnlyField(source="stock.product.price_per_unit")
#     price_per_unit = serializers.ReadOnlyField(source="stock.price_per_unit")

#     class Meta:
#         model = StockOrder
#         fields = "__all__"


# class OrderCreateSerializer(serializers.ModelSerializer):
#     stock_order = StockOrderSerializer(many=True)

#     class Meta:
#         model = Order
#         fields = ["customer", "total_after_disc", "stock_orders"]

#     def create(self, validated_data: dict):
#         stock_order_data = validated_data.pop("stock_order")
#         order = Order.objects.create(**validated_data)
#         total_amount = 0
#         for stock_order in stock_order_data:
#             stock_id = stock_order["stock"]
#             stock: Stock = Stock.objects.get(id=stock_id)
#             quantity: int = stock_order["quantity"]
#             if stock.qty < quantity:
#                 raise serializers.ValidationError(
#                     f"Insufficient quantity for stock: {stock.product.name}, Available: {stock.qty}"
#                 )
#             stock_order_instance = StockOrder.objects.create(stock=stock, quantity=quantity, order=order)
#             stock_order_instance.save()

#             total_amount += stock.price_per_unit * quantity

#             stock.qty -= quantity
#             stock.save()

#         if order.discount:
#             total_after_disc = total_amount * ((100 - order.discount) / 100)
#         else:
#             total_after_disc = total_amount
#         order.total_amount = total_amount
#         order.total_after_disc = total_after_disc
#         order.save()
#         return order


class OrderCreateSerializer(serializers.ModelSerializer):
    stock_orders = CreateStockOrder(many=True, required=True)  # A list of stock orders
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = ["customer", "total_after_disc", "stock_orders", "created_by"]
        extra_kwargs = {"customer": {"required": True}}

    def create(self, validated_data):
        try:
            stock_orders_data = validated_data.pop("stock_orders")
            total_amount = 0
            # Create the order and save it
            order = Order.objects.create(total_amount=total_amount, **validated_data)

            # Process each stock order and update stock quantities
            for stock_order_data in stock_orders_data:
                stock: Stock = stock_order_data["stock"]
                quantity: int = stock_order_data["quantity"]

                # Ensure there's enough stock
                if quantity > stock.qty or stock.qty <= 0:
                    raise serializers.ValidationError(
                        f"Not enough stock for product: {stock.product.name}"
                    )

                # # Decrement the stock quantity
                # stock.qty -= quantity
                # stock.save()  # Save the updated stock

                # Create StockOrder and save it
                StockOrder.objects.create(order=order, **stock_order_data)

                # Update the total amount for the order
                total_amount += quantity * stock.price_per_unit

            # Validate total_after_disc
            if validated_data.get("total_after_disc"):
                if validated_data["total_after_disc"] > total_amount:
                    raise serializers.ValidationError(
                        "Total after discount cannot exceed total amount"
                    )
                min_after_disc = (
                    total_amount * (100 - config.MAX_DISCOUNT_PERCENTAGE) / 100
                )
                if validated_data["total_after_disc"] < min_after_disc:
                    raise serializers.ValidationError(
                        f"Total after discount cannot be less than {min_after_disc}"
                    )

            # Update the total amount for the order
            order.total_amount = total_amount
            order.save()  # Save the order with the updated total amount

            return order

        except serializers.ValidationError as e:
            raise serializers.ValidationError(
                f"Error processing the order: {str(e.args[0])}"
            )
        except Exception as e:
            raise serializers.ValidationError(f"An unexpected error occured: {str(e)}")


class StockOrderDetailSerializer(serializers.ModelSerializer):
    stock = StockCRUDSerializer()

    class Meta:
        model = StockOrder
        # fields = "__all__"
        exclude = ["order"]


class OrderDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    stock_orders = StockOrderDetailSerializer(many=True)
    created_by = UserSerializer()

    class Meta:
        model = Order
        # fields = "__all__"
        exclude = ["stocks"]
