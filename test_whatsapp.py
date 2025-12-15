#!/usr/bin/env python3
"""
🧪 Script para testar envio de mensagens WhatsApp via Evolution API
Executa: cd src && python ../test_whatsapp.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
django.setup()

from notifications.services import EvolutionApiClient, WhatsappMessage
from scheduling.models import Tenant
from django.conf import settings

print("=" * 80)
print("🧪 TESTE DE WHATSAPP - EVOLUTION API")
print("=" * 80)

# 1️⃣ Verificar configurações
print("\n📋 1. Verificando configurações...")
api_url = getattr(settings, "EVOLUTION_API_URL", "")
api_key = getattr(settings, "EVOLUTION_API_KEY", "")

if not api_url or not api_key:
    print("❌ ERRO: Variáveis EVOLUTION_API_URL ou EVOLUTION_API_KEY não configuradas no .env")
    print(f"   - EVOLUTION_API_URL: {api_url or '❌ NÃO DEFINIDA'}")
    print(f"   - EVOLUTION_API_KEY: {api_key or '❌ NÃO DEFINIDA'}")
    sys.exit(1)

print(f"✅ EVOLUTION_API_URL: {api_url}")
print(f"✅ EVOLUTION_API_KEY: {api_key[:20]}...")

# 2️⃣ Buscar um tenant
print("\n📋 2. Buscando tenant...")
try:
    tenants = Tenant.objects.all()
    if not tenants.exists():
        print("❌ ERRO: Nenhum tenant encontrado no banco de dados")
        print("   Execute: python manage.py shell e crie um tenant")
        sys.exit(1)
    
    tenant = tenants.first()
    print(f"✅ Tenant encontrado: {tenant.name} (slug: {tenant.slug})")
except Exception as e:
    print(f"❌ ERRO ao buscar tenant: {e}")
    sys.exit(1)

# 3️⃣ Testar envio
print("\n📋 3. Testando envio de mensagem...")
print("   ⚠️  Para este teste, você precisa:")
print("      - Um número de WhatsApp real (ex: 5511987654321)")
print("      - A instância de WhatsApp configurada no Evolution API")

numero_teste = input("\n   📱 Digite o número do WhatsApp para teste (ex: 5511987654321): ").strip()

if not numero_teste:
    print("❌ Número inválido")
    sys.exit(1)

try:
    client = EvolutionApiClient(api_url, api_key)
    
    message = WhatsappMessage(
        tenant_slug=tenant.slug,
        to_number=numero_teste,
        message=f"🧪 Teste de WhatsApp - Bora Agendar\n\nSe você recebeu esta mensagem, a integração está funcionando! ✅"
    )
    
    print(f"\n   Enviando para: {numero_teste}")
    print(f"   Mensagem: {message.message}")
    
    resultado = client.send_message(message)
    
    if resultado:
        print("\n✅ SUCESSO! Mensagem enviada com sucesso!")
        print("   Verifique seu WhatsApp para confirmar.")
    else:
        print("\n⚠️  Falha ao enviar. Verifique os logs do servidor Evolution API")
        print("   Possíveis causas:")
        print("   - Número inválido")
        print("   - Instância não conectada no Evolution API")
        print("   - API Key inválida")
        
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ Teste concluído!")
print("=" * 80)
