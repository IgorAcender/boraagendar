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
from django.utils import timezone as django_timezone
from django.utils.timezone import make_aware, now
from django.views.decorators.http import require_POST

from tenants.services import TenantSelectionRequired, ensure_membership_for_request
from tenants.forms import TeamMemberCreateForm, TeamMemberUpdateForm, TenantUpdateForm, BrandingSettingsForm
from tenants.models import TenantMembership, BrandingSettings

from ..forms import BookingForm, ProfessionalForm, ProfessionalUpdateForm, ServiceForm
from ..models import Booking, Professional, Service
from ..services.notification_dispatcher import send_booking_confirmation
from ..services.financial import FinancialAnalytics


def _get_tenant_timezone(tenant):
    """Retorna timezone do tenant com fallback seguro."""
    tz_name = (getattr(tenant, "timezone", None) or settings.TIME_ZONE or "").strip()
    try:
        return ZoneInfo(tz_name)
    except Exception:
        try:
            return ZoneInfo(settings.TIME_ZONE)
        except Exception:
            return django_timezone.get_default_timezone()


@login_required
def index(request: HttpRequest) -> HttpResponse:
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff", "professional"],
    )
    if redirect_response:
        return redirect_response
    tenant = membership.tenant
    tz = _get_tenant_timezone(tenant)
    
    # ====== PROCESSAMENTO DO FILTRO DE TEMPO GLOBAL ======
    time_filter = request.GET.get('time_filter', 'mensal')
    custom_start_date = None
    custom_end_date = None
    
    # Calcular datas baseado no filtro de tempo
    now_tz = django_timezone.now().astimezone(tz)
    
    if time_filter == 'diario':
        # Últimas 24 horas
        custom_start_date = now_tz.replace(hour=0, minute=0, second=0, microsecond=0)
        custom_end_date = now_tz.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif time_filter == 'semanal':
        # Últimos 7 dias
        custom_start_date = now_tz - timedelta(days=7)
        custom_start_date = custom_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        custom_end_date = now_tz.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif time_filter == 'mensal':
        # Últimos 30 dias
        custom_start_date = now_tz - timedelta(days=30)
        custom_start_date = custom_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        custom_end_date = now_tz.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif time_filter == 'anual':
        # Últimos 365 dias
        custom_start_date = now_tz - timedelta(days=365)
        custom_start_date = custom_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        custom_end_date = now_tz.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif time_filter.startswith('custom:'):
        # Filtro personalizado: custom:YYYY-MM-DD:YYYY-MM-DD
        try:
            parts = time_filter.split(':')
            if len(parts) == 3:
                start_str = parts[1]
                end_str = parts[2]
                custom_start_date = django_timezone.make_aware(
                    datetime.strptime(f"{start_str} 00:00:00", "%Y-%m-%d %H:%M:%S"),
                    timezone=tz
                )
                custom_end_date = django_timezone.make_aware(
                    datetime.strptime(f"{end_str} 23:59:59", "%Y-%m-%d %H:%M:%S"),
                    timezone=tz
                )
        except (ValueError, IndexError):
            # Se erro, usar padrão de últimos 30 dias
            custom_start_date = now_tz - timedelta(days=30)
            custom_start_date = custom_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            custom_end_date = now_tz.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Default: últimos 30 dias
        custom_start_date = now_tz - timedelta(days=30)
        custom_start_date = custom_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        custom_end_date = now_tz.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # ====== FIM PROCESSAMENTO DO FILTRO DE TEMPO ======
    
    # Obter filtro de período (mantido para compatibilidade, mas não é mais usado)
    period_filter = request.GET.get('period', 'all')
    # Não chamar _get_date_range pois usamos custom_start_date e custom_end_date agora
    start_date, end_date = custom_start_date, custom_end_date
    
    # Obter abas de filtro
    event_type = request.GET.get('type', 'all')
    
    # Query base
    bookings_query = Booking.objects.filter(tenant=tenant)
    
    # Aplicar filtro de data
    if start_date and end_date:
        bookings_query = bookings_query.filter(
            scheduled_for__range=(start_date, end_date)
        ) | bookings_query.filter(
            updated_at__range=(start_date, end_date)
        )
    
    # Aplicar filtro de tipo de evento
    if event_type == 'confirmed':
        bookings_query = bookings_query.filter(status='confirmed')
    elif event_type == 'pending':
        bookings_query = bookings_query.filter(status='pending')
    elif event_type == 'cancelled':
        bookings_query = bookings_query.filter(status='cancelled')
    
    # Ordenar por data de atualização (para histórico completo)
    bookings_history = bookings_query.select_related(
        'service', 'professional'
    ).order_by('-updated_at')[:50]
    
    # Para exibição, precisamos identificar reagendamentos
    bookings_with_events = []
    for booking in bookings_history:
        event_type_display = 'Agendamento'
        if booking.notes and 'Reagendado de' in booking.notes:
            event_type_display = 'Reagendamento'
        elif booking.status == 'cancelled':
            event_type_display = 'Cancelamento'
        
        bookings_with_events.append({
            'booking': booking,
            'event_type': event_type_display,
            'timestamp': booking.updated_at or booking.created_at,
        })
    
    # Últimos 10 agendamentos (para a primeira seção)
    recent_bookings = Booking.objects.filter(tenant=tenant).order_by("-scheduled_for")[:10]
    
    totals = {
        "bookings": Booking.objects.filter(tenant=tenant).count(),
        "services": Service.objects.filter(tenant=tenant).count(),
        "professionals": Professional.objects.filter(tenant=tenant).count(),
    }
    
    # Obter análise financeira
    financial_service = FinancialAnalytics(tenant)
    
    # Obter análise operacional
    from ..services.operational import OperationalAnalytics
    operational_service = OperationalAnalytics(tenant)
    
    # Usar o novo filtro de tempo global para obter os dados
    # Se houver datas customizadas do filtro de tempo, usar elas
    if custom_start_date and custom_end_date:
        financial_data = financial_service.get_summary_by_date_range(custom_start_date, custom_end_date)
        operational_data = operational_service.get_summary_by_date_range(custom_start_date, custom_end_date)
    else:
        # Fallback para padrão de 30 dias
        financial_data = financial_service.get_dashboard_summary(days=30)
        operational_data = operational_service.get_dashboard_summary(days=30)
    
    # Obter comparação de períodos
    from ..services.period_comparison import PeriodComparison
    period_comparison = PeriodComparison(tenant)
    month_comparison = period_comparison.get_month_comparison()
    week_comparison = period_comparison.get_week_comparison()
    
    # Converter dados dos gráficos para JSON
    financial_data['revenue_last_7_days'] = json.dumps(financial_data['revenue_last_7_days'])
    financial_data['revenue_last_12_months'] = json.dumps(financial_data['revenue_last_12_months'])
    
    # Converter dados operacionais para JSON
    operational_data['bookings_by_status_last_7_days'] = json.dumps(operational_data['bookings_by_status_last_7_days'])
    # peak_hours e peak_days são listas e devem permanecer como objetos Python para iteração no template
    # operational_data['peak_hours'] e operational_data['peak_days'] já são listas e não precisam de JSON
    
    context = {
        "tenant": tenant,
        "bookings": recent_bookings,
        "bookings_history": bookings_with_events,
        "totals": totals,
        "period_filter": period_filter,
        "event_filter": event_type,
        "start_date": start_date,
        "end_date": end_date,
        "subscription": tenant.subscription if hasattr(tenant, 'subscription') else None,
        # Dados operacionais
        "operational": operational_data,
        # Dados financeiros
        "financial": financial_data,
        # Comparação de períodos
        "month_comparison": month_comparison,
        "week_comparison": week_comparison,
        # Filtro de tempo global
        "current_time_filter": time_filter,
    }
    
    return render(
        request,
        "scheduling/dashboard/index.html",
        context,
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
    tz = _get_tenant_timezone(tenant)

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
    tz = _get_tenant_timezone(tenant)

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
def booking_past_list(request: HttpRequest) -> HttpResponse:
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff"],
    )
    if redirect_response:
        return redirect_response

    tenant = membership.tenant
    tz = _get_tenant_timezone(tenant)
    current_time = now().astimezone(tz)

    past_bookings = (
        Booking.objects.filter(tenant=tenant, scheduled_for__lt=current_time)
        .select_related("service", "professional")
        .order_by("-scheduled_for")
    )

    bookings_by_status: dict[str, list[Booking]] = defaultdict(list)
    for booking in past_bookings:
        bookings_by_status[booking.status].append(booking)

    statuses_payload: list[dict[str, object]] = []
    for status_value, status_label in Booking.Status.choices:
        status_bookings = bookings_by_status.get(status_value, [])
        statuses_payload.append(
            {
                "value": status_value,
                "label": status_label,
                "bookings": status_bookings,
                "count": len(status_bookings),
            }
        )

    total_past = sum(item["count"] for item in statuses_payload)

    return render(
        request,
        "scheduling/dashboard/past_bookings.html",
        {
            "tenant": tenant,
            "statuses": statuses_payload,
            "total_past": total_past,
        },
    )


