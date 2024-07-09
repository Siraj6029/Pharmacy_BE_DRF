from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DistributionViewSet, FormulaViewSet

router = DefaultRouter()
router.register("company", CompanyViewSet)
router.register("distribution", DistributionViewSet)
router.register("formula", FormulaViewSet)

urlpatterns = [path("", include(router.urls))]
