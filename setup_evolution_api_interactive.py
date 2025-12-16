#!/usr/bin/env python3
"""
Setup rápido da Evolution API para o dashboard WhatsApp
Execute este script APENAS se você já tiver Evolution API rodando
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
django.setup()

from scheduling.models import EvolutionAPI

print("\n" + "="*70)
print("  ⚙️  SETUP: Configurar Evolution API")
print("="*70 + "\n")

# Perguntar dados da Evolution API
print("Forneça os dados de sua Evolution API:\n")

api_url = input("🔗 URL da Evolution API (ex: http://192.168.1.100:8080): ").strip()
instance_id = input("📦 Instance ID (ex: BORA_AGENDAR_1): ").strip()
api_key = input("🔑 API Key: ").strip()

if not all([api_url, instance_id, api_key]):
    print("\n❌ Erro: Todos os campos são obrigatórios!")
    sys.exit(1)

print(f"\n📝 Configuração:")
print(f"   URL: {api_url}")
print(f"   Instance ID: {instance_id}")
print(f"   API Key: {'*' * (len(api_key) - 4) + api_key[-4:]}")
print()

# Verificar se já existe
existing = EvolutionAPI.objects.filter(instance_id=instance_id).first()
if existing:
    print(f"⚠️  Já existe uma Evolution API com Instance ID '{instance_id}'")
    update = input("   Atualizar? (s/n): ").strip().lower()
    if update == 's':
        existing.api_url = api_url
        existing.api_key = api_key
        existing.is_active = True
        existing.save()
        print(f"✅ Atualizado com sucesso!")
    else:
        print("❌ Cancelado")
        sys.exit(1)
else:
    evo_api = EvolutionAPI.objects.create(
        instance_id=instance_id,
        api_url=api_url,
        api_key=api_key,
        is_active=True,
        capacity=10,
        priority=1
    )
    print(f"✅ Evolution API criada com sucesso!")

print()
print("="*70)
print("\n🧪 Próximo passo: Testar a conexão")
print("   Execute: python3 test_evolution_api_response.py\n")
print("="*70 + "\n")
