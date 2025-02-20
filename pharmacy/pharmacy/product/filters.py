import django_filters
from .models import Product, Stock
from django.utils import timezone
from django.db.models import QuerySet, F, Case, When, Value, BooleanField, Q, F, Sum
from datetime import timedelta
from pharmacy.utills.enums import ExpiryEnum, LowQuantityEnums, LowQuantityThresholEnum
from django.db.models.functions import Coalesce
from datetime import date, datetime


class ProductFilter(django_filters.FilterSet):
    expiration = django_filters.CharFilter(method="filter_expiration")
    company_ids = django_filters.CharFilter(method="filter_by_company_ids")
    distribution_ids = django_filters.CharFilter(method="filter_by_distribution_ids")
    formula_ids = django_filters.CharFilter(method="filter_by_formula_ids")
    low_qty = django_filters.CharFilter(method="filter_low_qty")
    showInactive = django_filters.BooleanFilter(method="filter_show_inactive")

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

    def filter_show_inactive(self, queryset: QuerySet, name: str, value: bool):
        if value:
            return queryset
        return queryset.filter(avg_qty__gt=0)


class StockFilter(django_filters.FilterSet):
    product_type = django_filters.CharFilter(
        field_name="product__product_type", lookup_expr="exact"
    )
    bought_from = django_filters.CharFilter(
        field_name="bought_from__id", lookup_expr="exact"
    )
    product_name = django_filters.CharFilter(method="product_name_filter")
    start_date = django_filters.CharFilter(method="filter_start_date")
    end_date = django_filters.CharFilter(method="filter_end_date")
    expiration = django_filters.CharFilter(method="filter_expiration")
    showInactive = django_filters.BooleanFilter(method="filter_show_inactive")

    def filter_start_date(self, queryset, name, value):
        try:
            naive_datetime = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            aware_datetime = timezone.make_aware(
                naive_datetime, timezone.get_default_timezone()
            )
            return queryset.filter(entry_date__gte=aware_datetime)
        except ValueError:
            return queryset

    def filter_end_date(self, queryset, name, value):
        try:
            naive_datetime = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            aware_datetime = timezone.make_aware(
                naive_datetime, timezone.get_default_timezone()
            )
            return queryset.filter(entry_date__lte=aware_datetime)
        except ValueError:
            return queryset

    def filter_expiration(self, queryset: QuerySet, name: str, value: str):
        if value not in ExpiryEnum.list_all_values():
            raise ValueError(
                f"Invalid expiration value. allowed values are: {ExpiryEnum.list_all_values()}"
            )
        today = timezone.now().date()
        six_months_later = today + timedelta(days=180)

        queryset = queryset.annotate(
            is_expired=Case(
                When(expiry_date__lt=Value(today), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            is_short_expired=Case(
                When(
                    expiry_date__gte=Value(today),
                    expiry_date__lt=Value(six_months_later),
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

    def product_name_filter(self, queryset: QuerySet, name, value):
        if value:
            return queryset.filter(product__name__icontains=value)
        return queryset

    def filter_show_inactive(self, queryset: QuerySet, name: str, value: bool):
        if value:
            return queryset
        return queryset.filter(qty__gt=0)

    class Meta:
        model = Stock
        fields = {
            "id": ["exact"],
            "barcode": ["exact"],
            "entry_date": ["exact", "gte", "lte"],
            "product__name": ["icontains"],
            "product__product_type": ["exact"],
            "bought_from__id": ["exact"],
        }
