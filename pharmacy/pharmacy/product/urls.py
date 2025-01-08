from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderCreateAPIView


router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")

urlpatterns = [
    path("createOrder/", OrderCreateAPIView.as_view(), name="create_order")
] + router.urls
