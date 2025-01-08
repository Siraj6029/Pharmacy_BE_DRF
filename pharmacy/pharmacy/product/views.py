# from rest_framework.viewsets import generics
from rest_framework.generics import ListAPIView
from .models import Product, Stock, ProductProxy
from .serializers import (
    ProductDetailSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
)
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from rest_framework import filters, status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.db import transaction
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Order, Product


class ProductViewSet(ModelViewSet):
    queryset = ProductProxy.objects.select_related(
        "company", "distribution", "formula"
    ).prefetch_related(Prefetch("stocks", queryset=Stock.objects.filter(qty__gt=0)))
    # queryset = ProductProxy.objects.all()
    serializer_class = ProductDetailSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = ProductFilter
    ordering_fields = ["name", "total_qty", "product_type"]
    ordering = ["name"]


class OrderCreateAPIView(APIView):
    @transaction.atomic
    def post(self, request: Request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order: Order = serializer.save()
            receipt_serializer = OrderDetailSerializer(order)
            return Response(receipt_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
