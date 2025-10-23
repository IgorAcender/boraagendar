from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
import json

from tenants.services import TenantSelectionRequired, ensure_membership_for_request
from tenants.forms import TeamMemberCreateForm, TeamMemberUpdateForm
from tenants.models import TenantMembership

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
    from datetime import datetime, timedelta, time
    from collections import defaultdict

    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff", "professional"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant

    # Get week offset (default to current week)
    week_offset = int(request.GET.get('week_offset', 0))
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    # Build week days
    week_days = []
    day_names = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        week_days.append({
            'date': day_date,
            'name': day_names[i],
            'is_today': day_date == today,
        })

    # Generate hours (8:00 to 20:00 with 30min intervals)
    hours = []
    for hour in range(8, 21):
        hours.append(f"{hour:02d}:00")
        if hour < 20:
            hours.append(f"{hour:02d}:30")

    # Get bookings for this week
    week_start_dt = datetime.combine(start_of_week, time.min)
    week_end_dt = datetime.combine(end_of_week, time.max)
    bookings_raw = Booking.objects.filter(
        tenant=tenant,
        scheduled_for__range=(week_start_dt, week_end_dt)
    ).select_related('service', 'professional').order_by('scheduled_for')

    # Process bookings for template
    bookings_by_cell = defaultdict(list)
    for booking in bookings_raw:
        date = booking.scheduled_for.date()
        hour = booking.scheduled_for.strftime('%H:%M')
        # Calculate height based on duration (60px per hour)
        height = (booking.duration_minutes / 60) * 100
        # Calculate offset within the cell
        minutes = booking.scheduled_for.minute
        offset = (minutes / 60) * 100 if minutes != 0 else 0

        bookings_by_cell[(date, hour[:5])].append({
            'id': booking.pk,
            'customer_name': booking.customer_name,
            'service': booking.service,
            'professional': booking.professional,
            'scheduled_for': booking.scheduled_for,
            'status': booking.status,
            'height': min(height, 200),  # Limit to 2 cells max
            'offset': offset,
            'date': date,
            'hour': hour[:5],  # HH:MM format
        })

    # Get all professionals for filter
    professionals = Professional.objects.filter(tenant=tenant, is_active=True).order_by('display_name')

    # Flatten bookings for template
    bookings_list = []
    for bookings in bookings_by_cell.values():
        bookings_list.extend(bookings)

    return render(
        request,
        "scheduling/dashboard/calendar.html",
        {
            "tenant": tenant,
            "bookings": bookings_list,
            "week_days": week_days,
            "hours": hours,
            "week_start": start_of_week,
            "week_end": end_of_week,
            "professionals": professionals,
        },
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
def service_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Update existing service"""
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    service = get_object_or_404(Service, pk=pk, tenant=tenant)

    if request.method == "POST":
        service.name = request.POST.get("name")
        service.description = request.POST.get("description", "")
        service.price = request.POST.get("price")
        service.duration_minutes = request.POST.get("duration_minutes")
        service.is_active = request.POST.get("is_active") == "on"
        service.save()
        messages.success(request, "Serviço atualizado com sucesso.")
        return redirect("dashboard:service_list")

    return redirect("dashboard:service_list")


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
        form = ProfessionalForm(tenant=tenant, data=request.POST, files=request.FILES)
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

    professionals = Professional.objects.filter(tenant=tenant).select_related("user").order_by("display_name")
    totals = {
        "professionals": professionals.count(),
        "active": professionals.filter(is_active=True).count(),
        "services": Service.objects.filter(tenant=tenant).count(),
    }
    return render(
        request,
        "scheduling/dashboard/professional_list.html",
        {"tenant": tenant, "professionals": professionals, "form": form, "totals": totals},
    )


def _membership_or_redirect(request: HttpRequest, allowed_roles: list[str]):
    try:
        membership = ensure_membership_for_request(request, allowed_roles=allowed_roles)
    except TenantSelectionRequired:
        select_url = f"{reverse('accounts:select_tenant')}?next={request.get_full_path()}"
        return None, redirect(select_url)
    return membership, None


@login_required
def team_list(request: HttpRequest) -> HttpResponse:
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant

    if request.method == "POST":
        form = TeamMemberCreateForm(request.POST, tenant=tenant)
        if form.is_valid():
            user, member = form.save()
            msg = f"Membro adicionado: {user.email} ({member.get_role_display()})."
            if form.generated_password:
                msg += f" Senha inicial: {form.generated_password}"
            messages.success(request, msg)
            return redirect("dashboard:team_list")
    else:
        form = TeamMemberCreateForm(tenant=tenant)

    members = (
        TenantMembership.objects.filter(tenant=tenant)
        .select_related("user")
        .order_by("-is_active", "user__first_name", "user__email")
    )
    return render(
        request,
        "scheduling/dashboard/team_list.html",
        {"tenant": tenant, "members": members, "form": form},
    )


@login_required
def team_update(request: HttpRequest, pk: int) -> HttpResponse:
    membership, redirect_response = _membership_or_redirect(request, allowed_roles=["owner"]) 
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    member = get_object_or_404(TenantMembership, pk=pk, tenant=tenant)
    if request.method == "POST":
        form = TeamMemberUpdateForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Membro atualizado.")
    return redirect("dashboard:team_list")


@login_required
def team_remove(request: HttpRequest, pk: int) -> HttpResponse:
    membership, redirect_response = _membership_or_redirect(request, allowed_roles=["owner"])
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    member = get_object_or_404(TenantMembership, pk=pk, tenant=tenant)
    if request.method == "POST":
        member.is_active = False
        member.save(update_fields=["is_active"])
        messages.success(request, "Membro desativado.")
    return redirect("dashboard:team_list")


@login_required
@require_POST
def booking_move(request: HttpRequest, pk: int) -> JsonResponse:
    """Move booking to new date/time via drag & drop"""
    from datetime import datetime

    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff"],
    )
    if redirect_response:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    tenant = membership.tenant
    booking = get_object_or_404(Booking, pk=pk, tenant=tenant)

    try:
        data = json.loads(request.body)
        new_date = data.get('date')  # YYYY-MM-DD
        new_time = data.get('time')  # HH:MM

        if not new_date or not new_time:
            return JsonResponse({"success": False, "error": "Missing date or time"}, status=400)

        # Parse new datetime
        new_datetime_str = f"{new_date} {new_time}"
        new_datetime = datetime.strptime(new_datetime_str, "%Y-%m-%d %H:%M")

        # Update booking
        booking.scheduled_for = new_datetime
        booking.save(update_fields=['scheduled_for', 'updated_at'])

        return JsonResponse({
            "success": True,
            "message": "Agendamento movido com sucesso",
            "booking": {
                "id": booking.pk,
                "scheduled_for": booking.scheduled_for.strftime("%Y-%m-%d %H:%M"),
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    except ValueError as e:
        return JsonResponse({"success": False, "error": f"Invalid date/time format: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)



@login_required
def professional_schedule(request: HttpRequest, pk: int) -> HttpResponse:
    """Manage professional's working hours (owner/manager only)"""
    from ..models import AvailabilityRule, TimeOff

    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager"],
    )
    if redirect_response:
        return redirect_response

    tenant = membership.tenant
    professional = get_object_or_404(Professional, pk=pk, tenant=tenant)

    # Handle form submissions
    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'add_availability':
            weekday = int(request.POST.get('weekday'))
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            break_start = request.POST.get('break_start') or None
            break_end = request.POST.get('break_end') or None

            AvailabilityRule.objects.create(
                tenant=tenant,
                professional=professional,
                weekday=weekday,
                start_time=start_time,
                end_time=end_time,
                break_start=break_start,
                break_end=break_end,
                is_active=True
            )
            messages.success(request, "Horário adicionado com sucesso.")

        elif action == 'delete_availability':
            rule_id = request.POST.get('rule_id')
            AvailabilityRule.objects.filter(pk=rule_id, tenant=tenant).delete()
            messages.success(request, "Horário removido.")

        elif action == 'add_timeoff':
            from datetime import datetime
            name = request.POST.get('name')
            start = request.POST.get('start')
            end = request.POST.get('end')

            TimeOff.objects.create(
                tenant=tenant,
                professional=professional,
                name=name,
                start=datetime.fromisoformat(start),
                end=datetime.fromisoformat(end)
            )
            messages.success(request, "Folga adicionada com sucesso.")

        elif action == 'delete_timeoff':
            timeoff_id = request.POST.get('timeoff_id')
            TimeOff.objects.filter(pk=timeoff_id, tenant=tenant).delete()
            messages.success(request, "Folga removida.")

        return redirect('dashboard:professional_schedule', pk=pk)

    availability_rules = AvailabilityRule.objects.filter(
        tenant=tenant,
        professional=professional,
        is_active=True
    ).order_by('weekday', 'start_time')

    from datetime import datetime
    timeoffs = TimeOff.objects.filter(
        tenant=tenant,
        professional=professional,
        end__gte=datetime.now()
    ).order_by('start')

    return render(
        request,
        "scheduling/dashboard/professional_schedule.html",
        {
            "tenant": tenant,
            "professional": professional,
            "availability_rules": availability_rules,
            "timeoffs": timeoffs,
        },
    )


