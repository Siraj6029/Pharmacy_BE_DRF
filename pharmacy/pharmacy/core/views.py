from rest_framework import viewsets
from .models import Company, Distribution, Formula, Customer
from .serializers import (
    CompanySerializer,
    DistributionSerializer,
    FormulaSerializer,
    CustomerSerializer,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_permissions(self):
        if self.action in ["destroy"]:
            # if self.action in ["update", "partial_update", "destroy"]:
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
