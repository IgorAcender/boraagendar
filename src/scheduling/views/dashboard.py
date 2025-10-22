from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from tenants.services import TenantSelectionRequired, ensure_membership_for_request

from ..forms import BookingForm, ProfessionalForm, ServiceForm
from ..models import Booking, Professional, Service
from ..services.notification_dispatcher import send_booking_confirmation


@login_required
def index(request: HttpRequest) -> HttpResponse:
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff", "professional"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    bookings = Booking.objects.filter(tenant=tenant).order_by("-scheduled_for")[:10]
    totals = {
        "bookings": Booking.objects.filter(tenant=tenant).count(),
        "services": Service.objects.filter(tenant=tenant).count(),
        "professionals": Professional.objects.filter(tenant=tenant).count(),
    }
    return render(
        request,
        "scheduling/dashboard/index.html",
        {"tenant": tenant, "bookings": bookings, "totals": totals},
    )


@login_required
def calendar_view(request: HttpRequest) -> HttpResponse:
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff", "professional"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    bookings = Booking.objects.filter(tenant=tenant).order_by("scheduled_for")
    return render(
        request,
        "scheduling/dashboard/calendar.html",
        {"tenant": tenant, "bookings": bookings},
    )


@login_required
def booking_detail(request: HttpRequest, pk: int) -> HttpResponse:
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff", "professional"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    booking = get_object_or_404(Booking, pk=pk, tenant=tenant)
    return render(
        request,
        "scheduling/dashboard/booking_detail.html",
        {"tenant": tenant, "booking": booking},
    )


@login_required
def booking_create(request: HttpRequest) -> HttpResponse:
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    if request.method == "POST":
        form = BookingForm(tenant=tenant, data=request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.tenant = tenant
            booking.created_by = request.user
            booking.save()
            send_booking_confirmation(booking)
            messages.success(request, "Agendamento criado com sucesso.")
            return redirect(reverse("dashboard:booking_detail", kwargs={"pk": booking.pk}))
    else:
        form = BookingForm(tenant=tenant)

    return render(
        request,
        "scheduling/dashboard/booking_form.html",
        {"tenant": tenant, "form": form},
    )


@login_required
def service_list(request: HttpRequest) -> HttpResponse:
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    if request.method == "POST":
        form = ServiceForm(tenant=tenant, data=request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.tenant = tenant
            service.save()
            form.save_m2m()
            messages.success(request, "Servico salvo com sucesso.")
            return redirect("dashboard:service_list")
    else:
        form = ServiceForm(tenant=tenant)

    services = Service.objects.filter(tenant=tenant).order_by("name")
    return render(
        request,
        "scheduling/dashboard/service_list.html",
        {"tenant": tenant, "services": services, "form": form},
    )


@login_required
def professional_list(request: HttpRequest) -> HttpResponse:
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    if request.method == "POST":
        form = ProfessionalForm(tenant=tenant, data=request.POST)
        if form.is_valid():
            professional = form.save(commit=False)
            professional.tenant = tenant
            professional.save()
            # Se um novo usuário foi criado no form, mostre credenciais temporárias
            creds = getattr(form, "generated_credentials", None)
            if creds:
                messages.info(
                    request,
                    (
                        "Usuário criado: %s | Senha temporária: %s. "
                        "Peça para o funcionário alterar a senha em Perfil."
                    )
                    % (creds["email"], creds["password"]),
                )
            messages.success(request, "Profissional salvo com sucesso.")
            return redirect("dashboard:professional_list")
    else:
        form = ProfessionalForm(tenant=tenant)

    professionals = Professional.objects.filter(tenant=tenant).order_by("display_name")
    return render(
        request,
        "scheduling/dashboard/professional_list.html",
        {"tenant": tenant, "professionals": professionals, "form": form},
    )


def _membership_or_redirect(request: HttpRequest, allowed_roles: list[str]):
    try:
        membership = ensure_membership_for_request(request, allowed_roles=allowed_roles)
    except TenantSelectionRequired:
        select_url = f"{reverse('accounts:select_tenant')}?next={request.get_full_path()}"
        return None, redirect(select_url)
    return membership, None
