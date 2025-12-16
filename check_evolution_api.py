#!/usr/bin/env python
"""
Script para verificar e criar Evolution API se necessário
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
django.setup()

from scheduling.models import EvolutionAPI, WhatsAppInstance
from tenants.models import Tenant
from django.conf import settings

print("🔍 Verificando Evolution API...")
print("=" * 70)

# 1. Verificar Evolution API no banco
try:
    evolution_apis = EvolutionAPI.objects.all()
    print(f"\n📊 Total de Evolution APIs no banco: {evolution_apis.count()}")
    
    if evolution_apis.count() == 0:
        print("❌ Nenhuma Evolution API cadastrada!")
    else:
        for api in evolution_apis:
            print(f"\n  📡 {api.instance_id}")
            print(f"     - URL: {api.api_url}")
            print(f"     - Ativo: {api.is_active}")
            print(f"     - Capacidade: {api.capacity}")
            print(f"     - Uso: {api.whatsapp_instances.count()}")
except Exception as e:
    print(f"❌ Erro ao consultar DB: {e}")
    sys.exit(1)

# 2. Verificar settings
print(f"\n⚙️  Verificando settings...")
print(f"   - EVOLUTION_API_URL: {getattr(settings, 'EVOLUTION_API_URL', 'NÃO CONFIGURADA')}")
print(f"   - EVOLUTION_INSTANCE_NAME: {getattr(settings, 'EVOLUTION_INSTANCE_NAME', 'NÃO CONFIGURADA')}")

# 3. Criar exemplo se não existir
if evolution_apis.count() == 0:
    print("\n➕ Criando Evolution API de exemplo...")
    try:
        evo = EvolutionAPI.objects.create(
            instance_id=getattr(settings, 'EVOLUTION_INSTANCE_NAME', 'default'),
            api_url=getattr(settings, 'EVOLUTION_API_URL', 'http://localhost:8080/api'),
            api_key='sua-chave-aqui',
            is_active=True,
            capacity=10,
            priority=1
        )
        print(f"✅ Evolution API criada: {evo.instance_id}")
        print(f"   ID: {evo.id}")
        
        # 4. Testar criação de WhatsApp
        tenant = Tenant.objects.first()
        if tenant:
            print(f"\n✅ Tenant encontrado: {tenant.name}")
            print(f"   Agora tente criar um WhatsApp no dashboard!")
        else:
            print(f"\n⚠️  Nenhum Tenant cadastrado. Crie um antes de usar.")
            
    except Exception as e:
        print(f"❌ Erro ao criar Evolution API: {e}")
        sys.exit(1)

print("\n" + "=" * 70)
print("✅ Verificação concluída!")
