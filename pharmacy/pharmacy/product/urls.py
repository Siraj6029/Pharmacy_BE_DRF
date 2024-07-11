from django.urls import path, include

# from rest_framework.routers import DefaultRouter
from .views import ProductDetailView


# router = DefaultRouter()
# router.register("productDetails", ProductDetailView, basename="product_detail")

# urlpatterns = [path("", include(router.urls))]

urlpatterns = [
    path("productDetails/", ProductDetailView.as_view(), name="product_list")
]
