#!/usr/bin/env python3
"""
🔍 DEBUG: Testar endpoint /api/whatsapp/connect/ direto
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from scheduling.views.whatsapp_manager import whatsapp_create
from tenants.models import Tenant, TenantMembership
import json

print("\n" + "="*70)
print("  🔍 DEBUG: Testando endpoint whatsapp_create")
print("="*70 + "\n")

# Criar client de teste
client = Client()

# Buscar user e tenant
User = get_user_model()
user = User.objects.first()
if not user:
    print("❌ Nenhum usuário no banco!")
    sys.exit(1)

tenant = Tenant.objects.first()
if not tenant:
    print("❌ Nenhum tenant no banco!")
    sys.exit(1)

# Verificar membership
membership = TenantMembership.objects.filter(user=user, tenant=tenant).first()
if not membership:
    print("⚠️  Criando membership de teste...")
    membership = TenantMembership.objects.create(
        user=user,
        tenant=tenant,
        role='owner'
    )
    print(f"✅ Membership criada: {user.email} → {tenant.name}")

print(f"👤 User: {user.email}")
print(f"🏢 Tenant: {tenant.name}")
print(f"🔑 Role: {membership.role}")
print()

# Login
client.force_login(user)

# Fazer request
print("📡 Fazendo POST para /api/whatsapp/connect/...")
print("─" * 70)

try:
    response = client.post(
        '/api/whatsapp/connect/',
        content_type='application/json',
        data=json.dumps({})
    )
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type', 'unknown')}")
    print()
    
    if response.status_code == 200:
        data = json.loads(response.content)
        print("✅ Resposta JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
        print()
        
        if 'qr_code' in data:
            qr = data['qr_code']
            print(f"✅ QR Code presente: {len(qr)} caracteres")
            if qr.startswith('data:image/png;base64,'):
                print("✅ QR Code com prefixo correto")
            else:
                print("⚠️  QR Code sem prefixo data:image")
        else:
            print("❌ QR Code NÃO está na resposta!")
            print(f"Keys presentes: {list(data.keys())}")
    else:
        print(f"❌ Status {response.status_code}")
        print(f"Response: {response.content.decode()[:500]}")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70 + "\n")