@login_required
@require_POST
def booking_update_status(request: HttpRequest, pk: int) -> HttpResponse:
    """Atualiza o status de um agendamento via AJAX"""
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff"],
    )
    if redirect_response:
        return JsonResponse({"success": False, "error": "Sem permissão"}, status=403)
    
    tenant = membership.tenant
    booking = get_object_or_404(Booking, pk=pk, tenant=tenant)
    
    # Obter novo status do request
    new_status = request.POST.get('status', '').strip()
    
    # Validar status
    valid_statuses = [status[0] for status in Booking.Status.choices]
    if new_status not in valid_statuses:
        return JsonResponse({"success": False, "error": "Status inválido"}, status=400)
    
    # Atualizar status
    old_status = booking.status
    booking.status = new_status
    booking.save()
    
    print(f"DEBUG booking_update_status: Status atualizado de '{old_status}' para '{new_status}' no booking {booking.id}")
    
    return JsonResponse({
        "success": True,
        "message": f"Status atualizado para {booking.get_status_display()}",
        "status": booking.status,
        "status_display": booking.get_status_display(),
    })


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
    
    services_qs = Service.objects.filter(tenant=tenant, is_active=True).prefetch_related("professionals")
    services_list = list(services_qs)
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

    services_payload: list[dict[str, object]] = []
    professionals_cache = {}

    for service in services_list:
        professionals_qs = service.professionals.filter(is_active=True).order_by("display_name")
        professionals_data = []
        for professional in professionals_qs:
            professionals_cache[professional.pk] = professional
            professionals_data.append(
                {
                    "id": professional.pk,
                    "name": professional.display_name,
                    "color": professional.color,
                    "allow_auto_assign": getattr(professional, "allow_auto_assign", True),
                    "photo_base64": professional.photo_base64 or "",
                    "photo_url": professional.photo.url if professional.photo else "",
                    "initial": (professional.display_name[:1] or "?").upper(),
                }
            )

        services_payload.append(
            {
                "id": service.pk,
                "name": service.name,
                "category": (service.category or "").strip(),
                "description": service.description,
                "duration_minutes": service.duration_minutes or 0,
                "price": format(service.price, "f"),
                "professionals": professionals_data,
                "has_auto_assign": any(p["allow_auto_assign"] for p in professionals_data),
            }
        )

    template_name = "scheduling/dashboard/booking_form_modal.html" if is_ajax else "scheduling/dashboard/booking_form.html"
    return render(
        request,
        template_name,
        {
            "tenant": tenant,
            "form": form,
            "services": sorted(services_list, key=lambda svc: ((svc.category or "").lower(), svc.name.lower())),
            "services_json": json.dumps(services_payload, ensure_ascii=False),
            "today": datetime.now(_get_tenant_timezone(tenant)).date(),
        },
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
def get_professionals_by_service(request: HttpRequest) -> JsonResponse:
    """Retorna profissionais que atendem um serviço específico.
    Opcionalmente filtra por disponibilidade em uma data específica."""
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff"],
    )
    if redirect_response:
        return JsonResponse({"error": "Access denied"}, status=403)
    
    tenant = membership.tenant
    service_id = request.GET.get('service')
    selected_date = request.GET.get('date')
    
    if not service_id:
        return JsonResponse({"error": "Service ID is required"}, status=400)
    
    try:
        service = Service.objects.get(id=service_id, tenant=tenant)
    except Service.DoesNotExist:
        return JsonResponse({"error": "Service not found"}, status=404)
    
    # Buscar profissionais que fazem esse serviço
    professionals = service.professionals.filter(is_active=True).order_by('display_name')
    
    # Se foi passada uma data, filtrar por disponibilidade
    if selected_date:
        from ..services.availability import AvailabilityService
        availability_service = AvailabilityService(tenant)
        
        # Filtrar apenas profissionais que têm disponibilidade na data
        available_professionals = []
        for professional in professionals:
            try:
                available_times = availability_service.get_available_times_for_professional(
                    professional=professional,
                    service=service,
                    date=selected_date
                )
                if available_times:  # Se tem horários disponíveis
                    available_professionals.append(professional)
            except Exception as e:
                # Log do erro mas continue com os outros profissionais
                print(f"Erro ao verificar disponibilidade do profissional {professional.id}: {e}")
                continue
        
        professionals = available_professionals
    
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
    
    return JsonResponse({
        "professionals": professionals_data,
        "service_name": service.name,
        "date": selected_date,
        "total": len(professionals_data)
    })


