#!/bin/bash
# Execute este comando NO TERMINAL DO EASYPANEL
# Copie e cole tudo de uma vez

cd /app/src && python3 << 'DIAGNOSTIC_EOF'
import sys
print("\n" + "="*60)
print("🔍 DIAGNÓSTICO COMPLETO - ERRO 500 CLIENTES")
print("="*60 + "\n")

# 1. Verificar versão do código
print("1️⃣ VERIFICANDO VERSÃO DO CÓDIGO:")
print("-" * 40)
try:
    import os
    stat = os.stat('/app/src/scheduling/views/dashboard.py')
    from datetime import datetime
    mod_time = datetime.fromtimestamp(stat.st_mtime)
    print(f"📅 Última modificação: {mod_time}")
    print(f"📦 Tamanho: {stat.st_size} bytes")
    
    # Verificar se client_list existe no arquivo
    with open('/app/src/scheduling/views/dashboard.py', 'r') as f:
        content = f.read()
        if 'def client_list' in content:
            line = content[:content.find('def client_list')].count('\n') + 1
            print(f"✅ client_list encontrado (linha {line})")
        else:
            print("❌ client_list NÃO encontrado no arquivo")
except Exception as e:
    print(f"❌ Erro ao verificar arquivo: {e}")

print()

# 2. Testar imports
print("2️⃣ TESTANDO IMPORTS:")
print("-" * 40)
try:
    from scheduling.models import Customer
    print("✅ Modelo Customer importado")
except Exception as e:
    print(f"❌ Erro ao importar Customer: {e}")

try:
    from scheduling.views.dashboard import client_list
    print("✅ View client_list importada")
except Exception as e:
    print(f"❌ Erro ao importar client_list: {e}")

print()

# 3. Verificar URLs no template
print("3️⃣ VERIFICANDO TEMPLATES:")
print("-" * 40)
try:
    with open('/app/src/templates/scheduling/dashboard/client_list.html', 'r') as f:
        template_content = f.read()
        
    if "{% url 'dashboard:client_create' %}" in template_content:
        print("✅ URL correta: dashboard:client_create")
    elif "{% url 'client_create' %}" in template_content:
        print("❌ URL INCORRETA: client_create (falta 'dashboard:')")
    else:
        print("⚠️  URL client_create não encontrada")
        
    if "{% url 'dashboard:client_list' %}" in template_content:
        print("✅ URL correta: dashboard:client_list")
    elif "{% url 'client_list' %}" in template_content:
        print("❌ URL INCORRETA: client_list (falta 'dashboard:')")
except Exception as e:
    print(f"❌ Erro ao verificar template: {e}")

print()

# 4. Testar a view diretamente
print("4️⃣ TESTANDO VIEW DIRETAMENTE:")
print("-" * 40)
try:
    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    from tenants.models import Tenant
    from scheduling.views.dashboard import client_list
    
    factory = RequestFactory()
    request = factory.get('/dashboard/clientes/')
    request.tenant = Tenant.objects.first()
    
    User = get_user_model()
    user = User.objects.first()
    if user:
        request.user = user
        response = client_list(request)
        print(f"✅ View executou! Status: {response.status_code}")
    else:
        print("⚠️  Nenhum usuário encontrado para teste")
        
except Exception as e:
    print(f"❌ ERRO AO EXECUTAR VIEW:")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Mensagem: {str(e)}")
    import traceback
    print("\n📋 TRACEBACK COMPLETO:")
    traceback.print_exc()

print()

# 5. Verificar URLs registradas
print("5️⃣ VERIFICANDO URLs REGISTRADAS:")
print("-" * 40)
try:
    from django.urls import reverse
    
    urls_to_test = [
        'dashboard:client_list',
        'dashboard:client_create',
        'dashboard:client_edit',
        'dashboard:client_delete'
    ]
    
    for url_name in urls_to_test:
        try:
            if 'edit' in url_name or 'delete' in url_name:
                url = reverse(url_name, args=[1])
            else:
                url = reverse(url_name)
            print(f"✅ {url_name}: {url}")
        except Exception as e:
            print(f"❌ {url_name}: {e}")
            
except Exception as e:
    print(f"❌ Erro ao verificar URLs: {e}")

print()

# 6. Verificar banco de dados
print("6️⃣ VERIFICANDO BANCO DE DADOS:")
print("-" * 40)
try:
    from scheduling.models import Customer
    from tenants.models import Tenant
    
    tenant = Tenant.objects.first()
    if tenant:
        count = Customer.objects.filter(tenant=tenant).count()
        print(f"✅ Tabela Customer existe")
        print(f"📊 Total de clientes: {count}")
    else:
        print("⚠️  Nenhum tenant encontrado")
except Exception as e:
    print(f"❌ Erro no banco: {e}")

print()
print("="*60)
print("🎯 FIM DO DIAGNÓSTICO")
print("="*60)
print("\n📤 ENVIE TODA ESTA SAÍDA PARA ANÁLISE\n")

DIAGNOSTIC_EOF
