from collections import defaultdict
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import make_aware, now
from django.views.decorators.http import require_POST

from tenants.services import TenantSelectionRequired, ensure_membership_for_request
from tenants.forms import TeamMemberCreateForm, TeamMemberUpdateForm, TenantUpdateForm
from tenants.models import TenantMembership

from ..forms import BookingForm, ProfessionalForm, ProfessionalUpdateForm, ServiceForm
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
    tz = ZoneInfo(tenant.timezone or settings.TIME_ZONE)

    # Get week offset (default to current week)
    week_offset = int(request.GET.get('week_offset', 0))
    today = now().astimezone(tz).date()
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

    # Generate hours (0:00 to 23:00 - todas as 24 horas)
    hours = []
    for hour in range(0, 24):
        hours.append(f"{hour:02d}:00")

    # Get professional filter (se houver)
    professional_filter_id = request.GET.get('professional')
    selected_professional = None
    if professional_filter_id:
        try:
            selected_professional = Professional.objects.get(pk=professional_filter_id, tenant=tenant)
        except Professional.DoesNotExist:
            pass

    # Get bookings for this week
    week_start_dt = make_aware(datetime.combine(start_of_week, time.min), tz)
    week_end_dt = make_aware(datetime.combine(end_of_week, time.max), tz)
    bookings_query = Booking.objects.filter(
        tenant=tenant,
        scheduled_for__range=(week_start_dt, week_end_dt)
    )

    # Aplicar filtro de profissional se selecionado
    if selected_professional:
        bookings_query = bookings_query.filter(professional=selected_professional)

    bookings_raw = bookings_query.select_related('service', 'professional').order_by('scheduled_for')

    print(f"DEBUG calendar_view: Total bookings encontrados: {bookings_raw.count()}")
    print(f"DEBUG calendar_view: Período: {week_start_dt} até {week_end_dt}")

    # Process bookings for template
    bookings_by_cell = defaultdict(list)
    for booking in bookings_raw:
        print(f"DEBUG calendar_view: Processando booking ID {booking.id} - {booking.customer_name} - {booking.scheduled_for}")
        local_scheduled_for = booking.scheduled_for.astimezone(tz)
        date = local_scheduled_for.date()
        # Usar apenas a hora (sem minutos) para agrupar na célula correta
        hour_base = local_scheduled_for.strftime('%H:00')
        # Calculate height based on duration (altura proporcional em %)
        height = (booking.duration_minutes / 60) * 100
        # Calculate offset within the cell (posição vertical dentro da célula em %)
        minutes = local_scheduled_for.minute
        offset = (minutes / 60) * 100

        bookings_by_cell[(date, hour_base)].append({
            'id': booking.pk,
            'customer_name': booking.customer_name,
            'service': booking.service,
            'professional': booking.professional,
            'scheduled_for': local_scheduled_for,
            'status': booking.status,
            'height': height,  # Altura em %
            'offset': offset,  # Offset em %
            'date': date,
            'hour': hour_base,  # HH:00 format (hora base da célula)
            'time_display': local_scheduled_for.strftime('%H:%M'),  # Hora exata para exibir
        })

    # Get all professionals for filter
    professionals = Professional.objects.filter(tenant=tenant, is_active=True).order_by('display_name')

    # Flatten bookings for template
    bookings_list = []
    for bookings in bookings_by_cell.values():
        bookings_list.extend(bookings)

    print(f"DEBUG calendar_view: Total bookings na lista final: {len(bookings_list)}")
    for b in bookings_list:
        print(f"  - ID {b['id']}: {b['customer_name']} em {b['date']} às {b['hour']} (status: {b['status']})")

    # Get availability rules (horários de atendimento)
    from ..models import AvailabilityRule
    availability_rules = AvailabilityRule.objects.filter(
        tenant=tenant,
                professional__isnull=True,  # Horário padrão da empresa
        is_active=True
    ).order_by('weekday', 'start_time')

    # Organizar disponibilidade por dia da semana
    availability_by_weekday = defaultdict(list)
    for rule in availability_rules:
        availability_by_weekday[rule.weekday].append({
            'start_time': rule.start_time,
            'end_time': rule.end_time,
            'break_start': rule.break_start,
            'break_end': rule.break_end,
        })

    # Adicionar disponibilidade aos dias da semana
    for day in week_days:
        weekday = day['date'].weekday()
        day['availability'] = availability_by_weekday.get(weekday, [])

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
            "selected_professional": selected_professional,
            "availability_by_weekday": dict(availability_by_weekday),
        },
    )