@login_required
def my_schedule(request: HttpRequest) -> HttpResponse:
    """Professional manages their own schedule"""
    from ..models import AvailabilityRule, TimeOff

    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["professional"],
    )
    if redirect_response:
        return redirect_response

    tenant = membership.tenant

    try:
        professional = Professional.objects.get(user=request.user, tenant=tenant)
    except Professional.DoesNotExist:
        messages.error(request, "Você não está cadastrado como profissional.")
        return redirect('dashboard:index')

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'add_availability':
            weekday = int(request.POST.get('weekday'))
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            break_start = request.POST.get('break_start') or None
            break_end = request.POST.get('break_end') or None

            AvailabilityRule.objects.create(
                tenant=tenant,
                professional=professional,
                weekday=weekday,
                start_time=start_time,
                end_time=end_time,
                break_start=break_start,
                break_end=break_end,
                is_active=True
            )
            messages.success(request, "Horário adicionado com sucesso.")

        elif action == 'delete_availability':
            rule_id = request.POST.get('rule_id')
            AvailabilityRule.objects.filter(pk=rule_id, tenant=tenant, professional=professional).delete()
            messages.success(request, "Horário removido.")

        elif action == 'add_timeoff':
            from datetime import datetime
            name = request.POST.get('name')
            start = request.POST.get('start')
            end = request.POST.get('end')

            TimeOff.objects.create(
                tenant=tenant,
                professional=professional,
                name=name,
                start=datetime.fromisoformat(start),
                end=datetime.fromisoformat(end)
            )
            messages.success(request, "Folga adicionada com sucesso.")

        elif action == 'delete_timeoff':
            timeoff_id = request.POST.get('timeoff_id')
            TimeOff.objects.filter(pk=timeoff_id, tenant=tenant, professional=professional).delete()
            messages.success(request, "Folga removida.")

        return redirect('dashboard:my_schedule')

    availability_rules = AvailabilityRule.objects.filter(
        tenant=tenant,
        professional=professional,
        is_active=True
    ).order_by('weekday', 'start_time')

    from datetime import datetime
    timeoffs = TimeOff.objects.filter(
        tenant=tenant,
        professional=professional,
        end__gte=datetime.now()
    ).order_by('start')

    return render(
        request,
        "scheduling/dashboard/my_schedule.html",
        {
            "tenant": tenant,
            "professional": professional,
            "availability_rules": availability_rules,
            "timeoffs": timeoffs,
        },
    )


