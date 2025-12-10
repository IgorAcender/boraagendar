from datetime import datetime
from zoneinfo import ZoneInfo
import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from tenants.models import Tenant, BrandingSettings
from ..models import AvailabilityRule

from ..forms import AvailabilitySearchForm, BookingForm
from ..models import Booking, Professional, Service
from ..services.availability import AvailabilityService
from ..services.notification_dispatcher import send_booking_confirmation
from .sections_helper import get_sections_config, get_sections_order


@xframe_options_exempt
def tenant_landing(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    """Página de landing/mini-site do tenant."""
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    
    # Definir tenant no request para que o context processor possa acessar
    request.tenant = tenant
    
    # Buscar horários padrão da empresa (professional=None)
    availability_rules = AvailabilityRule.objects.filter(
        tenant=tenant,
        professional__isnull=True,
        is_active=True
    ).order_by('weekday', 'start_time')
    
    # Converter para formato para o template
    business_hours = []
    for rule in availability_rules:
        business_hours.append({
            'day_of_week': rule.weekday,
            'day_name': dict(rule.WEEKDAYS)[rule.weekday],
            'start_time': rule.start_time,
            'end_time': rule.end_time,
            'break_start': rule.break_start,
            'break_end': rule.break_end,
        })
    
    # Buscar profissionais ativos do tenant
    professionals = Professional.objects.filter(
        tenant=tenant,
        is_active=True
    ).order_by('display_name')
    
    # Converter amenities e payment methods para listas
    amenities = [a.strip() for a in tenant.amenities.split(",") if a.strip()] if tenant.amenities else []
    payment_methods = [p.strip() for p in tenant.payment_methods.split(",") if p.strip()] if tenant.payment_methods else []
    
    # Obter configurações de branding
    branding = None
    branding_settings = None
    try:
        branding_settings = tenant.branding_settings
        branding = {
            "background_color": branding_settings.background_color,
            "text_color": branding_settings.text_color,
            "button_color_primary": branding_settings.button_color_primary,
            "button_color_secondary": branding_settings.button_color_secondary,
            "use_gradient_buttons": branding_settings.use_gradient_buttons,
            "button_text_color": getattr(branding_settings, "button_text_color", "#FFFFFF"),
            "highlight_color": getattr(branding_settings, "highlight_color", "#FBBF24"),
            "button_hover_color": branding_settings.get_hover_color(branding_settings.button_color_primary),
            "highlight_hover_color": branding_settings.get_hover_color(
                getattr(branding_settings, "highlight_color", branding_settings.button_color_primary)
            ),
        }
    except BrandingSettings.DoesNotExist:
        # Se não houver BrandingSettings, usa cores padrão
        branding = {
            "background_color": "#0F172A",
            "text_color": "#E2E8F0",
            "button_color_primary": "#667EEA",
            "button_color_secondary": "#764BA2",
            "use_gradient_buttons": True,
            "button_text_color": "#FFFFFF",
            "highlight_color": "#FBBF24",
            "button_hover_color": "#8090F6",
            "highlight_hover_color": "#FCC84B",
        }

    sections_config = get_sections_config(branding_settings)
    sections_order = get_sections_order(branding_settings)
    has_social_links = bool(tenant.instagram_url or tenant.facebook_url or tenant.whatsapp_number)
    
    context = {
        "tenant": tenant,
        "business_hours": business_hours,
        "professionals": professionals,
        "amenities": amenities,
        "payment_methods": payment_methods,
        "branding": branding,
        "sections_config": sections_config,
        "sections_order": sections_order,
        "has_social_links": has_social_links,
    }
    return render(request, "scheduling/public/tenant_landing.html", context)


@xframe_options_exempt
def booking_start(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    
    # Definir tenant no request para que o context processor possa acessar
    request.tenant = tenant
    
    form = AvailabilitySearchForm(tenant=tenant, data=request.GET or None)
    available_slots = []
    selected_service = None
    selected_professional = None
    selected_date = None
    available_professionals = []

    # Só processar se houver parâmetros GET (formulário foi submetido)
    if request.GET and form.is_valid():
        selected_service = form.cleaned_data.get("service")
        selected_professional = form.cleaned_data.get("professional")
        selected_date = form.cleaned_data.get("date")

        # Buscar profissionais que fazem o serviço selecionado
        if selected_service:
            available_professionals = list(
                selected_service.professionals.filter(is_active=True).order_by('display_name')
            )

        # Buscar horários se uma data foi informada e:
        # - Um profissional específico foi selecionado, OU
        # - "Qualquer profissional" foi selecionado (professional_id = 'any')
        professional_id_param = request.GET.get('professional')

        if selected_date and (selected_professional or professional_id_param == 'any'):
            availability_service = AvailabilityService(tenant=tenant)

            if professional_id_param == 'any':
                # Buscar slots de TODOS os profissionais e agregar
                all_slots = []
                for prof in available_professionals:
                    prof_slots = availability_service.get_available_slots(
                        service=selected_service,
                        professional=prof,
                        target_date=selected_date,
                    )
                    all_slots.extend(prof_slots)

                # Agrupar por horário (remover duplicatas)
                seen_times = {}
                for slot in all_slots:
                    time_key = slot['start_datetime']
                    if time_key not in seen_times:
                        seen_times[time_key] = slot

                available_slots = sorted(seen_times.values(), key=lambda x: x['start_datetime'])
            else:
                # Buscar slots de um profissional específico
                available_slots = availability_service.get_available_slots(
                    service=selected_service,
                    professional=selected_professional,
                    target_date=selected_date,
                )

    from datetime import date as date_type

    auto_assign_professionals = [prof for prof in available_professionals if getattr(prof, "allow_auto_assign", True)]

    services_queryset = form.fields["service"].queryset
    services = list(services_queryset)
    has_service_categories = any((service.category or "").strip() for service in services)

    # Obter configurações de branding
    branding = None
    try:
        branding_settings = tenant.branding_settings
        branding = {
            "background_color": branding_settings.background_color,
            "text_color": branding_settings.text_color,
            "button_color_primary": branding_settings.button_color_primary,
            "button_color_secondary": branding_settings.button_color_secondary,
            "use_gradient_buttons": branding_settings.use_gradient_buttons,
            
            "button_hover_color": branding_settings.get_hover_color(branding_settings.button_color_primary),
            
        }
    except:
        # Se não houver BrandingSettings, usa cores padrão
        branding = {
            "background_color": "#0F172A",
            "text_color": "#E2E8F0",
            "button_color_primary": "#667EEA",
            "button_color_secondary": "#764BA2",
            "use_gradient_buttons": True,
            "button_hover_color": "#8090F6",
        }

    context = {
        "tenant": tenant,
        "form": form,
        "available_slots": available_slots,
        "selected_service": selected_service,
        "selected_professional": selected_professional,
        "selected_date": selected_date,
        "available_professionals": available_professionals,
        "auto_assign_professionals": auto_assign_professionals,
        "has_auto_assign_professionals": bool(auto_assign_professionals),
        "today": date_type.today(),
        "services": services,
        "has_service_categories": has_service_categories,
        "branding": branding,
    }
    return render(request, "scheduling/public/booking_start.html", context)


@xframe_options_exempt
def booking_confirm(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    
    # Definir tenant no request para que o context processor possa acessar
    request.tenant = tenant
    
    tz = ZoneInfo(tenant.timezone)

    service_id = request.GET.get("service") or request.POST.get("service")
    professional_id = request.GET.get("professional") or request.POST.get("professional")
    start_iso = request.GET.get("start") or request.POST.get("start")

    print(f"DEBUG - booking_confirm chamado:")
    print(f"  service_id: {service_id}")
    print(f"  professional_id: {professional_id}")
    print(f"  start_iso: {start_iso}")

    if not service_id or not start_iso or not professional_id:
        print("DEBUG - Parâmetros faltando, redirecionando...")
        return redirect("public:booking_start", tenant_slug=tenant.slug)

    try:
        service = get_object_or_404(Service, pk=service_id, tenant=tenant, is_active=True)

        print(f"DEBUG - Service: {service.name}")
        print(f"DEBUG - Tentando fazer parse do datetime: {start_iso}")

        # Tentar diferentes formatos de parse
        try:
            start_datetime = datetime.fromisoformat(start_iso)
        except ValueError as e:
            print(f"DEBUG - Erro no fromisoformat: {e}")
            # Tentar remover os dois pontos do timezone (-03:00 -> -0300)
            start_iso_fixed = start_iso.replace(':', '', 2)  # Remove apenas os primeiros 2 ':'
            # Se tiver timezone com :, corrigir
            if start_iso.count(':') >= 3:  # Tem pelo menos hora:minuto:segundo:timezone
                parts = start_iso.rsplit(':', 1)
                if len(parts) == 2 and (parts[1].startswith('+') or parts[1].startswith('-')):
                    start_iso_fixed = start_iso[:-3] + start_iso[-2:]
                else:
                    # Formato normal, tentar com strptime
                    start_datetime = datetime.strptime(start_iso.split('+')[0].split('-')[0], '%Y-%m-%dT%H:%M:%S')
                    start_datetime = start_datetime.replace(tzinfo=tz)
            else:
                start_datetime = datetime.strptime(start_iso.split('+')[0].split('T')[0] + 'T' + start_iso.split('T')[1].split('-')[0], '%Y-%m-%dT%H:%M:%S')
                start_datetime = start_datetime.replace(tzinfo=tz)

        print(f"DEBUG - Datetime parseado: {start_datetime}")

        if start_datetime.tzinfo is None:
            start_datetime = start_datetime.replace(tzinfo=tz)
        else:
            start_datetime = start_datetime.astimezone(tz)

        print(f"DEBUG - Datetime com timezone: {start_datetime}")

        # Validar se a data/hora não está no passado
        from django.utils.timezone import now as django_now
        if start_datetime < django_now():
            print("DEBUG - Data/hora no passado, redirecionando...")
            return redirect("public:booking_start", tenant_slug=tenant.slug)

        # Determinar o profissional
        professional = None
        if professional_id == 'any':
            print("DEBUG - Escolhendo profissional automaticamente (menos ocupado)...")
            # Buscar todos os profissionais que fazem esse serviço
            available_professionals = service.professionals.filter(is_active=True, allow_auto_assign=True)
            target_date = start_datetime.date()

            # Contar agendamentos de cada profissional no mesmo dia
            from django.db.models import Count, Q
            professional_counts = []
            availability_service = AvailabilityService(tenant=tenant)

            for prof in available_professionals:
                # Checar se o profissional está disponível nesse horário
                if availability_service.is_slot_available(service, prof, start_datetime):
                    # Contar agendamentos do dia
                    from datetime import datetime as dt, time
                    start_of_day = dt.combine(target_date, time.min).replace(tzinfo=tz)
                    end_of_day = dt.combine(target_date, time.max).replace(tzinfo=tz)

                    count = Booking.objects.filter(
                        professional=prof,
                        scheduled_for__gte=start_of_day,
                        scheduled_for__lte=end_of_day,
                        status__in=['pending', 'confirmed']
                    ).count()
                    professional_counts.append((prof, count))
                    print(f"DEBUG - {prof.display_name}: {count} agendamentos hoje")

            if professional_counts:
                # Escolher o menos ocupado
                professional_counts.sort(key=lambda x: x[1])
                professional = professional_counts[0][0]
                print(f"DEBUG - Profissional escolhido: {professional.display_name} ({professional_counts[0][1]} agendamentos)")
            else:
                print("DEBUG - Nenhum profissional disponível para esse horário")
                return redirect("public:booking_start", tenant_slug=tenant.slug)

        elif professional_id:
            professional = get_object_or_404(Professional, pk=professional_id, tenant=tenant, is_active=True)

        print(f"DEBUG - Professional: {professional.display_name if professional else 'None'}")

        # Validar disponibilidade do slot
        availability_service = AvailabilityService(tenant=tenant)
        is_available = availability_service.is_slot_available(service, professional, start_datetime)
        print(f"DEBUG - Slot disponível: {is_available}")

        if not is_available:
            print("DEBUG - Slot não disponível, redirecionando...")
            return redirect("public:booking_start", tenant_slug=tenant.slug)
    except Exception as e:
        print(f"DEBUG - ERRO GERAL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise

    if request.method == "POST":
        print("DEBUG - POST recebido, processando form...")
        print(f"DEBUG - POST data: {request.POST}")
        try:
            form = BookingForm(tenant=tenant, data=request.POST, hide_schedule_fields=True)
            print("DEBUG - Form criado")
            if form.is_valid():
                print("DEBUG - Form válido, salvando...")
                booking: Booking = form.save(commit=False)
                booking.tenant = tenant
                print(f"DEBUG - Booking criado: {booking}")
                booking.save()
                print("DEBUG - Booking salvo, enviando notificação...")
                send_booking_confirmation(booking)
                print("DEBUG - Notificação enviada, redirecionando...")
                return redirect("public:booking_success", tenant_slug=tenant.slug)
            else:
                print(f"DEBUG - Form inválido: {form.errors}")
        except Exception as e:
            print(f"DEBUG - ERRO no POST: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    else:
        print("DEBUG - GET, preparando form inicial...")
        initial = {
            "service": service,
            "professional": professional,
            "date": start_datetime.date(),
            "time": start_datetime.time(),
        }
        print(f"DEBUG - Initial data: {initial}")
        try:
            form = BookingForm(tenant=tenant, initial=initial, hide_schedule_fields=True)
            print("DEBUG - Form criado com sucesso")
        except Exception as e:
            print(f"DEBUG - ERRO ao criar form: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise

    print("DEBUG - Renderizando template booking_confirm.html")
    try:
        # Calcular duração e preço específicos do profissional
        duration_minutes = service.duration_for(professional)
        price = service.price_for(professional)
        
        # Obter configurações de branding
        branding = None
        try:
            branding_settings = tenant.branding_settings
            branding = {
                "background_color": branding_settings.background_color,
                "text_color": branding_settings.text_color,
                "button_color_primary": branding_settings.button_color_primary,
                "button_color_secondary": branding_settings.button_color_secondary,
                "use_gradient_buttons": branding_settings.use_gradient_buttons,
                
                "button_hover_color": branding_settings.get_hover_color(branding_settings.button_color_primary),
                
            }
        except:
            # Se não houver BrandingSettings, usa cores padrão
            branding = {
                "background_color": "#0F172A",
                "text_color": "#E2E8F0",
                "button_color_primary": "#667EEA",
                "button_color_secondary": "#764BA2",
                "use_gradient_buttons": True,
                "button_hover_color": "#8090F6",
            }
        
        return render(
            request,
            "scheduling/public/booking_confirm.html",
            {
                "tenant": tenant,
                "form": form,
                "service": service,
                "professional": professional,
                "start_datetime": start_datetime,
                "duration_minutes": duration_minutes,
                "price": price,
                "branding": branding,
            },
        )
    except Exception as e:
        print(f"DEBUG - ERRO ao renderizar template: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


@xframe_options_exempt
def booking_success(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    
    # Definir tenant no request para que o context processor possa acessar
    request.tenant = tenant
    
    # Obter configurações de branding
    branding = None
    try:
        branding_settings = tenant.branding_settings
        branding = {
            "background_color": branding_settings.background_color,
            "text_color": branding_settings.text_color,
            "button_color_primary": branding_settings.button_color_primary,
            "button_color_secondary": branding_settings.button_color_secondary,
            "use_gradient_buttons": branding_settings.use_gradient_buttons,
            
            "button_hover_color": branding_settings.get_hover_color(branding_settings.button_color_primary),
            
        }
    except:
        # Se não houver BrandingSettings, usa cores padrão
        branding = {
            "background_color": "#0F172A",
            "text_color": "#E2E8F0",
            "button_color_primary": "#667EEA",
            "button_color_secondary": "#764BA2",
            "use_gradient_buttons": True,
            "button_hover_color": "#8090F6",
        }
    
    return render(
        request,
        "scheduling/public/booking_success.html",
        {"tenant": tenant, "branding": branding},
    )


def get_service_professionals(request: HttpRequest, tenant_slug: str) -> JsonResponse:
    """API endpoint para retornar profissionais de um serviço em JSON"""
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    service_id = request.GET.get('service_id')

    if not service_id:
        return JsonResponse({'professionals': []})

    try:
        service = Service.objects.get(pk=service_id, tenant=tenant, is_active=True)
        professionals = service.professionals.filter(is_active=True).order_by('display_name')

        professionals_data = []
        for prof in professionals:
            prof_data = {
                'id': prof.id,
                'display_name': prof.display_name,
                'bio': prof.bio or '',
                'color': prof.color,
                'photo_base64': prof.photo_base64 or '',
                'photo_url': prof.photo.url if prof.photo else '',
            }
            professionals_data.append(prof_data)

        return JsonResponse({'professionals': professionals_data})
    except Service.DoesNotExist:
        return JsonResponse({'professionals': []})


def get_available_slots(request: HttpRequest, tenant_slug: str) -> JsonResponse:
    """API endpoint para retornar horários disponíveis em JSON"""
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    service_id = request.GET.get('service_id')
    professional_id = request.GET.get('professional_id')
    date_str = request.GET.get('date')

    print(f"DEBUG - get_available_slots chamado:")
    print(f"  service_id: {service_id}")
    print(f"  professional_id: {professional_id}")
    print(f"  date_str: {date_str}")

    if not service_id or not professional_id or not date_str:
        print("DEBUG - Parâmetros faltando!")
        return JsonResponse({'slots': [], 'error': 'missing_parameters'})

    try:
        from datetime import datetime, date as date_type
        service = Service.objects.get(pk=service_id, tenant=tenant, is_active=True)
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Validar se a data não está no passado
        if target_date < date_type.today():
            print("DEBUG - Data no passado!")
            return JsonResponse({'slots': [], 'error': 'past_date'})

        print(f"DEBUG - Service: {service.name}")
        print(f"DEBUG - Target date: {target_date}")

        availability_service = AvailabilityService(tenant=tenant)

        # Se professional_id == 'any', agregar slots de todos os profissionais
        if professional_id == 'any':
            print("DEBUG - Buscando slots de TODOS os profissionais")
            available_professionals = service.professionals.filter(is_active=True)

            all_slots = []
            for prof in available_professionals:
                prof_slots = availability_service.get_available_slots(
                    service=service,
                    professional=prof,
                    target_date=target_date,
                )
                all_slots.extend(prof_slots)

            # Agrupar por horário (remover duplicatas)
            seen_times = {}
            for slot in all_slots:
                time_key = slot.start
                if time_key not in seen_times:
                    seen_times[time_key] = slot

            available_slots = sorted(seen_times.values(), key=lambda x: x.start)
            print(f"DEBUG - Slots agregados encontrados: {len(available_slots)}")
        else:
            professional = Professional.objects.get(pk=professional_id, tenant=tenant, is_active=True)
            print(f"DEBUG - Professional: {professional.display_name}")

            available_slots = availability_service.get_available_slots(
                service=service,
                professional=professional,
                target_date=target_date,
            )
            print(f"DEBUG - Slots encontrados: {len(available_slots)}")

        slots_data = []
        for slot in available_slots:
            slot_data = {
                'start': slot.start.isoformat(),
                'time': slot.start.strftime('%H:%M'),
                'date': slot.start.strftime('%d/%m/%Y - %A'),
            }
            slots_data.append(slot_data)

        return JsonResponse({'slots': slots_data})
    except (Service.DoesNotExist, Professional.DoesNotExist) as e:
        print(f"DEBUG - Erro: {e}")
        return JsonResponse({'slots': [], 'error': str(e)})


def check_phone(request: HttpRequest, tenant_slug: str) -> JsonResponse:
    """
    API para verificar se um telefone já está cadastrado
    Retorna o nome do cliente se encontrado
    """
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    
    phone = request.GET.get('phone', '').strip()
    
    if not phone:
        return JsonResponse({'exists': False, 'error': 'Telefone não fornecido'})
    
    # Normalizar telefone (remover caracteres especiais)
    import re
    phone_normalized = re.sub(r'[^\d]', '', phone)
    
    # Buscar agendamento mais recente com esse telefone
    from django.db.models import Q
    
    booking = Booking.objects.filter(
        tenant=tenant,
        customer_phone__icontains=phone_normalized[-8:]  # Últimos 8 dígitos
    ).order_by('-created_at').first()
    
    if booking:
        return JsonResponse({
            'exists': True,
            'customer_name': booking.customer_name,
            'customer_phone': booking.customer_phone
        })
    else:
        return JsonResponse({'exists': False})


def my_bookings_login(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    """
    Página de login para acessar meus agendamentos
    """
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    request.tenant = tenant
    
    error_message = None
    
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        
        if not phone:
            error_message = 'Por favor, informe seu telefone'
        else:
            # Normalizar telefone
            import re
            phone_normalized = re.sub(r'[^\d]', '', phone)
            
            # Buscar agendamentos com esse telefone
            bookings = Booking.objects.filter(
                tenant=tenant,
                customer_phone__icontains=phone_normalized[-8:]
            ).exists()
            
            if bookings:
                # Salvar telefone na sessão
                request.session['customer_phone'] = phone_normalized
                request.session['tenant_slug'] = tenant_slug
                return redirect('public:my_bookings', tenant_slug=tenant.slug)
            else:
                error_message = 'Nenhum agendamento encontrado com este telefone'
    
    # Obter branding
    branding = None
    try:
        branding_settings = tenant.branding_settings
        branding = {
            "background_color": branding_settings.background_color,
            "text_color": branding_settings.text_color,
            "button_color_primary": branding_settings.button_color_primary,
            "button_color_secondary": branding_settings.button_color_secondary,
            "button_text_color": branding_settings.button_text_color,
        }
    except:
        branding = {
            "background_color": "#0F172A",
            "text_color": "#E2E8F0",
            "button_color_primary": "#667EEA",
            "button_color_secondary": "#764BA2",
            "button_text_color": "#FFFFFF",
        }
    
    return render(request, 'scheduling/public/my_bookings_login.html', {
        'tenant': tenant,
        'branding': branding,
        'error_message': error_message,
    })


def my_bookings(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    """
    Página de listagem dos agendamentos do cliente
    """
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    request.tenant = tenant
    
    # Verificar se está autenticado
    customer_phone = request.session.get('customer_phone')
    if not customer_phone or request.session.get('tenant_slug') != tenant_slug:
        return redirect('public:my_bookings_login', tenant_slug=tenant.slug)
    
    # Buscar agendamentos do cliente
    from django.utils.timezone import now
    current_time = now()
    
    # Agendamentos futuros
    upcoming_bookings = Booking.objects.filter(
        tenant=tenant,
        customer_phone__icontains=customer_phone[-8:],
        scheduled_for__gte=current_time,
        status__in=['pending', 'confirmed']
    ).select_related('service', 'professional').order_by('scheduled_for')
    
    # Histórico (agendamentos passados ou cancelados)
    past_bookings = Booking.objects.filter(
        tenant=tenant,
        customer_phone__icontains=customer_phone[-8:]
    ).exclude(
        scheduled_for__gte=current_time,
        status__in=['pending', 'confirmed']
    ).select_related('service', 'professional').order_by('-scheduled_for')[:10]
    
    # Obter nome do cliente do primeiro agendamento
    customer_name = ''
    first_booking = Booking.objects.filter(
        tenant=tenant,
        customer_phone__icontains=customer_phone[-8:]
    ).first()
    if first_booking:
        customer_name = first_booking.customer_name
    
    # Obter branding
    branding = None
    try:
        branding_settings = tenant.branding_settings
        branding = {
            "background_color": branding_settings.background_color,
            "text_color": branding_settings.text_color,
            "button_color_primary": branding_settings.button_color_primary,
            "button_color_secondary": branding_settings.button_color_secondary,
            "button_text_color": branding_settings.button_text_color,
        }
    except:
        branding = {
            "background_color": "#0F172A",
            "text_color": "#E2E8F0",
            "button_color_primary": "#667EEA",
            "button_color_secondary": "#764BA2",
            "button_text_color": "#FFFFFF",
        }
    
    return render(request, 'scheduling/public/my_bookings.html', {
        'tenant': tenant,
        'branding': branding,
        'customer_name': customer_name,
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
    })


def logout_bookings(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    """
    Logout da área de meus agendamentos
    """
    if 'customer_phone' in request.session:
        del request.session['customer_phone']
    if 'tenant_slug' in request.session:
        del request.session['tenant_slug']
    
    return redirect('public:tenant_landing', tenant_slug=tenant_slug)


@require_http_methods(["POST"])
def cancel_booking(request: HttpRequest, tenant_slug: str, booking_id: int) -> HttpResponse:
    """
    Cancelar um agendamento
    """
    from django.utils import timezone
    from datetime import timedelta
    from scheduling.models import BookingPolicy
    import json
    
    # Verificar se o cliente está logado
    customer_phone = request.session.get('customer_phone')
    if not customer_phone:
        return JsonResponse({'success': False, 'error': 'Não autenticado'}, status=401)
    
    try:
        tenant = get_object_or_404(Tenant, slug=tenant_slug)
        booking = get_object_or_404(
            Booking,
            id=booking_id,
            tenant=tenant,
            customer_phone=customer_phone
        )
        
        # Obter política de cancelamento
        policy = BookingPolicy.get_or_create_for_tenant(tenant)
        
        # Verificar se cancelamento está permitido
        if not policy.allow_cancellation:
            return JsonResponse({
                'success': False,
                'error': 'Cancelamento não permitido pela política do estabelecimento.'
            }, status=403)
        
        # Verificar se o agendamento já foi cancelado
        if booking.status == 'cancelled':
            return JsonResponse({
                'success': False,
                'error': 'Este agendamento já foi cancelado.'
            }, status=400)
        
        # Verificar se o agendamento já passou
        if booking.scheduled_for < timezone.now():
            return JsonResponse({
                'success': False,
                'error': 'Não é possível cancelar um agendamento que já passou.'
            }, status=400)
        
        # Verificar antecedência mínima
        if policy.min_cancellation_hours > 0:
            min_time = timezone.now() + timedelta(hours=policy.min_cancellation_hours)
            if booking.scheduled_for < min_time:
                return JsonResponse({
                    'success': False,
                    'error': f'Cancelamento deve ser feito com pelo menos {policy.min_cancellation_hours} horas de antecedência.'
                }, status=400)
        
        # Verificar limite de cancelamentos
        if policy.max_cancellations > 0 and policy.cancellation_period_days > 0:
            period_start = timezone.now() - timedelta(days=policy.cancellation_period_days)
            recent_cancellations = Booking.objects.filter(
                tenant=tenant,
                customer_phone=customer_phone,
                status='cancelled',
                updated_at__gte=period_start
            ).count()
            
            if recent_cancellations >= policy.max_cancellations:
                # TODO: Implementar bloqueio de cliente (criar modelo Customer)
                return JsonResponse({
                    'success': False,
                    'error': f'Você atingiu o limite de {policy.max_cancellations} cancelamentos em {policy.cancellation_period_days} dias.'
                }, status=403)
        
        # Obter motivo do cancelamento se exigido
        reason = request.POST.get('reason', '').strip()
        if policy.require_cancellation_reason and not reason:
            return JsonResponse({
                'success': False,
                'error': 'Por favor, informe o motivo do cancelamento.'
            }, status=400)
        
        # Cancelar o agendamento
        booking.status = 'cancelled'
        if reason:
            booking.notes = f"{booking.notes}\n\nMotivo do cancelamento: {reason}" if booking.notes else f"Motivo do cancelamento: {reason}"
        booking.save()
        
        # Notificar gerente se configurado
        if policy.notify_manager_on_abuse:
            if policy.max_cancellations > 0 and policy.cancellation_period_days > 0:
                period_start = timezone.now() - timedelta(days=policy.cancellation_period_days)
                recent_cancellations = Booking.objects.filter(
                    tenant=tenant,
                    customer_phone=customer_phone,
                    status='cancelled',
                    updated_at__gte=period_start
                ).count()
                
                if recent_cancellations >= policy.max_cancellations - 1:
                    # TODO: Enviar notificação para o gerente
                    pass
        
        return JsonResponse({
            'success': True,
            'message': 'Agendamento cancelado com sucesso.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET", "POST"])
def reschedule_booking(request: HttpRequest, tenant_slug: str, booking_id: int) -> HttpResponse:
    """
    Reagendar um agendamento
    """
    from django.utils import timezone
    from datetime import timedelta, datetime
    from scheduling.models import BookingPolicy
    
    # Verificar se o cliente está logado
    customer_phone = request.session.get('customer_phone')
    if not customer_phone:
        return redirect('public:my_bookings_login', tenant_slug=tenant_slug)
    
    tenant = get_object_or_404(Tenant, slug=tenant_slug)
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        tenant=tenant,
        customer__phone=customer_phone
    )
    
    # Obter política de reagendamento
    policy = BookingPolicy.get_or_create_for_tenant(tenant)
    
    # Verificar se reagendamento está permitido
    if not policy.allow_rescheduling:
        messages.error(request, 'Reagendamento não permitido pela política do estabelecimento.')
        return redirect('public:my_bookings', tenant_slug=tenant_slug)
    
    # Verificar se o agendamento já foi cancelado
    if booking.status == 'cancelled':
        messages.error(request, 'Não é possível reagendar um agendamento cancelado.')
        return redirect('public:my_bookings', tenant_slug=tenant_slug)
    
    # Verificar se o agendamento já passou
    if booking.scheduled_for < timezone.now():
        messages.error(request, 'Não é possível reagendar um agendamento que já passou.')
        return redirect('public:my_bookings', tenant_slug=tenant_slug)
    
    # Verificar antecedência mínima
    if policy.min_reschedule_hours > 0:
        min_time = timezone.now() + timedelta(hours=policy.min_reschedule_hours)
        if booking.scheduled_for < min_time:
            messages.error(request, f'Reagendamento deve ser feito com pelo menos {policy.min_reschedule_hours} horas de antecedência.')
            return redirect('public:my_bookings', tenant_slug=tenant_slug)
    
    # Verificar limite de reagendamentos por agendamento
    if policy.max_reschedules_per_booking > 0:
        # Contar reagendamentos deste booking (usando histórico se disponível)
        # Por enquanto, vamos usar um campo metadata
        reschedule_count = booking.metadata.get('reschedule_count', 0) if hasattr(booking, 'metadata') and booking.metadata else 0
        
        if reschedule_count >= policy.max_reschedules_per_booking:
            messages.error(request, f'Este agendamento já foi reagendado {policy.max_reschedules_per_booking} vez(es). Limite atingido.')
            return redirect('public:my_bookings', tenant_slug=tenant_slug)
    
    if request.method == 'POST':
        # Processar reagendamento
        new_datetime_str = request.POST.get('new_datetime')
        
        if not new_datetime_str:
            messages.error(request, 'Por favor, selecione uma nova data e horário.')
            return redirect('public:reschedule_booking', tenant_slug=tenant_slug, booking_id=booking_id)
        
        try:
            # Parse datetime
            new_datetime = datetime.fromisoformat(new_datetime_str.replace('Z', '+00:00'))
            
            # Converter para timezone aware se necessário
            if timezone.is_naive(new_datetime):
                new_datetime = timezone.make_aware(new_datetime)
            
            # Verificar janela de reagendamento
            if policy.reschedule_window_days > 0:
                max_date = timezone.now() + timedelta(days=policy.reschedule_window_days)
                if new_datetime > max_date:
                    messages.error(request, f'O reagendamento deve ser feito dentro de {policy.reschedule_window_days} dias.')
                    return redirect('public:reschedule_booking', tenant_slug=tenant_slug, booking_id=booking_id)
            
            # Verificar se o novo horário está disponível
            # TODO: Implementar verificação de disponibilidade
            
            # Atualizar agendamento
            old_datetime = booking.scheduled_for
            booking.scheduled_for = new_datetime
            
            # Incrementar contador de reagendamentos
            if hasattr(booking, 'metadata') and booking.metadata:
                booking.metadata['reschedule_count'] = booking.metadata.get('reschedule_count', 0) + 1
            else:
                booking.metadata = {'reschedule_count': 1}
            
            # Adicionar nota sobre reagendamento
            reschedule_note = f"\n\nReagendado de {old_datetime.strftime('%d/%m/%Y %H:%M')} para {new_datetime.strftime('%d/%m/%Y %H:%M')}"
            booking.notes = f"{booking.notes}{reschedule_note}" if booking.notes else reschedule_note.strip()
            
            booking.save()
            
            messages.success(request, 'Agendamento reagendado com sucesso!')
            return redirect('public:my_bookings', tenant_slug=tenant_slug)
            
        except ValueError as e:
            messages.error(request, 'Data e horário inválidos.')
            return redirect('public:reschedule_booking', tenant_slug=tenant_slug, booking_id=booking_id)
        except Exception as e:
            messages.error(request, f'Erro ao reagendar: {str(e)}')
            return redirect('public:reschedule_booking', tenant_slug=tenant_slug, booking_id=booking_id)
    
    # GET - mostrar formulário de reagendamento
    branding = tenant.branding if hasattr(tenant, 'branding') else None
    
    return render(request, 'scheduling/public/reschedule_booking.html', {
        'tenant': tenant,
        'booking': booking,
        'policy': policy,
        'branding': branding,
    })

