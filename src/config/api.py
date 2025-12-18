from django.http import JsonResponse
from scheduling.models import Booking
from scheduling.services.tenant_context import get_tenant_for_request


def dashboard_stats(request):
    """Return basic booking stats for the current tenant.

    If tenant selection fails, return mock/empty values (200) so frontend can
    gracefully fallback.
    """
    try:
        tenant = get_tenant_for_request(request)
    except Exception:
        # Tenant not selected or misconfigured - return default values
        return JsonResponse({
            "total": 0,
            "confirmed": 0,
            "pending": 0,
            "cancelled": 0,
        })

    qs = Booking.objects.filter(tenant=tenant)
    total = qs.count()
    confirmed = qs.filter(status=Booking.Status.CONFIRMED).count()
    pending = qs.filter(status=Booking.Status.PENDING).count()
    cancelled = qs.filter(status=Booking.Status.CANCELLED).count()

    return JsonResponse(
        {
            "total": total,
            "confirmed": confirmed,
            "pending": pending,
            "cancelled": cancelled,
        }
    )
