#!/bin/bash

#############################################################################
#                                                                           #
#  🚀 SETUP 2º EVOLUTION API - ESCALAR PARA 100 WHATSAPPS                 #
#                                                                           #
#  Execute este script DEPOIS que tiver 50 WhatsApps funcionando           #
#  Adiciona um 2º Evolution API e rebalanceia para 25+25                   #
#                                                                           #
#############################################################################

set -e

cd "$(dirname "$0")/src" || exit 1

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   🐳 ADICIONANDO 2º EVOLUTION API                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Validar que Django está disponível
if ! python manage.py check &>/dev/null; then
    echo "❌ Erro: Django não está disponível"
    exit 1
fi

echo "📝 Registrando 2º Evolution API..."
echo ""
echo "⚠️  IMPORTANTE:"
echo "   1. Você já tem 50 WhatsApps no evolution-1"
echo "   2. Vamos rebalancear para 25 + 25"
echo "   3. Depois criar 50 WhatsApps novos"
echo ""
echo "Tem certeza? [s/N]"
read -r confirm

if [[ ! "$confirm" =~ ^[sS]$ ]]; then
    echo "❌ Cancelado"
    exit 1
fi

python manage.py shell << 'EOF'
from scheduling.models import EvolutionAPI, WhatsAppInstance

print("📊 Status ANTES:")
for api in EvolutionAPI.objects.all():
    count = api.whatsapp_instances.count()
    print(f"   {api.instance_id}: {count}/{api.capacity}")

# Criar 2º Evolution (você vai precisar fornecer os dados)
print("\n📝 Preciso dos dados do 2º Evolution API:")
domain = input("   URL (ex: https://seu-dominio.com): ").strip()
api_key = input("   API Key: ").strip()

if not domain or not api_key:
    print("❌ Dados inválidos")
    exit(1)

try:
    evolution2 = EvolutionAPI.objects.create(
        instance_id='evolution-2',
        url=domain,
        api_key=api_key,
        capacity=50,
        priority=5,  # Menor prioridade que evolution-1
        is_active=True
    )
    print(f"\n✅ 2º Evolution criado: {evolution2.instance_id}")
except Exception as e:
    print(f"❌ Erro: {e}")
    exit(1)

print("\n📊 Status DEPOIS:")
for api in EvolutionAPI.objects.all():
    count = api.whatsapp_instances.count()
    print(f"   {api.instance_id}: {count}/{api.capacity}")

print("\n✅ Próximo passo: python create_whatsapp_instances_simple.py")
print("   Isso vai rebalancear e criar 50 novos WhatsApps")

EOF

echo ""
echo "🎉 2º Evolution registrado!"
echo ""
echo "Próximos passos:"
echo "   1. python create_whatsapp_instances_simple.py"
echo "   2. Conectar WhatsApps no 2º Evolution API"
echo ""
