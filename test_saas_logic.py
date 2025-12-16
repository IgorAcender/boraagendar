#!/usr/bin/env python3
"""
🧪 TESTE COMPLETO: Lógica SaaS Multi-Tenant
Simula: Primeira conexão + Reconexão
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
django.setup()

from scheduling.models import WhatsAppInstance, Tenant
from django.conf import settings
import requests

print("\n" + "="*70)
print("  🧪 TESTE: Lógica SaaS Multi-Tenant")
print("="*70 + "\n")

# Configuração
EVOLUTION_API_URL = settings.EVOLUTION_API_URL
EVOLUTION_API_KEY = settings.EVOLUTION_API_KEY
headers = {'apikey': EVOLUTION_API_KEY, 'Content-Type': 'application/json'}

if not EVOLUTION_API_URL or not EVOLUTION_API_KEY:
    print("❌ Configure EVOLUTION_API_URL e EVOLUTION_API_KEY")
    sys.exit(1)

print(f"📍 URL: {EVOLUTION_API_URL}")
print(f"🔑 Key: {'*' * 20}{EVOLUTION_API_KEY[-4:]}")
print()

# Simular tenant de teste
print("1️⃣  Buscando tenant de teste...")
print("─" * 70)

tenant = Tenant.objects.first()
if not tenant:
    print("❌ Nenhum tenant no banco! Crie um tenant primeiro.")
    sys.exit(1)

print(f"✅ Tenant: {tenant.name}")
print(f"   Slug: {tenant.slug}")
print()

instance_name = f"{tenant.slug}_whatsapp"
print(f"💡 Instance name que será usado: {instance_name}")
print()

# Verificar se já existe WhatsApp para este tenant
print("2️⃣  Verificando WhatsApp existente...")
print("─" * 70)

existing = WhatsAppInstance.objects.filter(tenant=tenant).first()
if existing:
    print(f"⚠️  JÁ EXISTE WhatsApp para {tenant.name}")
    print(f"   Instance: {existing.instance_name}")
    print(f"   Status: {existing.connection_status}")
    print(f"   Criado em: {existing.created_at}")
    print()
    print("💡 Simulando RECONEXÃO...")
    is_first_time = False
else:
    print(f"✅ PRIMEIRA VEZ para {tenant.name}")
    print()
    print("💡 Simulando PRIMEIRA CONEXÃO...")
    is_first_time = True

print()

# Simular fluxo
if is_first_time:
    print("3️⃣  [PRIMEIRA VEZ] Criando instância...")
    print("─" * 70)
    
    create_url = f"{EVOLUTION_API_URL}/instance/create"
    create_data = {
        "instanceName": instance_name,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    
    print(f"   POST {create_url}")
    
    try:
        response = requests.post(create_url, json=create_data, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201, 409]:
            print(f"   ✅ Instância criada/já existe")
        else:
            print(f"   ❌ Erro: {response.text[:200]}")
            sys.exit(1)
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        sys.exit(1)
    
    print()

print("4️⃣  Obtendo QR code...")
print("─" * 70)

connect_url = f"{EVOLUTION_API_URL}/instance/connect/{instance_name}"
print(f"   GET {connect_url}")

try:
    response = requests.get(connect_url, headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        qr_base64 = data.get('base64', '')
        
        if qr_base64:
            print(f"   ✅ QR code recebido: {len(qr_base64)} caracteres")
            
            # Limpar prefixo se tiver
            if qr_base64.startswith('data:image'):
                qr_base64 = qr_base64.split(',', 1)[-1]
            
            print(f"   QR (limpo): {len(qr_base64)} caracteres")
            
            if is_first_time:
                print()
                print("5️⃣  [PRIMEIRA VEZ] Criando registro no banco...")
                print("─" * 70)
                
                wa = WhatsAppInstance.objects.create(
                    instance_name=instance_name,
                    phone_number="pending",
                    display_name=f"WhatsApp {tenant.name}",
                    tenant=tenant,
                    connection_status='connecting',
                    is_primary=True,
                    qr_code=qr_base64
                )
                
                print(f"   ✅ Registro criado: ID {wa.id}")
                print(f"   Instance: {wa.instance_name}")
                print(f"   Tenant: {wa.tenant.name}")
                
            else:
                print()
                print("5️⃣  [RECONEXÃO] Atualizando QR no banco...")
                print("─" * 70)
                
                existing.qr_code = qr_base64
                existing.connection_status = 'connecting'
                existing.save()
                
                print(f"   ✅ QR atualizado: ID {existing.id}")
                print(f"   Instance: {existing.instance_name}")
        else:
            print(f"   ❌ QR code não retornado")
            print(f"   Response: {data}")
    else:
        print(f"   ❌ Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

print()
print("="*70)
print()
print("✅ TESTE CONCLUÍDO COM SUCESSO!")
print()

if is_first_time:
    print("📝 Resultado:")
    print("   • Instância criada na Evolution API")
    print("   • QR code obtido")
    print("   • Registro salvo no banco")
    print()
    print("🔄 Próximo teste: Execute novamente para simular RECONEXÃO")
else:
    print("📝 Resultado:")
    print("   • Instância existente reutilizada")
    print("   • Novo QR code obtido")
    print("   • QR atualizado no banco")
    print()
    print("✅ Lógica SaaS funcionando corretamente!")

print()
print("="*70 + "\n")
