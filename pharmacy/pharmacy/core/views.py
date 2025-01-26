from rest_framework import viewsets, generics
from .models import Company, Distribution, Formula, Customer
from .serializers import (
    CompanySerializer,
    DistributionSerializer,
    FormulaSerializer,
    CustomerSerializer,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView, Response, status
from rest_framework.exceptions import NotFound


# class CompanyViewSet(viewsets.ModelViewSet):
#     queryset = Company.objects.all()
#     serializer_class = CompanySerializer

#     def get_permissions(self):
#         if self.action in ["destroy"]:
#             # if self.action in ["update", "partial_update", "destroy"]:
#             permission_classes = [IsAuthenticated, IsAdminUser]
#         else:
#             permission_classes = [IsAuthenticated]
#         return [permission() for permission in permission_classes]


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_queryset(self):
        """
        Optionally filter companies by distribution_id.
        """
        queryset = super().get_queryset()

        # Check if 'distribution_id' is in the query parameters
        distribution_id = self.request.query_params.get("distribution_id")
        if distribution_id:
            try:
                distribution_id = int(distribution_id)
            except ValueError:
                raise NotFound("Invalid distribution ID.")

            # Ensure the distribution exists
            if not Distribution.objects.filter(id=distribution_id).exists():
                raise NotFound("Distribution not found.")

            # Filter companies associated with the given distribution_id
            queryset = (
                queryset.filter(products__distribution_id=distribution_id)
                .distinct()
                .prefetch_related("products")
            )

        return queryset

    def get_permissions(self):
        if self.action in ["destroy"]:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class DistributionViewSet(viewsets.ModelViewSet):
    queryset = Distribution.objects.all()
    serializer_class = DistributionSerializer

    def get_permissions(self):
        if self.action in ["destroy"]:
            # if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class FormulaViewSet(viewsets.ModelViewSet):
    queryset = Formula.objects.all()
    serializer_class = FormulaSerializer

    def get_permissions(self):
        if self.action in ["destroy"]:
            # if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.action in ["destroy"]:
            # if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


# class CompaniesByDistributionIdAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, distribution_id):
#         # Check if the distribution exists
#         if not Distribution.objects.filter(id=distribution_id).exists():
#             return Response(
#                 {"error": "Distribution not found"}, status=status.HTTP_404_NOT_FOUND
#             )

#         # Get distinct companies associated with the given distribution_id
#         companies = (
#             Company.objects.filter(products__distribution_id=distribution_id)
#             .distinct()
#             .prefetch_related("products")
#         )

#         # Serialize and return the response
#         serializer = CompanySerializer(companies, many=True)
#         return Response(serializer.data)