@login_required
def get_available_times(request: HttpRequest) -> JsonResponse:
    """Retorna horários disponíveis para uma data e profissional específicos."""
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager", "staff"],
    )
    if redirect_response:
        return JsonResponse({"error": "Access denied"}, status=403)
    
    tenant = membership.tenant
    date_str = request.GET.get('date')
    professional_id = request.GET.get('professional')
    service_id = request.GET.get('service')
    
    if not date_str:
        return JsonResponse({"error": "Date is required"}, status=400)
    
    if not service_id:
        return JsonResponse({"error": "Service is required"}, status=400)
    
    try:
        from datetime import datetime
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format"}, status=400)
    
    # Buscar serviço (obrigatório)
    try:
        service = Service.objects.get(id=service_id, tenant=tenant)
    except Service.DoesNotExist:
        return JsonResponse({"error": "Service not found"}, status=404)
    
    # Importar o serviço de disponibilidade
    from ..services.availability import AvailabilityService
    
    # Buscar profissional se especificado
    professional = None
    if professional_id:
        try:
            professional = Professional.objects.get(id=professional_id, tenant=tenant)
        except Professional.DoesNotExist:
            return JsonResponse({"error": "Professional not found"}, status=404)
    
    # Criar instância do serviço de disponibilidade
    try:
        availability_service = AvailabilityService(tenant)
        available_slots = availability_service.get_available_slots(
            service=service,
            professional=professional,
            target_date=selected_date
        )
    except Exception as e:
        return JsonResponse({"error": f"Availability error: {str(e)}"}, status=500)
    
    # Converter para formato JSON
    slots_data = []
    for slot in available_slots:
        slots_data.append({
            "time": slot.start.strftime("%H:%M"),
            "value": slot.start.strftime("%H:%M"),
            "available": True
        })
    
    return JsonResponse({"available_times": slots_data})


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
            try:
                form.save()
                messages.success(request, "Profissional atualizado com sucesso.")
                return redirect("dashboard:professional_list")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erro ao salvar profissional {pk}: {str(e)}", exc_info=True)
                messages.error(request, f"Erro ao salvar profissional: {str(e)}")
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Formulário inválido para profissional {pk}: {form.errors}")
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
    tz = _get_tenant_timezone(tenant)

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
    tz = _get_tenant_timezone(tenant)

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
    tz = _get_tenant_timezone(tenant)

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


