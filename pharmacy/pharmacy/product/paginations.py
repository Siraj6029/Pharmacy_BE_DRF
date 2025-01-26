from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ProductsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "perPage"
    page_query_param = "page"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        # Set default page to 1 if not provided
        if not request.query_params.get(self.page_query_param):
            request.query_params._mutable = True
            request.query_params[self.page_query_param] = "1"
            request.query_params._mutable = False

        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response(
            {
                "total_count": self.page.paginator.count,
                "current_page": self.page.number,
                "has_next_page": self.page.has_next(),
                "results": data,
            }
        )
