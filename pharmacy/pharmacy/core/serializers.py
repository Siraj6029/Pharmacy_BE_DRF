from rest_framework import serializers
from .models import Company, Distribution, Formula, Customer
from rest_framework.exceptions import ValidationError


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class DistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution
        fields = "__all__"


class FormulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formula
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
