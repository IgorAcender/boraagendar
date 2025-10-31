#!/usr/bin/env python
import os
import sys
import django

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, TenantMembership
from scheduling.models import Service, Professional

User = get_user_model()

def create_test_data():
    print("🏗️ Criando dados de teste...")
    
    # Criar usuário admin se não existir
    admin_user, created = User.objects.get_or_create(
        email='admin@test.com',
        defaults={
            'is_superuser': True,
            'is_staff': True,
            'first_name': 'Admin',
            'last_name': 'User'
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Usuário admin criado: {admin_user.email}")
    else:
        print(f"ℹ️ Usuário admin já existe: {admin_user.email}")
    
    # Criar tenant de teste
    tenant, created = Tenant.objects.get_or_create(
        slug='test-clinic',
        defaults={
            'name': 'Clínica de Teste',
            'phone_number': '(11) 99999-9999',
            'email': 'contato@test-clinic.com'
        }
    )
    if created:
        print(f"✅ Tenant criado: {tenant.name}")
    else:
        print(f"ℹ️ Tenant já existe: {tenant.name}")
    
    # Criar membership do admin no tenant
    membership, created = TenantMembership.objects.get_or_create(
        user=admin_user,
        tenant=tenant,
        defaults={
            'role': 'owner',
            'is_active': True
        }
    )
    if created:
        print(f"✅ Membership criado para {admin_user.email} no tenant {tenant.name}")
    else:
        print(f"ℹ️ Membership já existe para {admin_user.email} no tenant {tenant.name}")
    
    # Criar serviços de teste
    services_data = [
        {'name': 'Consulta Médica', 'description': 'Consulta médica geral', 'duration_minutes': 30, 'price': 150.00},
        {'name': 'Exame de Sangue', 'description': 'Coleta de sangue para exames', 'duration_minutes': 15, 'price': 80.00},
        {'name': 'Fisioterapia', 'description': 'Sessão de fisioterapia', 'duration_minutes': 60, 'price': 120.00},
    ]
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            tenant=tenant,
            name=service_data['name'],
            defaults=service_data
        )
        if created:
            print(f"✅ Serviço criado: {service.name}")
        else:
            print(f"ℹ️ Serviço já existe: {service.name}")
    
    # Criar profissionais de teste
    professionals_data = [
        {'display_name': 'Dr. João Silva', 'color': '#3b82f6'},
        {'display_name': 'Dra. Maria Santos', 'color': '#ef4444'},
        {'display_name': 'Dr. Pedro Oliveira', 'color': '#10b981'},
    ]
    
    for prof_data in professionals_data:
        professional, created = Professional.objects.get_or_create(
            tenant=tenant,
            display_name=prof_data['display_name'],
            defaults={
                'color': prof_data['color'],
                'is_active': True
            }
        )
        if created:
            print(f"✅ Profissional criado: {professional.display_name}")
            # Associar todos os serviços a todos os profissionais
            professional.services.set(Service.objects.filter(tenant=tenant))
        else:
            print(f"ℹ️ Profissional já existe: {professional.display_name}")
    
    print("🎉 Dados de teste criados com sucesso!")
    print(f"👤 Usuário: admin@test.com / admin123")
    print(f"🏢 Tenant: {tenant.slug}")
    print(f"🔗 URL: http://127.0.0.1:8001/")

if __name__ == '__main__':
    create_test_data()