@login_required
def branding_settings(request: HttpRequest) -> HttpResponse:
    """Configurações de personalização de cores - apenas para donos"""
    membership, redirect_response = _membership_or_redirect(request, allowed_roles=["owner"])
    if redirect_response:
        return redirect_response
    tenant = membership.tenant

    # Obter ou criar BrandingSettings
    branding, created = BrandingSettings.objects.get_or_create(tenant=tenant)

    if request.method == "POST":
        try:
            form = BrandingSettingsForm(request.POST, request.FILES, instance=branding, tenant=tenant)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, "Configurações de cores atualizadas com sucesso!")
                    return redirect("dashboard:branding_settings")
                except Exception as save_error:
                    print(f"❌ Erro ao salvar o formulário: {save_error}")
                    import traceback
                    traceback.print_exc()
                    messages.error(request, f"Erro ao salvar: {str(save_error)}")
            else:
                print(f"❌ Erros na validação do formulário:")
                for field, errors in form.errors.items():
                    print(f"   {field}: {errors}")
                messages.error(request, f"Erros no formulário: {form.errors}")
        except Exception as e:
            print(f"❌ Erro geral na view: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"Erro ao processar: {str(e)}")
    else:
        form = BrandingSettingsForm(instance=branding, tenant=tenant)

    # Construir URL do site de forma simples e segura
    tenant_landing_url = f"/{tenant.slug}/"

    return render(
        request,
        "scheduling/dashboard/branding_settings.html",
        {
            "tenant": tenant,
            "form": form,
            "branding": branding,
            "tenant_landing_url": tenant_landing_url,
        },
    )


@login_required
def booking_policies(request: HttpRequest) -> HttpResponse:
    """Configuração de políticas de cancelamento e reagendamento"""
    membership, redirect_response = _membership_or_redirect(request, allowed_roles=["owner", "manager"])
    if redirect_response:
        return redirect_response
    tenant = membership.tenant

    # Importar aqui para evitar import circular
    from ..models import BookingPolicy

    # Obter ou criar política
    policy = BookingPolicy.get_or_create_for_tenant(tenant)

    if request.method == "POST":
        try:
            # Atualizar campos de cancelamento
            policy.allow_cancellation = request.POST.get('allow_cancellation') == 'on'
            policy.min_cancellation_hours = int(request.POST.get('min_cancellation_hours', 4))
            policy.max_cancellations = int(request.POST.get('max_cancellations', 3))
            policy.cancellation_period_days = int(request.POST.get('cancellation_period_days', 30))
            policy.require_cancellation_reason = request.POST.get('require_cancellation_reason') == 'on'
            
            # Atualizar campos de reagendamento
            policy.allow_rescheduling = request.POST.get('allow_rescheduling') == 'on'
            policy.min_reschedule_hours = int(request.POST.get('min_reschedule_hours', 2))
            policy.max_reschedules_per_booking = int(request.POST.get('max_reschedules_per_booking', 2))
            policy.reschedule_window_days = int(request.POST.get('reschedule_window_days', 60))
            
            # Atualizar campos de penalidades
            policy.block_on_limit_reached = request.POST.get('block_on_limit_reached') == 'on'
            policy.block_duration_days = int(request.POST.get('block_duration_days', 15))
            policy.notify_manager_on_abuse = request.POST.get('notify_manager_on_abuse') == 'on'
            
            policy.save()
            messages.success(request, "Políticas de agendamento atualizadas com sucesso!")
            return redirect("dashboard:booking_policies")
        except Exception as e:
            messages.error(request, f"Erro ao salvar políticas: {str(e)}")

    return render(
        request,
        "scheduling/dashboard/booking_policies.html",
        {
            "tenant": tenant,
            "policy": policy,
        },
    )


def _get_date_range(period: str, tz: ZoneInfo) -> tuple:
    """
    Obtém o intervalo de datas baseado no período selecionado.
    Retorna (start_date, end_date) como datetime aware.
    """
    from django.utils import timezone as django_tz
    
    now = django_tz.now().astimezone(tz)
    today = now.date()
    
    if period == 'today':
        # Hoje
        start = django_tz.make_aware(datetime.combine(today, time.min), tz)
        end = django_tz.make_aware(datetime.combine(today, time.max), tz)
    elif period == 'week':
        # Esta semana (segunda a domingo)
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        start = django_tz.make_aware(datetime.combine(start_date, time.min), tz)
        end = django_tz.make_aware(datetime.combine(end_date, time.max), tz)
    elif period == 'month':
        # Este mês
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = start_date.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=today.month + 1, day=1) - timedelta(days=1)
        start = django_tz.make_aware(datetime.combine(start_date, time.min), tz)
        end = django_tz.make_aware(datetime.combine(end_date, time.max), tz)
    elif period == 'year':
        # Este ano
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
        start = django_tz.make_aware(datetime.combine(start_date, time.min), tz)
        end = django_tz.make_aware(datetime.combine(end_date, time.max), tz)
    else:
        # 'all' - sem filtro de data
        return (None, None)
    
    return (start, end)


