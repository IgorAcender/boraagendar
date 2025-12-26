#!/bin/bash
# 🔍 VERIFICAR CÓDIGO NO EASYPANEL

echo "=== 1. Verificar se a view existe e está correta ==="
python3 -c "
import inspect
from scheduling.views.dashboard import branding_settings
print(inspect.getsource(branding_settings))
" 2>&1 | head -40

echo ""
echo "=== 2. Verificar se o template existe ==="
find /app -name "branding_settings.html" -type f

echo ""
echo "=== 3. Verificar última modificação dos arquivos ==="
ls -lh /app/scheduling/views/dashboard.py
ls -lh /app/tenants/forms.py
ls -lh /app/tenants/models.py

echo ""
echo "=== 4. Ver hash do último commit ==="
cd /app && git log -1 --oneline 2>/dev/null || echo "Não é um repositório git"

echo ""
echo "=== 5. Testar a URL diretamente ==="
python3 manage.py shell -c "
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
client = Client()

# Pegar um usuário owner
from tenants.models import TenantMembership
membership = TenantMembership.objects.filter(role='owner').first()
if membership:
    user = membership.user
    client.force_login(user)
    response = client.get('/dashboard/configuracoes/marca/')
    print(f'Status Code: {response.status_code}')
    if response.status_code == 500:
        print('ERRO 500 confirmado')
        print('Conteúdo:', response.content[:500])
else:
    print('Nenhum owner encontrado')
"
