#!/usr/bin/env python3
"""
Script simples para criar Evolution API
Execute: python3 setup_evolution_quick.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
django.setup()

from scheduling.models import EvolutionAPI
from django.conf import settings

print("\n" + "="*70)
print("  🚀 SETUP EVOLUTION API - BORA AGENDAR")
print("="*70)

# 1. Verificar se já existe
existing = EvolutionAPI.objects.all()
print(f"\n📊 Evolution APIs existentes: {existing.count()}")

if existing.count() > 0:
    for api in existing:
        print(f"\n   ✅ {api.instance_id}")
        print(f"      - URL: {api.api_url}")
        print(f"      - Ativa: {api.is_active}")
        print(f"      - WhatsApps: {api.whatsapp_instances.count()}")
    
    print("\n✅ Você já tem Evolution API configurada!")
    print("   Agora tente conectar um WhatsApp no dashboard.\n")
    sys.exit(0)

# 2. Criar nova
print("\n➕ Nenhuma Evolution API encontrada. Criando uma padrão...")

try:
    api_url = getattr(settings, 'EVOLUTION_API_URL', 'http://localhost:8080/api')
    instance_name = getattr(settings, 'EVOLUTION_INSTANCE_NAME', 'default')
    
    evo = EvolutionAPI.objects.create(
        instance_id=instance_name or 'default',
        api_url=api_url,
        api_key='temp-key-configure-depois',
        is_active=True,
        capacity=10,
        priority=1
    )
    
    print(f"\n✅ Evolution API criada com sucesso!")
    print(f"   ID no banco: {evo.id}")
    print(f"   Instance: {evo.instance_id}")
    print(f"   URL: {evo.api_url}")
    print(f"   Ativa: {evo.is_active}")
    print(f"   Capacidade: {evo.capacity}")
    
    print("\n🎉 Pronto! Agora você pode:")
    print("   1. Voltar ao dashboard")
    print("   2. Clicar em 'Conectar WhatsApp'")
    print("   3. O QR code deve aparecer! 📱")
    
except Exception as e:
    print(f"\n❌ Erro ao criar Evolution API: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70 + "\n")
