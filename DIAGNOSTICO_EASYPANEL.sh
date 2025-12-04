#!/bin/bash
# 🔍 DIAGNÓSTICO - Execute no terminal do EasyPanel

echo "=== 1. Verificar status das migrações do tenants ==="
python3 manage.py showmigrations tenants

echo ""
echo "=== 2. Verificar se o modelo BrandingSettings existe ==="
python3 manage.py shell -c "from tenants.models import BrandingSettings; print('✅ BrandingSettings OK')"

echo ""
echo "=== 3. Testar criação de BrandingSettings ==="
python3 manage.py shell -c "
from tenants.models import Tenant, BrandingSettings
tenant = Tenant.objects.first()
if tenant:
    branding, created = BrandingSettings.objects.get_or_create(tenant=tenant)
    print(f'✅ BrandingSettings para {tenant.name}: {branding}')
    print(f'   - background_color: {branding.background_color}')
    print(f'   - text_color: {branding.text_color}')
    print(f'   - button_color_primary: {branding.button_color_primary}')
    print(f'   - button_text_color: {branding.button_text_color}')
else:
    print('❌ Nenhum tenant encontrado')
"

echo ""
echo "=== 4. Verificar campos do modelo ==="
python3 manage.py inspectdb --database default tenants_brandingsettings

echo ""
echo "=== 5. Verificar logs de erro ==="
echo "Execute: tail -f /var/log/seu-app.log"
echo "Ou verifique os logs do container no EasyPanel"
