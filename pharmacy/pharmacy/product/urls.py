from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderAPIView, StockViewSet


router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("stocks", StockViewSet, basename="stock")

urlpatterns = [
    path("orders/", OrderAPIView.as_view(), name="orders"),
    path("orders/<int:pk>/", OrderAPIView.as_view(), name="order-status-update"),
] + router.urls
