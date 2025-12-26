#!/bin/bash
# Script para inserir Evolution API no banco de dados

# A forma mais simples é usar o Django shell
cd /Users/user/Desktop/Programação/boraagendar

echo "🔧 Criando Evolution API..."

python3 << 'EOF'
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
django.setup()

from scheduling.models import EvolutionAPI

# Verificar se já existe
existing = EvolutionAPI.objects.filter(instance_id='default').first()

if existing:
    print(f"✅ Evolution API já existe: {existing.id}")
else:
    # Criar
    evo = EvolutionAPI.objects.create(
        instance_id='default',
        api_url='http://localhost:8080/api',
        api_key='test-key',
        is_active=True,
        capacity=10,
        priority=1
    )
    print(f"✅ Evolution API criada com sucesso!")
    print(f"   ID: {evo.id}")
    print(f"   Instance: {evo.instance_id}")

# Listar todas
all_apis = EvolutionAPI.objects.all()
print(f"\n📊 Total no banco: {all_apis.count()}")
for api in all_apis:
    print(f"   - {api.instance_id} (Ativo: {api.is_active})")
EOF

echo "✅ Concluído!"
