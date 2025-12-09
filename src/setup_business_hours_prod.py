"""
Script para popular os horários de funcionamento padrão dos tenants.
Execute com: python3 manage.py shell < setup_business_hours_prod.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

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

print("=" * 60)
print("🚀 CONFIGURANDO HORÁRIOS DE FUNCIONAMENTO")
print("=" * 60)

total_created = 0
total_existing = 0

# Criar horários para todos os tenants que não têm
for tenant in Tenant.objects.all():
    print(f"\n📍 {tenant.name} ({tenant.slug})")
    print("-" * 60)
    
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
        
        day_name = business_hour.get_day_of_week_display()
        
        if created:
            total_created += 1
            status = "FECHADO" if business_hour.is_closed else f"{opening_time.strftime('%H:%M')} - {closing_time.strftime('%H:%M')}"
            print(f"  ✅ {day_name}: {status}")
        else:
            total_existing += 1
            status = "FECHADO" if business_hour.is_closed else f"{business_hour.opening_time.strftime('%H:%M')} - {business_hour.closing_time.strftime('%H:%M')}"
            print(f"  ⏭️  {day_name}: {status} (já existe)")

print("\n" + "=" * 60)
print("✨ SETUP CONCLUÍDO!")
print("=" * 60)
print(f"📊 Novos horários criados: {total_created}")
print(f"📊 Horários existentes: {total_existing}")
print("\n✅ Os horários devem aparecer no site agora!")
print("=" * 60)
