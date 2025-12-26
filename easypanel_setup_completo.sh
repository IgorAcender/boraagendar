#!/bin/bash

#############################################################################
#                                                                           #
#  🚀 EASYPANEL QUICK SETUP - Evolution API + 50 WhatsApps                #
#                                                                           #
#  Este script faz TUDO automaticamente para o Bora Agendar                #
#  Execute dentro do terminal da EasyPanel                                 #
#                                                                           #
#############################################################################

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║    🚀 SETUP COMPLETO: EVOLUTION API + 50 WHATSAPPS            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Validações iniciais
if ! command -v python &> /dev/null; then
    echo "❌ Python não encontrado"
    exit 1
fi

# Encontrar o caminho do manage.py
if [ -f "./manage.py" ]; then
    DJANGO_DIR="."
elif [ -f "./src/manage.py" ]; then
    DJANGO_DIR="./src"
else
    echo "❌ manage.py não encontrado"
    echo "   Execute este script da pasta raiz do projeto"
    exit 1
fi

cd "$DJANGO_DIR"

echo "📁 Diretório: $(pwd)"
echo ""

# PASSO 1: Verificar Django
echo "1️⃣  Verificando Django..."
if ! python manage.py check &>/dev/null; then
    echo "❌ Django não está funcionando"
    echo "   Verifique o banco de dados e dependências"
    exit 1
fi
echo "✅ Django OK"
echo ""

# PASSO 2: Aplicar migrações
echo "2️⃣  Aplicando migrações..."
python manage.py migrate --noinput 2>&1 | tail -3
echo "✅ Migrações aplicadas"
echo ""

# PASSO 3: Registrar Evolution API
echo "3️⃣  Registrando 1 Evolution API..."
python manage.py shell << 'SHELL'
from scheduling.models import EvolutionAPI

EVOLUTION_DATA = {
    'instance_id': 'evolution-1',
    'url': 'https://robo-de-agendamento-igor.ivhjcm.easypanel.host',
    'api_key': '429683C4C977415CAAFCCE10F7D57E11',
    'capacity': 50,
    'priority': 10,
    'is_active': True,
}

try:
    # Verificar se já existe
    existing = EvolutionAPI.objects.filter(instance_id=EVOLUTION_DATA['instance_id']).first()
    
    if existing:
        print(f"⚠️  Evolution API '{EVOLUTION_DATA['instance_id']}' já existe")
        print(f"   URL: {existing.url}")
        print(f"   Capacity: {existing.capacity}")
    else:
        # Criar nova
        evolution = EvolutionAPI.objects.create(**EVOLUTION_DATA)
        print(f"✅ Evolution API criada: {evolution.instance_id}")
        print(f"   URL: {evolution.url}")
        print(f"   Capacity: {evolution.capacity} WhatsApps")
        print(f"   Priority: {evolution.priority}")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

SHELL

echo "✅ Evolution API registrada"
echo ""

# PASSO 4: Criar 50 WhatsApps
echo "4️⃣  Criando 50 WhatsApps..."
python manage.py shell << 'SHELL'
from scheduling.models import EvolutionAPI, WhatsAppInstance

evolution_apis = EvolutionAPI.objects.filter(is_active=True).order_by('priority')

if not evolution_apis.exists():
    print("❌ Nenhum Evolution API encontrado!")
    exit(1)

# Contar existentes
existing = WhatsAppInstance.objects.count()

if existing >= 50:
    print(f"✅ Já existem {existing} WhatsApps criados")
else:
    to_create = 50 - existing
    created = 0
    
    base_phone = 5511999
    api_index = 0
    apis_list = list(evolution_apis)
    
    for i in range(existing, 50):
        evolution_api = apis_list[api_index % len(apis_list)]
        api_index += 1
        
        phone_number = f"{base_phone}{i:05d}"
        
        try:
            instance = WhatsAppInstance.objects.create(
                evolution_api=evolution_api,
                phone_number=phone_number,
                display_name=f"WhatsApp #{i+1}",
                is_active=True,
                is_primary=(i == existing),
                connection_status='pending'
            )
            created += 1
            
            if (i + 1 - existing) % 10 == 0:
                print(f"   ✓ {i + 1 - existing} criados...", flush=True)
        
        except Exception as e:
            print(f"   ⚠️  Erro ao criar #{i+1}: {e}")
            continue
    
    print(f"✅ {created} WhatsApps criados (total: {WhatsAppInstance.objects.count()})")

SHELL

echo "✅ WhatsApps criados"
echo ""

# RESUMO FINAL
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 SETUP CONCLUÍDO!                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

python manage.py shell << 'SHELL'
from scheduling.models import EvolutionAPI, WhatsAppInstance

print("📊 RESUMO FINAL:")
print("")

# Evolution APIs
print("Evolution APIs:")
for api in EvolutionAPI.objects.all():
    count = api.whatsapp_instances.count()
    status = "✅" if api.is_active else "❌"
    print(f"   {status} {api.instance_id}: {count}/{api.capacity} ({api.get_usage_percentage()}%)")

# Total de WhatsApps
total = WhatsAppInstance.objects.count()
print(f"\nTotal de WhatsApps: {total}")

# Status de conexão
for status in ['pending', 'connected', 'connecting', 'disconnected', 'error']:
    count = WhatsAppInstance.objects.filter(connection_status=status).count()
    if count > 0:
        icons = {
            'pending': '📋',
            'connected': '✅',
            'connecting': '⏳',
            'disconnected': '❌',
            'error': '⚠️',
        }
        print(f"   {icons[status]} {status}: {count}")

print("")
print("✅ Sistema pronto para enviar WhatsApps!")

SHELL

echo ""
echo "📚 Próximos passos:"
echo "   1. Acessar Django Admin: /admin/scheduling/evolutionapivolume/"
echo "   2. Conectar WhatsApps no Evolution API"
echo "   3. Testar com um agendamento"
echo ""
