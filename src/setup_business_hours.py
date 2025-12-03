"""
Script para popular os horários de funcionamento padrão dos tenants.
Execute com: python manage.py shell < setup_business_hours.py
"""

from tenants.models import Tenant, BusinessHours
from datetime import time

# Horários padrão
DEFAULT_HOURS = {
    0: (time(9, 0), time(18, 0)),      # Segunda
    1: (time(9, 0), time(18, 0)),      # Terça
    2: (time(9, 0), time(18, 0)),      # Quarta
    3: (time(9, 0), time(18, 0)),      # Quinta
    4: (time(9, 0), time(18, 0)),      # Sexta
    5: (time(9, 0), time(15, 0)),      # Sábado
    6: (None, None),                    # Domingo (Fechado)
}

# Criar horários para todos os tenants que não têm
for tenant in Tenant.objects.all():
    for day_of_week, (opening_time, closing_time) in DEFAULT_HOURS.items():
        business_hour, created = BusinessHours.objects.get_or_create(
            tenant=tenant,
            day_of_week=day_of_week,
            defaults={
                'is_closed': opening_time is None,
                'opening_time': opening_time,
                'closing_time': closing_time,
            }
        )
        if created:
            status = "FECHADO" if business_hour.is_closed else f"{opening_time.strftime('%H:%M')} - {closing_time.strftime('%H:%M')}"
            print(f"✅ {tenant.name} - {business_hour.get_day_of_week_display()}: {status}")
        else:
            print(f"⏭️  {tenant.name} - {business_hour.get_day_of_week_display()}: Já existe")

print("\n✨ Setup concluído!")
