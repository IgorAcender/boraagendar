from datetime import date

from django.db.models import Count, Sum

from scheduling.models import Booking, Service
from tenants.models import Tenant


class ReportService:
    def __init__(self, tenant: Tenant):
        self.tenant = tenant

    def occupancy_by_professional(self, start: date, end: date):
        queryset = (
            Booking.objects.filter(tenant=self.tenant, scheduled_for__date__range=(start, end))
            .values("professional__display_name")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        return list(queryset)

    def revenue_by_service(self, start: date, end: date):
        queryset = (
            Booking.objects.filter(tenant=self.tenant, scheduled_for__date__range=(start, end))
            .values("service__name")
            .annotate(amount=Sum("price"))
            .order_by("-amount")
        )
        return list(queryset)

    def no_show_rate(self, start: date, end: date):
        total = Booking.objects.filter(tenant=self.tenant, scheduled_for__date__range=(start, end)).count()
        if not total:
            return 0
        no_show = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__date__range=(start, end),
            status=Booking.Status.NO_SHOW,
        ).count()
        return round(no_show / total * 100, 2)
