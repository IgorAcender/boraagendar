from django.http import JsonResponse
from scheduling.models import Booking
from scheduling.services.tenant_context import get_tenant_for_request
from django.utils import timezone
from datetime import timedelta


def dashboard_stats_series(request):
    """Return time series (daily counts) for bookings in the current tenant.

    Response format:
    {
      "series": [
         {"date": "2025-12-01", "count": 3},
         ...
      ]
    }
    """
    try:
        tenant = get_tenant_for_request(request)
    except Exception:
        # Tenant not selected - return empty series
        return JsonResponse({"series": []})

    # last N days (including today)
    days = 30
    today = timezone.now().date()
    start_date = today - timedelta(days=days - 1)

    qs = Booking.objects.filter(tenant=tenant, scheduled_for__date__gte=start_date)

    # Build a map date->count
    counts = {}
    for b in qs:
        d = b.scheduled_for.date()
        counts[d] = counts.get(d, 0) + 1

    series = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        series.append({"date": d.isoformat(), "count": counts.get(d, 0)})

    return JsonResponse({"series": series})


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
