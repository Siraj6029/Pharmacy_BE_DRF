import django_filters
from .models import Product
from django.utils import timezone
from django.db.models import QuerySet, F, Case, When, Value, BooleanField, Q, F, Sum
from datetime import timedelta
from pharmacy.utills.enums import ExpiryEnum, LowQuantityEnums, LowQuantityThresholEnum
from django.db.models.functions import Coalesce
from datetime import date


class ProductFilter(django_filters.FilterSet):
    expiration = django_filters.CharFilter(method="filter_expiration")
    company_ids = django_filters.CharFilter(method="filter_by_company_ids")
    distribution_ids = django_filters.CharFilter(method="filter_by_distribution_ids")
    formula_ids = django_filters.CharFilter(method="filter_by_formula_ids")
    low_qty = django_filters.CharFilter(method="filter_low_qty")

    class Meta:
        model = Product  # changed from ProductProxy
        fields = {
            "id": ["exact"],
            "name": ["exact", "icontains"],
            "product_type": ["exact"],
            # "company__name": ["exact", "icontains"],
            # "distribution__name": ["exact", "icontains"],
            # "formula__name": ["exact", "icontains"],
        }

    def filter_by_company_ids(self, queryset: QuerySet, name: str, value: str):
        company_ids = value.split(",")
        if not all(c_id.isdigit() for c_id in company_ids):
            raise ValueError("All company IDs must be numeric.")
        return queryset.filter(company__id__in=company_ids)

    def filter_by_distribution_ids(self, queryset: QuerySet, name: str, value: str):
        distribution_ids = value.split(",")
        if not all(c_id.isdigit() for c_id in distribution_ids):
            raise ValueError("All company IDs must be numeric.")
        return queryset.filter(distribution__id__in=distribution_ids)

    def filter_by_formula_ids(self, queryset: QuerySet, name: str, value: str):
        print(value)
        formula_ids = value.split(",")
        if not all(c_id.isdigit() for c_id in formula_ids):
            raise ValueError("All company IDs must be numeric.")
        return queryset.filter(formula__id__in=formula_ids)

    def filter_expiration(self, queryset: QuerySet, name: str, value: str):
        if value not in ExpiryEnum.list_all_values():
            raise ValueError(
                f"Invalid expiration value. allowed values are: {ExpiryEnum.list_all_values()}"
            )
        today = timezone.now().date()
        six_months_later = today + timedelta(days=180)

        queryset = queryset.annotate(
            is_expired=Case(
                When(stocks__expiry_date__lt=Value(today), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            is_short_expired=Case(
                When(
                    stocks__expiry_date__gte=Value(today),
                    stocks__expiry_date__lt=Value(six_months_later),
                    then=(Value(True)),
                ),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )

        if value == ExpiryEnum.EXPIRED.value:
            return queryset.filter(is_expired=True).distinct()
        elif value == ExpiryEnum.SHORT_EXPIRED.value:
            return queryset.filter(is_short_expired=True).distinct()
        elif value == ExpiryEnum.EXPIRED_AND_SHORT_EXPIRED.value:
            return queryset.filter(
                Q(is_expired=True) | Q(is_short_expired=True)
            ).distinct()

    def filter_low_qty(self, queryset: QuerySet, name: str, value: str):
        if value not in LowQuantityEnums.list_all_values():
            raise ValueError(
                f"Invalid low_qty value. Allowed values are: {LowQuantityEnums.list_all_values()}"
            )

        # Get today's date to filter out expired stocks
        today = date.today()

        # Annotate total quantity, excluding expired stocks
        queryset = queryset.annotate(
            total_quantity=Coalesce(
                Sum(
                    "stocks__qty", filter=Q(stocks__expiry_date__gte=today)
                ),  # Only include non-expired stocks
                Value(0),
            )
        )

        if value == LowQuantityEnums.VERY_LOW.value:
            return queryset.filter(
                total_quantity__lt=F("avg_qty")
                * LowQuantityThresholEnum.VERY_LOW_LIMIT.value
            ).distinct()
        elif value == LowQuantityEnums.LOW.value:
            return queryset.filter(
                total_quantity__lt=F("avg_qty")
                * LowQuantityThresholEnum.LOW_LIMIT.value
            ).distinct()

        return queryset
