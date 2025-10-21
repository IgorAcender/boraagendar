from datetime import datetime
from zoneinfo import ZoneInfo

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from tenants.models import Tenant

from ..forms import AvailabilitySearchForm, BookingForm
from ..models import Booking, Professional, Service
from ..services.availability import AvailabilityService
from ..services.notification_dispatcher import send_booking_confirmation


def booking_start(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    form = AvailabilitySearchForm(tenant=tenant, data=request.GET or None)
    available_slots = []
    selected_service = None
    selected_professional = None
    selected_date = None

    if form.is_valid():
        selected_service = form.cleaned_data["service"]
        selected_professional = form.cleaned_data["professional"]
        selected_date = form.cleaned_data["date"]
        availability_service = AvailabilityService(tenant=tenant)
        available_slots = availability_service.get_available_slots(
            service=selected_service,
            professional=selected_professional,
            target_date=selected_date,
        )

    context = {
        "tenant": tenant,
        "form": form,
        "available_slots": available_slots,
        "selected_service": selected_service,
        "selected_professional": selected_professional,
        "selected_date": selected_date,
    }
    return render(request, "scheduling/public/booking_start.html", context)


def booking_confirm(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    tz = ZoneInfo(tenant.timezone)

    service_id = request.GET.get("service") or request.POST.get("service")
    professional_id = request.GET.get("professional") or request.POST.get("professional")
    start_iso = request.GET.get("start") or request.POST.get("start")

    if not service_id or not start_iso:
        return redirect("public:booking_start", tenant_slug=tenant.slug)

    service = get_object_or_404(Service, pk=service_id, tenant=tenant, is_active=True)
    professional = None
    if professional_id:
        professional = get_object_or_404(Professional, pk=professional_id, tenant=tenant, is_active=True)
    start_datetime = datetime.fromisoformat(start_iso)
    if start_datetime.tzinfo is None:
        start_datetime = start_datetime.replace(tzinfo=tz)
    else:
        start_datetime = start_datetime.astimezone(tz)

    availability_service = AvailabilityService(tenant=tenant)
    if not availability_service.is_slot_available(service, professional, start_datetime):
        return redirect("public:booking_start", tenant_slug=tenant.slug)

    if request.method == "POST":
        form = BookingForm(tenant=tenant, data=request.POST, hide_schedule_fields=True)
        if form.is_valid():
            booking: Booking = form.save(commit=False)
            booking.tenant = tenant
            booking.save()
            send_booking_confirmation(booking)
            return redirect("public:booking_success", tenant_slug=tenant.slug)
    else:
        initial = {
            "service": service,
            "professional": professional,
            "date": start_datetime.date(),
            "time": start_datetime.time(),
        }
        form = BookingForm(tenant=tenant, initial=initial, hide_schedule_fields=True)

    return render(
        request,
        "scheduling/public/booking_confirm.html",
        {
            "tenant": tenant,
            "form": form,
            "service": service,
            "professional": professional,
            "start_datetime": start_datetime,
        },
    )


def booking_success(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    return render(
        request,
        "scheduling/public/booking_success.html",
        {"tenant": tenant},
    )
