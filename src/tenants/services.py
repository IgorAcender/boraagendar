from dataclasses import dataclass
from typing import Iterable, Optional

from django.core.exceptions import PermissionDenied

from accounts.models import User

from .models import Tenant, TenantMembership


class TenantSelectionRequired(PermissionDenied):
    """Excecao usada quando o usuario precisa escolher um tenant explicitamente."""


@dataclass
class MembershipContext:
    tenant: Tenant
    membership: Optional[TenantMembership]


def _active_memberships_queryset(user: User):
    return (
        TenantMembership.objects.filter(user=user, is_active=True, tenant__is_active=True)
        .select_related("tenant")
        .order_by("tenant__name")
    )


def get_membership(user: User, tenant_id: Optional[int] = None) -> Optional[TenantMembership]:
    if not user.is_authenticated:
        return None

    qs = _active_memberships_queryset(user)

    if tenant_id is not None:
        return qs.filter(tenant_id=tenant_id).first()

    memberships = list(qs[:2])
    if not memberships:
        return None
    if len(memberships) > 1:
        return None
    return memberships[0]


def ensure_membership(
    user: User,
    allowed_roles: Optional[Iterable[str]] = None,
    tenant_id: Optional[int] = None,
) -> TenantMembership:
    if not user.is_authenticated:
        raise PermissionDenied("Usuario sem acesso a empresa.")

    if user.is_superuser:
        tenant = _resolve_superuser_tenant(tenant_id)
        return TenantMembership(tenant=tenant, user=user, role=TenantMembership.Role.OWNER, is_active=True)

    qs = _active_memberships_queryset(user)

    if tenant_id is not None:
        membership = qs.filter(tenant_id=tenant_id).first()
        if membership is None:
            raise PermissionDenied("Usuario sem acesso a empresa selecionada.")
    else:
        memberships = list(qs[:2])
        if not memberships:
            raise PermissionDenied("Usuario sem acesso a empresa.")
        if len(memberships) > 1:
            raise TenantSelectionRequired("Selecione uma empresa para continuar.")
        membership = memberships[0]

    if allowed_roles and membership.role not in allowed_roles:
        raise PermissionDenied("Voce nao possui permissao para esta acao.")

    return membership


def ensure_membership_for_request(
    request,
    allowed_roles: Optional[Iterable[str]] = None,
) -> TenantMembership:
    tenant_id = request.session.get("active_tenant_id")
    try:
        membership = ensure_membership(request.user, allowed_roles=allowed_roles, tenant_id=tenant_id)
    except TenantSelectionRequired:
        raise
    except PermissionDenied:
        if tenant_id is None:
            raise
        request.session.pop("active_tenant_id", None)
        membership = ensure_membership(request.user, allowed_roles=allowed_roles)
    request.session["active_tenant_id"] = membership.tenant_id
    return membership


def _resolve_superuser_tenant(tenant_id: Optional[int]) -> Tenant:
    tenants = Tenant.objects.filter(is_active=True).order_by("name")
    if tenant_id is not None:
        tenant = tenants.filter(id=tenant_id).first()
        if tenant is None:
            raise PermissionDenied("Empresa selecionada nao esta disponivel.")
        return tenant

    tenant = tenants.first()
    if tenant is None:
        raise PermissionDenied("Nenhuma empresa ativa cadastrada.")
    return tenant
