#!/bin/bash
# 🚨 DIAGNÓSTICO COMPLETO - Todas as páginas com erro 500

echo "=== 1. Verificar se o Django está rodando ==="
python3 manage.py check

echo ""
echo "=== 2. Testar imports críticos ==="
python3 -c "
try:
    from scheduling.views import dashboard as dashboard_views
    print('✅ dashboard views OK')
except Exception as e:
    print(f'❌ Erro ao importar dashboard views: {e}')
    import traceback
    traceback.print_exc()

try:
    from tenants.forms import BrandingSettingsForm
    print('✅ BrandingSettingsForm OK')
except Exception as e:
    print(f'❌ Erro ao importar BrandingSettingsForm: {e}')

try:
    from tenants.models import BrandingSettings
    print('✅ BrandingSettings model OK')
except Exception as e:
    print(f'❌ Erro ao importar BrandingSettings: {e}')
"

echo ""
echo "=== 3. Verificar collectstatic ==="
python3 manage.py collectstatic --noinput --clear 2>&1 | tail -5

echo ""
echo "=== 4. Verificar variáveis de ambiente críticas ==="
python3 -c "
import os
from django.conf import settings

print(f'DEBUG: {settings.DEBUG}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'DATABASE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'SECRET_KEY definido: {bool(settings.SECRET_KEY)}')
"

echo ""
echo "=== 5. Testar página simples ==="
python3 manage.py shell -c "
from django.test import Client
client = Client()
response = client.get('/admin/login/')
print(f'Admin login: {response.status_code}')
"

echo ""
echo "=== 6. Verificar se há erro de sintaxe Python ==="
python3 -m py_compile scheduling/views/dashboard.py
python3 -m py_compile tenants/forms.py
python3 -m py_compile tenants/models.py
echo "✅ Sintaxe OK"

echo ""
echo "=== 7. Reiniciar servidor (se necessário) ==="
echo "Execute: pkill -f gunicorn && gunicorn config.wsgi:application"
