#!/bin/bash

# Script para aplicar migration do Customer no EasyPanel
# Execute no terminal do container: bash aplicar_migration_customer.sh

echo "🚀 Aplicando Migration do Customer no EasyPanel"
echo "================================================"
echo ""

# Navegar para o diretório correto
cd /app/src || { echo "❌ Erro: diretório /app/src não encontrado"; exit 1; }

echo "📂 Diretório atual: $(pwd)"
echo ""

# Verificar migrations pendentes
echo "📋 Verificando migrations pendentes..."
python3 manage.py showmigrations scheduling | grep "scheduling.0013_customer"
echo ""

# Aplicar migration
echo "⚙️  Aplicando migration..."
python3 manage.py migrate scheduling 0013
echo ""

# Confirmar sucesso
echo "✅ Verificando se foi aplicada..."
python3 manage.py showmigrations scheduling | grep "0013_customer"
echo ""

# Criar clientes de exemplo (opcional)
read -p "🤔 Deseja criar clientes de exemplo? (s/n): " criar_exemplos

if [ "$criar_exemplos" = "s" ] || [ "$criar_exemplos" = "S" ]; then
    echo "📝 Criando clientes de exemplo..."
    python3 manage.py shell << 'EOF'
from scheduling.models import Customer
from tenants.models import Tenant

tenant = Tenant.objects.first()
if tenant:
    sample_clients = [
        {
            'tenant': tenant,
            'name': 'Maria Silva',
            'email': 'maria.silva@email.com',
            'phone': '(11) 98765-4321',
            'city': 'São Paulo',
            'state': 'SP',
        },
        {
            'tenant': tenant,
            'name': 'João Santos',
            'email': 'joao.santos@email.com',
            'phone': '(11) 97654-3210',
            'city': 'São Paulo',
            'state': 'SP',
        },
    ]
    
    for client_data in sample_clients:
        if not Customer.objects.filter(tenant=tenant, phone=client_data['phone']).exists():
            Customer.objects.create(**client_data)
            print(f"✅ Cliente criado: {client_data['name']}")
        else:
            print(f"⚠️  Cliente já existe: {client_data['name']}")
    
    print(f"\n📊 Total de clientes: {Customer.objects.filter(tenant=tenant).count()}")
else:
    print("❌ Nenhum tenant encontrado")
EOF
fi

echo ""
echo "🎉 Migration aplicada com sucesso!"
echo "🌐 Acesse: https://robo-de-agendamento-igor.lvh.cm.easypanel.host/dashboard/clientes/"
echo ""
