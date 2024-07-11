# from rest_framework.viewsets import generics
from rest_framework.generics import ListAPIView
from .models import Product, Stock, ProductProxy
from .serializers import ProductDetailSerializer
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from rest_framework import filters


class ProductDetailView(ListAPIView):
    queryset = ProductProxy.objects.select_related(
        "company", "distribution", "formula"
    ).prefetch_related(Prefetch("stocks", queryset=Stock.objects.filter(qty__gt=0)))
    # queryset = ProductProxy.objects.all()
    serializer_class = ProductDetailSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = ProductFilter