@login_required
def professional_services(request: HttpRequest, pk: int) -> HttpResponse:
    """Manage professional's services and prices (owner/manager only)"""
    from ..models import ProfessionalService

    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager"],
    )
    if redirect_response:
        return redirect_response

    tenant = membership.tenant
    professional = get_object_or_404(Professional, pk=pk, tenant=tenant)

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'add_service':
            service_id = request.POST.get('service_id')
            custom_price = request.POST.get('custom_price') or None
            custom_duration = request.POST.get('custom_duration') or None

            service = get_object_or_404(Service, pk=service_id, tenant=tenant)

            ProfessionalService.objects.get_or_create(
                professional=professional,
                service=service,
                defaults={
                    'price': custom_price,
                    'duration_minutes': custom_duration,
                }
            )
            messages.success(request, f"Serviço '{service.name}' adicionado.")

        elif action == 'update_service':
            ps_id = request.POST.get('ps_id')
            custom_price = request.POST.get('custom_price') or None
            custom_duration = request.POST.get('custom_duration') or None

            ps = get_object_or_404(ProfessionalService, pk=ps_id, professional__tenant=tenant)
            ps.price = custom_price
            ps.duration_minutes = custom_duration
            ps.save()
            messages.success(request, "Serviço atualizado.")

        elif action == 'remove_service':
            ps_id = request.POST.get('ps_id')
            ProfessionalService.objects.filter(pk=ps_id, professional__tenant=tenant).delete()
            messages.success(request, "Serviço removido.")

        return redirect('dashboard:professional_services', pk=pk)

    # Get professional's services
    professional_services = ProfessionalService.objects.filter(
        professional=professional
    ).select_related('service')

    # Get available services not yet assigned
    assigned_service_ids = [ps.service.id for ps in professional_services]
    available_services = Service.objects.filter(
        tenant=tenant,
        is_active=True
    ).exclude(id__in=assigned_service_ids)

    return render(
        request,
        "scheduling/dashboard/professional_services.html",
        {
            "tenant": tenant,
            "professional": professional,
            "professional_services": professional_services,
            "available_services": available_services,
        },
    )


