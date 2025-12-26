#!/bin/bash

# 🎯 Teste do Construtor de Seções
# Este script verifica se a implementação está funcionando corretamente

echo "🔍 TESTE DO CONSTRUTOR DE SEÇÕES"
echo "=================================="
echo ""

echo "1️⃣  Verificando modelo BrandingSettings..."
python3 manage.py shell -c "
from tenants.models import BrandingSettings
print('   ✅ Modelo existe')
# Verificar se o campo existe
if hasattr(BrandingSettings, 'sections_config'):
    print('   ✅ Campo sections_config existe')
else:
    print('   ❌ Campo sections_config NÃO existe')
"

echo ""
echo "2️⃣  Verificando se form renderiza o campo..."
python3 manage.py shell -c "
from tenants.forms import BrandingSettingsForm
if 'sections_config' in BrandingSettingsForm.Meta.fields:
    print('   ✅ Campo sections_config está no formulário')
else:
    print('   ❌ Campo sections_config NÃO está no formulário')
"

echo ""
echo "3️⃣  Verificando helpers Python..."
python3 manage.py shell -c "
try:
    from scheduling.views.sections_helper import get_sections_config, get_sections_order
    print('   ✅ Helpers importados com sucesso')
    
    # Testar função com None
    result = get_sections_config(None)
    if 'about' in result and result['about']['visible']:
        print('   ✅ get_sections_config() retorna padrão correto')
    else:
        print('   ❌ get_sections_config() não retorna padrão correto')
except Exception as e:
    print(f'   ❌ Erro ao importar helpers: {e}')
"

echo ""
echo "4️⃣  Verificando template tags..."
python3 manage.py shell -c "
try:
    from django import template
    from scheduling.templatetags import sections
    print('   ✅ Template tags importadas com sucesso')
except Exception as e:
    print(f'   ❌ Erro ao importar template tags: {e}')
"

echo ""
echo "5️⃣  Verificando se migrations foram aplicadas..."
python3 manage.py showmigrations tenants | grep "0021_brandingsettings_sections_config"

echo ""
echo "✅ TESTES CONCLUÍDOS!"
echo ""
echo "Próximas etapas:"
echo "1. Abra a página de branding settings no dashboard"
echo "2. Role até 'Construtor de Seções'"
echo "3. Teste ativar/desativar seções"
echo "4. Teste mover seções com setas"
echo "5. Clique em 'Salvar Configurações'"
echo "6. Recarregue a página para verificar se dados foram salvos"
