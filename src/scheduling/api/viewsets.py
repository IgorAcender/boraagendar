from rest_framework import permissions, viewsets

from scheduling.api.serializers import BookingSerializer, ProfessionalSerializer, ServiceSerializer
from scheduling.models import Booking, Professional, Service
from scheduling.services.tenant_context import get_tenant_for_request


class TenantScopedMixin:
    def get_tenant(self):
        return get_tenant_for_request(self.request)

    def apply_tenant_filter(self, queryset):
        tenant = self.get_tenant()
        return queryset.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        serializer.save(tenant=tenant, created_by=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["tenant"] = self.get_tenant()
        return context


class ServiceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.apply_tenant_filter(Service.objects.all())


class ProfessionalViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    serializer_class = ProfessionalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.apply_tenant_filter(Professional.objects.all())


class BookingViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.apply_tenant_filter(Booking.objects.select_related("service", "professional"))