@login_required
def my_services(request: HttpRequest) -> HttpResponse:
    """Professional manages their own services and prices"""
    from ..models import ProfessionalService

    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["professional"],
    )
    if redirect_response:
        return redirect_response

    tenant = membership.tenant

    try:
        professional = Professional.objects.get(user=request.user, tenant=tenant)
    except Professional.DoesNotExist:
        messages.error(request, "Você não está cadastrado como profissional.")
        return redirect('dashboard:index')

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'add_service':
            service_id = request.POST.get('service_id')
            custom_price = request.POST.get('custom_price') or None
            custom_duration = request.POST.get('custom_duration') or None

            service = get_object_or_404(Service, pk=service_id, tenant=tenant)

            ProfessionalService.objects.get_or_create(
                professional=professional,
                service=service,
                defaults={
                    'price': custom_price,
                    'duration_minutes': custom_duration,
                }
            )
            messages.success(request, f"Serviço '{service.name}' adicionado.")

        elif action == 'update_service':
            ps_id = request.POST.get('ps_id')
            custom_price = request.POST.get('custom_price') or None
            custom_duration = request.POST.get('custom_duration') or None

            ps = get_object_or_404(
                ProfessionalService,
                pk=ps_id,
                professional=professional,
                professional__tenant=tenant
            )
            ps.price = custom_price
            ps.duration_minutes = custom_duration
            ps.save()
            messages.success(request, "Serviço atualizado.")

        elif action == 'remove_service':
            ps_id = request.POST.get('ps_id')
            ProfessionalService.objects.filter(
                pk=ps_id,
                professional=professional,
                professional__tenant=tenant
            ).delete()
            messages.success(request, "Serviço removido.")

        return redirect('dashboard:my_services')

    professional_services = ProfessionalService.objects.filter(
        professional=professional
    ).select_related('service')

    assigned_service_ids = [ps.service.id for ps in professional_services]
    available_services = Service.objects.filter(
        tenant=tenant,
        is_active=True
    ).exclude(id__in=assigned_service_ids)

    return render(
        request,
        "scheduling/dashboard/my_services.html",
        {
            "tenant": tenant,
            "professional": professional,
            "professional_services": professional_services,
            "available_services": available_services,
        },
    )
