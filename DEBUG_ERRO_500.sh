#!/bin/bash
# 🔍 CAPTURAR ERRO REAL - Execute no EasyPanel

echo "=== Testando a view branding_settings ==="
python3 manage.py shell << 'EOF'
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from tenants.models import Tenant, TenantMembership
from scheduling.views.dashboard import branding_settings

# Pegar o primeiro tenant e usuário owner
User = get_user_model()
tenant = Tenant.objects.first()
membership = TenantMembership.objects.filter(tenant=tenant, role='owner').first()

if not membership:
    print("❌ Nenhum membership 'owner' encontrado")
    print("Criando um para teste...")
    user = User.objects.first()
    if user:
        membership = TenantMembership.objects.create(
            tenant=tenant,
            user=user,
            role='owner',
            is_active=True
        )
        print(f"✅ Membership criado para {user.email}")

if membership:
    # Simular uma requisição
    factory = RequestFactory()
    request = factory.get('/dashboard/configuracoes/marca/')
    request.user = membership.user
    
    try:
        response = branding_settings(request)
        print(f"✅ Resposta: {response.status_code}")
    except Exception as e:
        print(f"❌ ERRO ENCONTRADO:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Não foi possível criar teste")
EOF
