import django_filters
from .models import Product, ProductProxy
from django.utils import timezone
from django.db.models import QuerySet
from datetime import timedelta


class ProductFilter(django_filters.FilterSet):
    expiration = django_filters.CharFilter(method="filter_expiration")
    company_ids = django_filters.CharFilter(method="filter_by_company_ids")

    class Meta:
        model = ProductProxy
        fields = {
            "id": ["exact"],
            "name": ["exact", "icontains"],
            "product_type": ["exact"],
            "company__name": ["exact", "icontains"],
            "distribution__name": ["exact", "icontains"],
            "formula__name": ["exact", "icontains"],
        }

    def filter_by_company_ids(self, queryset: QuerySet, name: str, value: str):
        company_ids = value.split(",")
        return queryset.filter(company__id__in=company_ids)

    def filter_expiration(self, queryset: QuerySet, name: str, value: bool):
        today = timezone.now().date()
        if value == "expired":
            return queryset.filter(stocks__expiry_date__lt=today).distinct()
        elif value == "shortExpired":
            six_month_later = today + timedelta(days=180)
            return queryset.filter(
                stocks__expiry_date__gt=today, stocks__expiry_date__lt=six_month_later
            ).distinct()
        elif value == "expiredAndShortExpired":
            six_months_later = today + timedelta(days=180)
            return queryset.filter(stocks__expiry_date__lt=six_months_later)
        return queryset
