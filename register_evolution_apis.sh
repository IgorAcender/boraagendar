#!/bin/bash
# Script para registrar as 2 Evolution APIs no Django

cd "$(dirname "$0")/src"

echo "=================================="
echo "📝 REGISTRANDO EVOLUTION APIs"
echo "=================================="
echo ""

# Achar domínio do .env
MAIN_DOMAIN=$(grep "ALLOWED_HOSTS=" ../.env | cut -d'=' -f2 | tr -d ' ')

echo "Domínio detectado: $MAIN_DOMAIN"
echo ""
echo "⚠️  IMPORTANTE: Configure os domínios das Evolution APIs corretamente!"
echo "   - Evolution API 1: https://evo1.$MAIN_DOMAIN (ou seu domínio específico)"
echo "   - Evolution API 2: https://evo2.$MAIN_DOMAIN (ou seu domínio específico)"
echo ""

python3 manage.py shell << 'PYTHON_CODE'
from scheduling.models import EvolutionAPI

print("\n🔧 Criando Evolution APIs...\n")

# Evolution API 1
try:
    evo1, created = EvolutionAPI.objects.get_or_create(
        name="Evolution API 1",
        defaults={
            "url": "https://evo1.robo-de-agendamento-igor.ivhjcm.easypanel.host/message/sendText",
            "api_key": "429683C4C977415CAAFCCE10F7D57E11",
            "whatsapp_capacity": 50,
            "whatsapp_connected": 0,
            "is_active": True,
            "priority": 10,
            "notes": "Primeira instância - Prioridade alta"
        }
    )
    if created:
        print("✅ Evolution API 1 criada com sucesso")
        print(f"   URL: {evo1.url}")
        print(f"   Prioridade: {evo1.priority}")
    else:
        print("ℹ️  Evolution API 1 já existe")
except Exception as e:
    print(f"❌ Erro ao criar Evolution API 1: {e}")

# Evolution API 2
try:
    evo2, created = EvolutionAPI.objects.get_or_create(
        name="Evolution API 2",
        defaults={
            "url": "https://evo2.robo-de-agendamento-igor.ivhjcm.easypanel.host/message/sendText",
            "api_key": "429683C4C977415CAAFCCE10F7D57E11",
            "whatsapp_capacity": 50,
            "whatsapp_connected": 0,
            "is_active": True,
            "priority": 5,
            "notes": "Segunda instância - Prioridade média (failover)"
        }
    )
    if created:
        print("✅ Evolution API 2 criada com sucesso")
        print(f"   URL: {evo2.url}")
        print(f"   Prioridade: {evo2.priority}")
    else:
        print("ℹ️  Evolution API 2 já existe")
except Exception as e:
    print(f"❌ Erro ao criar Evolution API 2: {e}")

# Resumo
print("\n📊 RESUMO\n")
evos = EvolutionAPI.objects.all().order_by("-priority")
print(f"Total de Evolution APIs: {evos.count()}\n")

for evo in evos:
    status = "✅ Ativa" if evo.is_active else "❌ Inativa"
    print(f"{status} {evo.name}")
    print(f"   URL: {evo.url}")
    print(f"   Prioridade: {evo.priority}")
    print(f"   Capacidade: {evo.whatsapp_capacity}")
    print()

print("=" * 50)
print("✅ Evolution APIs registradas com sucesso!")
print("=" * 50)
print("\n📝 Próximo passo:")
print("   Execute: python create_whatsapp_instances.py")
print()

PYTHON_CODE