@login_required
def export_report_pdf(request: HttpRequest) -> HttpResponse:
    """Exportar relatório financeiro em PDF"""
    membership, redirect_response = _membership_or_redirect(
        request,
        allowed_roles=["owner", "manager"],
    )
    if redirect_response:
        return redirect_response
    
    tenant = membership.tenant
    
    # Obter análise financeira
    financial_service = FinancialAnalytics(tenant)
    
    # Verificar se há filtro de data customizada
    filter_start_date = request.GET.get('start_date')
    filter_end_date = request.GET.get('end_date')
    period_label = "30 Últimos Dias"
    
    if filter_start_date and filter_end_date:
        try:
            from datetime import datetime
            tz = ZoneInfo(tenant.timezone or settings.TIME_ZONE)
            # Parsear as datas do formulário
            custom_start = datetime.strptime(filter_start_date, '%Y-%m-%d').replace(tzinfo=tz)
            custom_end = datetime.strptime(filter_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=tz)
            
            # Usar filtro customizado
            financial_data = financial_service.get_summary_by_date_range(custom_start, custom_end)
            period_label = f"De {filter_start_date} até {filter_end_date}"
        except (ValueError, AttributeError):
            # Se erro ao parsear datas, usar padrão
            financial_data = financial_service.get_dashboard_summary(days=30)
    else:
        # Sem filtro customizado, usar padrão
        financial_data = financial_service.get_dashboard_summary(days=30)
    
    # Gerar PDF
    from ..services.pdf_generator import PDFReportGenerator
    
    pdf_gen = PDFReportGenerator(tenant, financial_data)
    pdf_buffer = pdf_gen.generate(period_label)
    
    # Retornar como download
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    filename = f"relatorio-financeiro-{tenant.slug}-{django_timezone.now().strftime('%Y%m%d-%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


