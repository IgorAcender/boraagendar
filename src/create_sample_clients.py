"""
Script para criar clientes de exemplo no sistema
Execute com: python manage.py shell < create_sample_clients.py
"""

from scheduling.models import Customer
from tenants.models import Tenant

# Pegar o primeiro tenant (ajuste conforme necessário)
tenant = Tenant.objects.first()

if not tenant:
    print("❌ Nenhum tenant encontrado! Crie um tenant primeiro.")
    exit()

print(f"✅ Usando tenant: {tenant.name}")

# Clientes de exemplo
sample_clients = [
    {
        'name': 'Maria Silva',
        'nickname': 'Mari',
        'email': 'maria.silva@email.com',
        'phone': '(11) 98765-4321',
        'cpf': '123.456.789-00',
        'city': 'São Paulo',
        'state': 'SP',
        'tags': 'vip, fidelidade',
        'gender': 'F',
    },
    {
        'name': 'João Santos',
        'email': 'joao.santos@email.com',
        'phone': '(11) 97654-3210',
        'cpf': '987.654.321-00',
        'city': 'São Paulo',
        'state': 'SP',
        'tags': 'primeira-vez',
        'gender': 'M',
    },
    {
        'name': 'Ana Costa',
        'nickname': 'Aninha',
        'email': 'ana.costa@email.com',
        'phone': '(21) 99876-5432',
        'city': 'Rio de Janeiro',
        'state': 'RJ',
        'referred_by': 'Maria Silva',
        'gender': 'F',
    },
    {
        'name': 'Pedro Oliveira',
        'email': 'pedro.oliveira@email.com',
        'phone': '(11) 96543-2109',
        'cpf': '456.789.123-00',
        'city': 'Campinas',
        'state': 'SP',
        'tags': 'desconto-estudante',
        'gender': 'M',
    },
    {
        'name': 'Carla Mendes',
        'email': 'carla.mendes@email.com',
        'phone': '(85) 98765-1234',
        'city': 'Fortaleza',
        'state': 'CE',
        'tags': 'vip',
        'gender': 'F',
        'is_active': True,
    },
]

# Criar clientes
created_count = 0
for client_data in sample_clients:
    client_data['tenant'] = tenant
    
    # Verificar se já existe
    existing = Customer.objects.filter(
        tenant=tenant,
        phone=client_data['phone']
    ).first()
    
    if existing:
        print(f"⚠️  Cliente {client_data['name']} já existe (mesmo telefone)")
        continue
    
    customer = Customer.objects.create(**client_data)
    created_count += 1
    print(f"✅ Cliente criado: {customer.name}")

print(f"\n🎉 Total de clientes criados: {created_count}")
print(f"📊 Total de clientes no sistema: {Customer.objects.filter(tenant=tenant).count()}")
