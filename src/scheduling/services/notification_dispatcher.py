from datetime import datetime
from zoneinfo import ZoneInfo

from django.utils import timezone

from notifications.services import EvolutionApiClient, WhatsappMessage


def send_booking_confirmation(booking) -> bool:
    tenant = booking.tenant
    tz = ZoneInfo(tenant.timezone or "America/Sao_Paulo")
    appointment_time = timezone.localtime(booking.scheduled_for, tz)
    message = (
        f"Ola {booking.customer_name}, aqui e {tenant.name}. "
        f"Seu horario para {booking.service.name} com {booking.professional.display_name} "
        f"esta marcado para {appointment_time:%d/%m %H:%M}."
    )
    client = EvolutionApiClient()
    payload = WhatsappMessage(
        tenant_slug=tenant.slug,
        to_number=booking.customer_phone,
        message=message,
    )
    return client.send_message(payload)
