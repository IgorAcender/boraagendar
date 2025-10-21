from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest

from tenants.models import Tenant
from tenants.services import TenantSelectionRequired

from . import tenant_repository


def get_tenant_for_request(request: HttpRequest) -> Tenant:
    try:
        tenant = tenant_repository.get_active_tenant_for_request(request)
    except TenantSelectionRequired:
        raise
    if tenant is None:
        raise ImproperlyConfigured("Usuario sem empresa associada.")
    return tenant
