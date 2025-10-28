from datetime import datetime
from zoneinfo import ZoneInfo
import json

from django.http import HttpRequest, HttpResponse, JsonResponse
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

    context = {
        "tenant": tenant,
        "form": form,
        "available_slots": available_slots,
        "selected_service": selected_service,
        "selected_professional": selected_professional,
        "selected_date": selected_date,
        "available_professionals": available_professionals,
    }
    return render(request, "scheduling/public/booking_start.html", context)


def booking_confirm(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    tz = ZoneInfo(tenant.timezone)

    service_id = request.GET.get("service") or request.POST.get("service")
    professional_id = request.GET.get("professional") or request.POST.get("professional")
    start_iso = request.GET.get("start") or request.POST.get("start")

    print(f"DEBUG - booking_confirm chamado:")
    print(f"  service_id: {service_id}")
    print(f"  professional_id: {professional_id}")
    print(f"  start_iso: {start_iso}")

    if not service_id or not start_iso:
        print("DEBUG - Parâmetros faltando, redirecionando...")
        return redirect("public:booking_start", tenant_slug=tenant.slug)

    try:
        service = get_object_or_404(Service, pk=service_id, tenant=tenant, is_active=True)
        professional = None

        # Se professional_id == 'any', escolher o menos ocupado automaticamente
        if professional_id == 'any':
            print("DEBUG - Escolhendo profissional automaticamente (menos ocupado)...")
            # Buscar todos os profissionais que fazem esse serviço
            available_professionals = service.professionals.filter(is_active=True)

            # Parse do horário para pegar a data
            try:
                start_datetime = datetime.fromisoformat(start_iso)
            except ValueError:
                start_datetime = datetime.strptime(start_iso.split('+')[0].split('-')[0], '%Y-%m-%dT%H:%M:%S')
                start_datetime = start_datetime.replace(tzinfo=tz)

            if start_datetime.tzinfo is None:
                start_datetime = start_datetime.replace(tzinfo=tz)

            target_date = start_datetime.date()

            # Contar agendamentos de cada profissional no mesmo dia
            from django.db.models import Count, Q
            professional_counts = []
            for prof in available_professionals:
                # Checar se o profissional está disponível nesse horário
                availability_service = AvailabilityService(tenant=tenant)
                if availability_service.is_slot_available(service, prof, start_datetime):
                    # Contar agendamentos do dia
                    count = Booking.objects.filter(
                        professional=prof,
                        date=target_date,
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

        print(f"DEBUG - Service: {service.name}")
        print(f"DEBUG - Professional: {professional.display_name if professional else 'None'}")
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
    except Exception as e:
        print(f"DEBUG - ERRO ao renderizar template: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


def booking_success(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    return render(
        request,
        "scheduling/public/booking_success.html",
        {"tenant": tenant},
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
