from typing import Optional

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from tenants.models import Tenant
from tenants.services import TenantSelectionRequired, ensure_membership_for_request


def get_active_tenant_for_request(request: HttpRequest) -> Optional[Tenant]:
    if not request.user.is_authenticated:
        return None
    try:
        membership = ensure_membership_for_request(request)
    except TenantSelectionRequired:
        raise
    except PermissionDenied:
        return None
    return membership.tenant
