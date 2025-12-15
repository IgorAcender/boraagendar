#!/bin/bash

#############################################################################
#                                                                           #
#  🚀 SETUP EVOLUTION API SIMPLES - MVP COM 1 INSTANCE                    #
#                                                                           #
#  Este script registra 1 Evolution API no Django para começar             #
#  Permite escalar depois adicionando mais Evolution APIs                  #
#                                                                           #
#############################################################################

set -e

cd "$(dirname "$0")/src" || exit 1

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   🐳 REGISTRANDO 1 EVOLUTION API                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Validar que Django está disponível
if ! python manage.py check &>/dev/null; then
    echo "❌ Erro: Django não está disponível"
    echo "   Execute: cd src && python manage.py migrate"
    exit 1
fi

echo "📝 Registrando Evolution API principal..."
echo ""

python manage.py shell << 'EOF'
from scheduling.models import EvolutionAPI
from django.utils import timezone

# Dados do Evolution API fornecido pelo usuário
EVOLUTION_DOMAIN = "robo-de-agendamento-igor.ivhjcm.easypanel.host"
EVOLUTION_API_KEY = "429683C4C977415CAAFCCE10F7D57E11"
EVOLUTION_INSTANCE_ID = "evolution-1"

# URL do Evolution API
EVOLUTION_URL = f"https://{EVOLUTION_DOMAIN}"

try:
    # Verificar se já existe
    existing = EvolutionAPI.objects.filter(instance_id=EVOLUTION_INSTANCE_ID).first()
    
    if existing:
        print(f"⚠️  Evolution API '{EVOLUTION_INSTANCE_ID}' já existe!")
        print(f"   - URL: {existing.url}")
        print(f"   - Capacity: {existing.capacity}")
        print(f"   - Prioridade: {existing.priority}")
        exit(0)
    
    # Criar nova instância
    evolution = EvolutionAPI.objects.create(
        instance_id=EVOLUTION_INSTANCE_ID,
        url=EVOLUTION_URL,
        api_key=EVOLUTION_API_KEY,
        capacity=50,  # 50 WhatsApps neste Evolution
        priority=10,  # Alta prioridade
        is_active=True
    )
    
    print("✅ Evolution API criada com sucesso!")
    print("")
    print(f"   ID: {evolution.instance_id}")
    print(f"   URL: {evolution.url}")
    print(f"   API Key: {evolution.api_key[:10]}...{evolution.api_key[-5:]}")
    print(f"   Capacity: {evolution.capacity} WhatsApps")
    print(f"   Prioridade: {evolution.priority}")
    print(f"   Ativo: {'✅ Sim' if evolution.is_active else '❌ Não'}")
    print("")
    print("📊 Status:")
    print(f"   - Instâncias conectadas: 0/50")
    print(f"   - Utilização: 0%")
    
except Exception as e:
    print(f"❌ Erro ao criar Evolution API: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

EOF

echo ""
echo "🎉 Setup concluído!"
echo ""
echo "Próximo passo: Criar 50 WhatsApps"
echo "   → python create_whatsapp_instances.py"
echo ""
