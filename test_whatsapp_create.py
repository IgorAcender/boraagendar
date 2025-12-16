#!/usr/bin/env python
"""
Script de teste para verificar se a view whatsapp_create funciona
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from tenants.models import Tenant, TenantMembership
from scheduling.models import EvolutionAPI, WhatsAppInstance
import json

User = get_user_model()

print("🔍 Testando WhatsApp Create View")
print("=" * 60)

# 1. Criar ou obter tenant
try:
    tenant = Tenant.objects.first()
    if not tenant:
        tenant = Tenant.objects.create(name="Test Tenant")
        print(f"✅ Tenant criado: {tenant.name}")
    else:
        print(f"✅ Tenant encontrado: {tenant.name}")
except Exception as e:
    print(f"❌ Erro ao criar tenant: {e}")
    sys.exit(1)

# 2. Criar ou obter usuário
try:
    user = User.objects.filter(username='testuser').first()
    if not user:
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        print(f"✅ Usuário criado: {user.username}")
    else:
        print(f"✅ Usuário encontrado: {user.username}")
except Exception as e:
    print(f"❌ Erro ao criar usuário: {e}")
    sys.exit(1)

# 3. Criar membership
try:
    membership = TenantMembership.objects.filter(
        tenant=tenant,
        user=user
    ).first()
    if not membership:
        membership = TenantMembership.objects.create(
            tenant=tenant,
            user=user,
            role='owner'
        )
        print(f"✅ Membership criado")
    else:
        print(f"✅ Membership encontrado")
except Exception as e:
    print(f"❌ Erro ao criar membership: {e}")
    sys.exit(1)

# 4. Criar ou obter Evolution API
try:
    evo_api = EvolutionAPI.objects.filter(is_active=True).first()
    if not evo_api:
        evo_api = EvolutionAPI.objects.create(
            instance_id="test_instance",
            api_url="http://localhost:8080",
            api_key="test_key",
            is_active=True,
            capacity=5,
            priority=1
        )
        print(f"✅ Evolution API criada: {evo_api.instance_id}")
    else:
        print(f"✅ Evolution API encontrada: {evo_api.instance_id}")
except Exception as e:
    print(f"❌ Erro ao criar Evolution API: {e}")
    sys.exit(1)

# 5. Testar a view
print("\n📡 Testando a view whatsapp_create...")
print("-" * 60)

client = Client()
client.login(username='testuser', password='testpass123')

# Primeiro, definir o tenant na sessão
session = client.session
session['selected_tenant_id'] = tenant.id
session.save()

try:
    response = client.post(
        '/dashboard/whatsapp/criar/',
        data=json.dumps({}),
        content_type='application/json',
        HTTP_X_CSRF_TOKEN=client.post('/dashboard/whatsapp/').cookies.get('csrftoken')
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type')}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response JSON: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            print(f"\n✅ QR CODE GERADO COM SUCESSO!")
            print(f"   Telefone: {data.get('phone_number')}")
            print(f"   ID WhatsApp: {data.get('whatsapp_id')}")
        else:
            print(f"\n❌ Erro: {data.get('error')}")
    else:
        print(f"❌ Status {response.status_code}")
        print(f"Response: {response.content.decode()}")
        
except Exception as e:
    print(f"❌ Erro ao fazer requisição: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
