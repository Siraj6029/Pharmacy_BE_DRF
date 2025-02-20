# from rest_framework.viewsets import generics
from rest_framework.generics import ListAPIView
from .models import Product, Stock
from .serializers import (
    ProductDetailSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    StockCRUDSerializer,
)
from .filters import ProductFilter, StockFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from rest_framework import filters, status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.db import transaction
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Order, Product
from .paginations import CustomPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from pharmacy.utills.enums import OrderStatusEnum
from pharmacy.config import ONLY_SUPER_USER_CANCEL_ORDER


class ProductViewSet(ModelViewSet):
    queryset = (
        Product.objects.select_related(
            "company", "distribution", "formula"
        )  # changed from ProductProxy
        .prefetch_related(Prefetch("stocks", queryset=Stock.objects.filter(qty__gt=0)))
        .distinct()
    )
    # queryset = ProductProxy.objects.all()
    serializer_class = ProductDetailSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = ProductFilter
    ordering_fields = ["name", "total_qty", "product_type"]
    ordering = ["name"]
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class StockViewSet(ModelViewSet):
    queryset = Stock.objects.select_related("product").all()
    serializer_class = StockCRUDSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = StockFilter
    filterset_fields = ["product", "barcode"]
    ordering_fields = ["entry_date", "product", "expiry_date"]
    ordering = ["-entry_date"]
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            order = serializer.save()
        return Response(
            OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED
        )

    @transaction.atomic()
    def patch(self, request: Request, pk, *args, **kwargs):
        if "status" not in request.data or len(request.data) > 1:
            return Response(
                {"error": "Only 'status' field can be updated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = request.data["status"]
        if new_status not in OrderStatusEnum.list_all_values():
            return Response(
                f"Only {OrderStatusEnum.list_all_values()} are allowed",
                status=status.HTTP_403_FORBIDDEN,
            )

        allowed_transitions = {
            OrderStatusEnum.PENDING.value: [OrderStatusEnum.COMPLETED.value],
            OrderStatusEnum.COMPLETED.value: [OrderStatusEnum.CANCELLED.value],
            OrderStatusEnum.CANCELLED.value: [],
        }

        instance = get_object_or_404(Order, pk=pk)

        if instance.status not in allowed_transitions:
            return Response(
                {"error": "Invalid current status."}, status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in allowed_transitions[instance.status]:
            return Response(
                {
                    "error": f"Cannot change status from {instance.status} to {new_status}."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            instance.status == OrderStatusEnum.PENDING.value
            and new_status == OrderStatusEnum.COMPLETED.value
        ):
            for stock_order in instance.stock_orders.all():
                stock_order.stock.qty -= stock_order.quantity
                stock_order.stock.save()
        elif (
            instance.status == OrderStatusEnum.COMPLETED.value
            and new_status == OrderStatusEnum.CANCELLED.value
        ):
            if ONLY_SUPER_USER_CANCEL_ORDER and not request.user.is_superuser:
                return Response(
                    "Only Superuser can cancel the order",
                    status=status.HTTP_403_FORBIDDEN,
                )

            for stock_order in instance.stock_orders.all():
                stock_order.stock.qty += stock_order.quantity
                stock_order.stock.save()

        serializer = OrderDetailSerializer(
            instance, data={"status": request.data["status"]}, partial=True
        )  # Partial update

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
