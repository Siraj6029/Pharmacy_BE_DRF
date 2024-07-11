from rest_framework import serializers
from .models import Product, Stock, ProductProxy
from pharmacy.core.serializers import (
    CompanySerializer,
    DistributionSerializer,
    FormulaSerializer,
)
from django.db.models import Sum


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class ProductDetailSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    distribution = DistributionSerializer(read_only=True)
    formula = FormulaSerializer(read_only=True)
    stocks = StockSerializer(many=True)
    # total_qty = serializers.SerializerMethodField()
    total_qty = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductProxy
        fields = "__all__"

    # def get_total_qty(self, obj: Product):
    #     return obj.stocks.aggregate(total_qty=Sum("qty"))["total_qty"] or 0
