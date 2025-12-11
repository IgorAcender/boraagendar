#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/Users/user/Desktop/Programação/boraagendar/src')

django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from tenants.models import Tenant, TenantMembership
from scheduling.views.dashboard import index

try:
    # Buscar tenant existente
    tenants = Tenant.objects.all()
    print(f"✓ Total de tenants: {tenants.count()}")
    
    if tenants.count() == 0:
        print("Nenhum tenant encontrado!")
        sys.exit(1)
    
    tenant = tenants.first()
    print(f"✓ Tenant selecionado: {tenant.name}")
    
    # Buscar um usuário com membership
    memberships = TenantMembership.objects.filter(tenant=tenant)
    print(f"✓ Total de memberships: {memberships.count()}")
    
    if memberships.count() == 0:
        print("Nenhum membership encontrado!")
        sys.exit(1)
    
    membership = memberships.first()
    user = membership.user
    print(f"✓ Usuário: {user.username}")
    
    # Criar request mock
    factory = RequestFactory()
    request = factory.get('/scheduling/dashboard/')
    request.user = user
    request.session = {}
    
    print("\n📋 Testando view...")
    
    # Executar view
    response = index(request)
    print(f"✅ Sucesso! Status: {response.status_code}")
    
except Exception as e:
    print(f"\n❌ Erro encontrado:")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")
    print("\n📍 Traceback completo:")
    import traceback
    traceback.print_exc()
    sys.exit(1)
