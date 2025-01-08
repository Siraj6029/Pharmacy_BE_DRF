from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DistributionViewSet, FormulaViewSet, CustomerViewSet

router = DefaultRouter()
router.register("company", CompanyViewSet)
router.register("distribution", DistributionViewSet)
router.register("formula", FormulaViewSet)
router.register("customer", CustomerViewSet)

urlpatterns = [path("", include(router.urls))]
