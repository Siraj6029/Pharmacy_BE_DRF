from django.contrib import admin
from .models import Product, Stock, StockOrder, Order

admin.site.register((Product, Stock))


class StockOrderInline(admin.TabularInline):
    model = StockOrder
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [StockOrderInline]


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         qs = qs.prefetch_related(
#             "stockorder_set__stock"
#         )  # Use prefetch_related for efficient querying
#         return qs
