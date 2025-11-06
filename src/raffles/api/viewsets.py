from __future__ import annotations

from rest_framework import permissions, response, status, viewsets
from rest_framework.decorators import action

from raffles.api.serializers import (
    RaffleOrderSerializer,
    RaffleSerializer,
    ReferralInvitationSerializer,
    ReferralRedeemSerializer,
)
from raffles.models import Raffle, RaffleOrder, ReferralInvitation
from scheduling.services.tenant_context import get_tenant_for_request


class TenantScopedMixin:
    permission_classes = [permissions.IsAuthenticated]

    def get_tenant(self):
        return get_tenant_for_request(self.request)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if "tenant" not in context:
            context["tenant"] = self.get_tenant()
        return context


class RaffleViewSet(TenantScopedMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = RaffleSerializer

    def get_queryset(self):
        tenant = self.get_tenant()
        return Raffle.objects.filter(tenant=tenant, status=Raffle.Status.ACTIVE)


class RaffleOrderViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    serializer_class = RaffleOrderSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        tenant = self.get_tenant()
        return (
            RaffleOrder.objects.filter(user=self.request.user, raffle__tenant=tenant)
            .select_related("raffle")
            .prefetch_related("ticket_allocations")
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        order = self.get_object()
        if order.is_paid:
            return response.Response(
                {
                    "detail": "Pedido já marcado como pago.",
                    "numbers": sorted(order.ticket_allocations.values_list("number", flat=True)),
                },
                status=status.HTTP_200_OK,
            )
        order.mark_paid()
        return response.Response(
            {
                "detail": "Pedido marcado como pago.",
                "numbers": sorted(order.ticket_allocations.values_list("number", flat=True)),
            },
            status=status.HTTP_200_OK,
        )


class ReferralInvitationViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    serializer_class = ReferralInvitationSerializer
    lookup_field = "code"
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_permissions(self):
        if self.action in {"visit", "redeem"}:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        base = ReferralInvitation.objects.select_related("raffle", "inviter", "invitee")
        if self.action in {"retrieve", "visit", "redeem"}:
            return base
        tenant = self.get_tenant()
        return base.filter(inviter=self.request.user, raffle__tenant=tenant)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], url_path="visit")
    def visit(self, request, *args, **kwargs):
        referral = self.get_object()
        referral.register_visit()
        return response.Response(
            {
                "status": referral.status,
                "clicks": referral.clicks,
                "last_clicked_at": referral.last_clicked_at,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="redeem")
    def redeem(self, request, *args, **kwargs):
        referral = self.get_object()
        serializer = ReferralRedeemSerializer(
            data=request.data,
            context={"request": request, "referral": referral},
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=status.HTTP_200_OK)

