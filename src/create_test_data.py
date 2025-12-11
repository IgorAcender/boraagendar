"""
Script para gerar dados de teste no dashboard
Cria agendamentos fictícios para visualizar os gráficos
"""

import os
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from scheduling.models import Booking, Tenant, Service, Professional

def create_test_data():
    """Criar agendamentos de teste para preencher gráficos"""
    
    try:
        tenant = Tenant.objects.get(slug='test-clinic')
        print(f"✓ Usando tenant: {tenant.name}")
    except Tenant.DoesNotExist:
        print("❌ Tenant 'test-clinic' não encontrado")
        return
    
    # Garantir que existem serviços
    services = Service.objects.filter(tenant=tenant)
    if services.count() == 0:
        print("❌ Nenhum serviço encontrado. Criando...")
        services = [
            Service.objects.create(
                tenant=tenant,
                name='Corte de Cabelo',
                slug='corte-cabelo',
                duration_minutes=30,
                price=50.00
            ),
            Service.objects.create(
                tenant=tenant,
                name='Barba',
                slug='barba',
                duration_minutes=20,
                price=30.00
            ),
            Service.objects.create(
                tenant=tenant,
                name='Hidratação',
                slug='hidratacao',
                duration_minutes=45,
                price=80.00
            ),
        ]
    else:
        services = list(services)
    
    print(f"✓ Serviços: {len(services)}")
    
    # Garantir que existem profissionais
    professionals = Professional.objects.filter(tenant=tenant, is_active=True)
    if professionals.count() == 0:
        print("❌ Nenhum profissional encontrado. Criando...")
        professionals = [
            Professional.objects.create(
                tenant=tenant,
                display_name='João Silva',
                slug='joao-silva',
                is_active=True
            ),
            Professional.objects.create(
                tenant=tenant,
                display_name='Maria Santos',
                slug='maria-santos',
                is_active=True
            ),
            Professional.objects.create(
                tenant=tenant,
                display_name='Pedro Oliveira',
                slug='pedro-oliveira',
                is_active=True
            ),
        ]
        for prof in professionals:
            prof.services.set(services)
    else:
        professionals = list(professionals)
    
    print(f"✓ Profissionais: {len(professionals)}")
    
    # ===================== GERAR DADOS DOS ÚLTIMOS 7 DIAS =====================
    print("\n📊 Gerando dados dos últimos 7 dias...")
    
    now = timezone.now()
    for i in range(7):
        date = now - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Gerar 2-4 agendamentos por dia
        num_bookings = random.randint(2, 4)
        
        for j in range(num_bookings):
            # Hora aleatória do dia (09:00 até 17:00)
            hour = random.randint(9, 17)
            minute = random.choice([0, 15, 30, 45])
            
            scheduled_time = date_start.replace(hour=hour, minute=minute)
            
            service = random.choice(services)
            professional = random.choice(professionals)
            
            Booking.objects.create(
                tenant=tenant,
                service=service,
                professional=professional,
                customer_name=f'Cliente Teste {random.randint(1000, 9999)}',
                customer_phone='11987654321',
                customer_email='cliente@example.com',
                scheduled_for=scheduled_time,
                duration_minutes=service.duration_minutes,
                price=service.price,
                status='confirmed',  # Sempre confirmado
                notes='Agendamento de teste'
            )
        
        print(f"  ✓ {num_bookings} agendamentos em {date.strftime('%d/%m/%Y')}")
    
    # ===================== GERAR DADOS DOS ÚLTIMOS 12 MESES =====================
    print("\n📊 Gerando dados dos últimos 12 meses...")
    
    for month_offset in range(12):
        # Calcular primeiro dia do mês
        date = now - timedelta(days=30 * month_offset)
        month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Gerar 15-30 agendamentos por mês
        num_bookings = random.randint(15, 30)
        
        for j in range(num_bookings):
            # Data aleatória do mês
            day = random.randint(1, 28)
            hour = random.randint(9, 17)
            minute = random.choice([0, 15, 30, 45])
            
            try:
                scheduled_time = month_start.replace(day=day, hour=hour, minute=minute)
            except ValueError:
                # Se o dia não existe (ex: 30 de fevereiro)
                continue
            
            service = random.choice(services)
            professional = random.choice(professionals)
            
            Booking.objects.create(
                tenant=tenant,
                service=service,
                professional=professional,
                customer_name=f'Cliente Teste {random.randint(1000, 9999)}',
                customer_phone='11987654321',
                customer_email='cliente@example.com',
                scheduled_for=scheduled_time,
                duration_minutes=service.duration_minutes,
                price=service.price,
                status='confirmed',  # Sempre confirmado
                notes='Agendamento de teste'
            )
        
        print(f"  ✓ {num_bookings} agendamentos em {month_start.strftime('%b/%Y')}")
    
    print("\n✅ Dados de teste criados com sucesso!")
    print(f"📈 Total de agendamentos: {Booking.objects.filter(tenant=tenant).count()}")
    print(f"💰 Total de receita: R$ {sum(b.price for b in Booking.objects.filter(tenant=tenant)):.2f}")

if __name__ == '__main__':
    create_test_data()