@login_required
def calendar_day_view(request: HttpRequest) -> HttpResponse:
    ""    """Visualização diária mostrando todos os profissionais em colunas"""""
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff", "professional"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    tz = ZoneInfo(tenant.timezone or settings.TIME_ZONE)

    # Get selected date from query param or use today
    today = now().astimezone(tz).date()
    date_param = request.GET.get('date')

    if date_param:
        try:
            from datetime import datetime as dt
            selected_date = dt.strptime(date_param, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            selected_date = today
    else:
        # Fallback to day_offset for backward compatibility
        day_offset = int(request.GET.get('day_offset', 0))
        selected_date = today + timedelta(days=day_offset)

    # Calculate day_offset for navigation buttons
    day_offset = (selected_date - today).days

    # Day name
    day_names = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    day_name = day_names[selected_date.weekday()]

    # Generate hours (0:00 to 23:00 - todas as 24 horas)
    hours = []
    for hour in range(0, 24):
        hours.append(f"{hour:02d}:00")

    # Get all active professionals
    professionals = Professional.objects.filter(tenant=tenant, is_active=True).order_by('display_name')

    # Get bookings for this day for all professionals
    day_start_dt = make_aware(datetime.combine(selected_date, time.min), tz)
    day_end_dt = make_aware(datetime.combine(selected_date, time.max), tz)
    bookings_query = Booking.objects.filter(
        tenant=tenant,
        scheduled_for__range=(day_start_dt, day_end_dt)
    ).select_related('service', 'professional').order_by('scheduled_for')

    # Process bookings by professional and hour
    bookings_by_professional_hour = defaultdict(lambda: defaultdict(list))
    for booking in bookings_query:
        local_scheduled_for = booking.scheduled_for.astimezone(tz)
        hour_base = local_scheduled_for.strftime('%H:00')

        # Calculate height based on duration (altura proporcional em %)
        height = (booking.duration_minutes / 60) * 100
        # Calculate offset within the cell (posição vertical dentro da célula em %)
        minutes = local_scheduled_for.minute
        offset = (minutes / 60) * 100

        bookings_by_professional_hour[booking.professional.id][hour_base].append({
            'id': booking.pk,
            'customer_name': booking.customer_name,
            'service': booking.service,
            'professional': booking.professional,
            'scheduled_for': local_scheduled_for,
            'status': booking.status,
            'height': height,
            'offset': offset,
            'time_display': local_scheduled_for.strftime('%H:%M'),
        })

    # Get availability rules for each professional
    from ..models import AvailabilityRule
    availability_by_professional = {}

    for professional in professionals:
        # Tentar pegar regras específicas do profissional, senão usa as padrão da empresa
        rules = AvailabilityRule.objects.filter(
            tenant=tenant,
            professional=professional,
            is_active=True,
            weekday=selected_date.weekday()
        )

        if not rules.exists():
                        # Usar regras padrão da empresa
            rules = AvailabilityRule.objects.filter(
                tenant=tenant,
                professional__isnull=True,
                is_active=True,
                weekday=selected_date.weekday()
            )

        availability_by_professional[professional.id] = [
            {
                'start_time': rule.start_time,
                'end_time': rule.end_time,
                'break_start': rule.break_start,
                'break_end': rule.break_end,
            }
            for rule in rules
        ]

    return render(
        request,
        "scheduling/dashboard/calendar_day.html",
        {
            "tenant": tenant,
            "professionals": professionals,
            "hours": hours,
            "selected_date": selected_date,
            "day_name": day_name,
            "day_offset": day_offset,
            "bookings_by_professional_hour": dict(bookings_by_professional_hour),
            "availability_by_professional": availability_by_professional,
            "is_today": selected_date == today,
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
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if request.method == "POST":
        form = BookingForm(tenant=tenant, data=request.POST)
        if form.is_valid():
            print("DEBUG booking_create: form válido. Dados limpos:", form.cleaned_data)
            booking = form.save(commit=False)
            booking.tenant = tenant
            booking.created_by = request.user
            booking.save()
            print(f"DEBUG booking_create: booking salvo com ID {booking.pk} para {booking.customer_name} em {booking.scheduled_for}")
            send_booking_confirmation(booking)
            messages.success(request, "Agendamento criado com sucesso.")
            if is_ajax:
                return JsonResponse(
                    {
                        "success": True,
                        "booking": {
                            "id": booking.pk,
                            "customer_name": booking.customer_name,
                            "scheduled_for": booking.scheduled_for.isoformat(),
                            "status": booking.status,
                        },
                    }
                )
            return redirect(reverse("dashboard:booking_detail", kwargs={"pk": booking.pk}))
        else: # Form is invalid
            print("DEBUG booking_create: form inválido:", form.errors)
            if is_ajax:
                # For AJAX, re-render the form snippet with errors and a 400 status
                return render(
                    request,
                    "scheduling/dashboard/booking_form_modal.html",
                    {"tenant": tenant, "form": form},
                    status=400
                )
    else: # GET request
        form = BookingForm(tenant=tenant)

    template_name = "scheduling/dashboard/booking_form_modal.html" if is_ajax else "scheduling/dashboard/booking_form.html"
    return render(
        request,
        template_name,
        {"tenant": tenant, "form": form},
    )


@login_required
def get_professionals_data(request: HttpRequest) -> JsonResponse:
    """Retorna dados dos profissionais incluindo fotos para AJAX."""
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff"],
    )
    if redirect_response:
        return JsonResponse({"error": "Access denied"}, status=403)
    
    tenant = membership.tenant
    professionals = Professional.objects.filter(tenant=tenant, is_active=True)
    
    professionals_data = []
    for professional in professionals:
        prof_data = {
            "id": professional.id,
            "name": professional.display_name,
            "color": professional.color,
            "photo_url": None,
            "photo_base64": None,
        }
        
        # Adicionar foto se disponível
        if professional.photo_base64:
            prof_data["photo_base64"] = professional.photo_base64
        elif professional.photo:
            prof_data["photo_url"] = professional.photo.url
            
        professionals_data.append(prof_data)
    
    return JsonResponse({"professionals": professionals_data})


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

    services = Service.objects.filter(tenant=tenant).order_by("category", "name")
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
        service.category = request.POST.get("category", "").strip()
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


@login_required
def professional_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Update existing professional"""
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    professional = get_object_or_404(Professional, pk=pk, tenant=tenant)

    if request.method == "POST":
        form = ProfessionalUpdateForm(tenant=tenant, data=request.POST, files=request.FILES, instance=professional)
        if form.is_valid():
            form.save()
            messages.success(request, "Profissional atualizado com sucesso.")
            return redirect("dashboard:professional_list")
    else:
        form = ProfessionalUpdateForm(tenant=tenant, instance=professional)

    return render(
        request,
        "scheduling/dashboard/professional_form.html",
        {"tenant": tenant, "form": form, "professional": professional},
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
def tenant_settings(request: HttpRequest) -> HttpResponse:
    """Configurações da empresa - apenas para donos"""
    membership, redirect_response = _membership_or_redirect(request, allowed_roles=["owner"])
    if redirect_response:
        return redirect_response
    tenant = membership.tenant

    if request.method == "POST":
        try:
            form = TenantUpdateForm(request.POST, request.FILES, instance=tenant)
            if form.is_valid():
                form.save()
                messages.success(request, "Configurações da empresa atualizadas com sucesso!")
                return redirect("dashboard:tenant_settings")
            else:
                messages.error(request, f"Erros no formulário: {form.errors}")
        except Exception as e:
            messages.error(request, f"Erro ao salvar: {str(e)}")
            import traceback
            print("ERRO COMPLETO:")
            traceback.print_exc()
    else:
        form = TenantUpdateForm(instance=tenant)

    return render(
        request,
        "scheduling/dashboard/tenant_settings.html",
        {"tenant": tenant, "form": form},
    )


@login_required
@require_POST
def booking_move(request: HttpRequest, pk: int) -> JsonResponse:
    """Move booking to new date/time via drag & drop"""
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff"],
    )
    if redirect_response:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    tenant = membership.tenant
    booking = get_object_or_404(Booking, pk=pk, tenant=tenant)
    tz = ZoneInfo(tenant.timezone or settings.TIME_ZONE)

    try:
        data = json.loads(request.body)
        new_date = data.get('date')  # YYYY-MM-DD
        new_time = data.get('time')  # HH:MM

        if not new_date or not new_time:
            return JsonResponse({"success": False, "error": "Missing date or time"}, status=400)

        # Parse new datetime
        new_datetime_str = f"{new_date} {new_time}"
        naive_datetime = datetime.strptime(new_datetime_str, "%Y-%m-%d %H:%M")
        new_datetime = make_aware(naive_datetime, tz)

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
    tz = ZoneInfo(tenant.timezone or settings.TIME_ZONE)

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
            name = request.POST.get('name')
            start = request.POST.get('start')
            end = request.POST.get('end')

            TimeOff.objects.create(
                tenant=tenant,
                professional=professional,
                name=name,
                start=make_aware(datetime.fromisoformat(start), tz),
                end=make_aware(datetime.fromisoformat(end), tz)
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

    timeoffs = TimeOff.objects.filter(
        tenant=tenant,
        professional=professional,
        end__gte=now()
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
    tz = ZoneInfo(tenant.timezone or settings.TIME_ZONE)

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
            name = request.POST.get('name')
            start = request.POST.get('start')
            end = request.POST.get('end')

            TimeOff.objects.create(
                tenant=tenant,
                professional=professional,
                name=name,
                start=make_aware(datetime.fromisoformat(start), tz),
                end=make_aware(datetime.fromisoformat(end), tz)
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

    timeoffs = TimeOff.objects.filter(
        tenant=tenant,
        professional=professional,
        end__gte=now()
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


@login_required
def default_availability_view(request: HttpRequest) -> HttpResponse:
    """Gerenciar horários padrão da empresa"""
    from ..models import AvailabilityRule

    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant

        # Buscar horários padrão (professional=None significa padrão da empresa)
    default_rules = AvailabilityRule.objects.filter(
        tenant=tenant,
        professional__isnull=True,
        is_active=True
    ).order_by('weekday', 'start_time')

    # Organizar por dia da semana
    rules_by_weekday = defaultdict(list)
    for rule in default_rules:
        rules_by_weekday[rule.weekday].append(rule)

    weekdays = [
        {"value": 0, "label": "Segunda", "rules": rules_by_weekday[0]},
        {"value": 1, "label": "Terça", "rules": rules_by_weekday[1]},
        {"value": 2, "label": "Quarta", "rules": rules_by_weekday[2]},
        {"value": 3, "label": "Quinta", "rules": rules_by_weekday[3]},
        {"value": 4, "label": "Sexta", "rules": rules_by_weekday[4]},
        {"value": 5, "label": "Sábado", "rules": rules_by_weekday[5]},
        {"value": 6, "label": "Domingo", "rules": rules_by_weekday[6]},
    ]

    return render(
        request,
        "scheduling/dashboard/default_availability.html",
        {
            "tenant": tenant,
            "weekdays": weekdays,
        },
    )


@login_required
@require_POST
def default_availability_save(request: HttpRequest) -> HttpResponse:
    """Salvar horários padrão da empresa"""
    from ..models import AvailabilityRule

    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant

    # Deletar todas as regras padrão existentes
    AvailabilityRule.objects.filter(tenant=tenant, professional__isnull=True).delete()

    # Criar novas regras
    created_count = 0
    for weekday in range(7):
        i = 0
        while True:
            start_key = f"weekday_{weekday}_{i}_start"
            end_key = f"weekday_{weekday}_{i}_end"

            start_time_str = request.POST.get(start_key)
            end_time_str = request.POST.get(end_key)

            if not start_time_str or not end_time_str:
                break

            try:
                start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()

                break_start_str = request.POST.get(f"weekday_{weekday}_{i}_break_start", "").strip()
                break_end_str = request.POST.get(f"weekday_{weekday}_{i}_break_end", "").strip()

                break_start_obj = None
                break_end_obj = None

                if break_start_str and break_end_str:
                    break_start_obj = datetime.strptime(break_start_str, '%H:%M').time()
                    break_end_obj = datetime.strptime(break_end_str, '%H:%M').time()

                AvailabilityRule.objects.create(
                    tenant=tenant,
                    professional=None,
                    weekday=weekday,
                    start_time=start_time_obj,
                    end_time=end_time_obj,
                    break_start=break_start_obj,
                    break_end=break_end_obj,
                    is_active=True
                )
                created_count += 1
            except ValueError:
                pass

            i += 1

    messages.success(request, f"Horários padrão salvos! ({created_count} regras)")
    return redirect("dashboard:default_availability")
