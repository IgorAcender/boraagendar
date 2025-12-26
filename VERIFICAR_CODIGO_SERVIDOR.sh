// ============================================================================
// COMANDO ÚNICO - Verificar se o código está no servidor
// Copie e cole no Terminal do EasyPanel
// ============================================================================

cd /app/src && python3 << 'EOF'
print("\n🔍 VERIFICANDO CÓDIGO NO SERVIDOR\n")
print("="*50)

# 1. Verificar se o modelo existe
try:
    from scheduling.models import Customer
    print("✅ 1. Modelo Customer: OK")
except ImportError as e:
    print(f"❌ 1. Modelo Customer: ERRO - {e}")

# 2. Verificar se a view existe
try:
    from scheduling.views.dashboard import client_list
    print("✅ 2. View client_list: OK")
except ImportError as e:
    print(f"❌ 2. View client_list: ERRO - {e}")
except AttributeError as e:
    print(f"❌ 2. View client_list: NÃO ENCONTRADA")
    print("   ⚠️  CÓDIGO ANTIGO NO SERVIDOR!")

# 3. Verificar URLs
try:
    from django.urls import reverse
    url = reverse('dashboard:client_list')
    print(f"✅ 3. URL client_list: {url}")
except Exception as e:
    print(f"❌ 3. URL client_list: ERRO - {e}")

# 4. Verificar tabela no banco
try:
    from scheduling.models import Customer
    from tenants.models import Tenant
    tenant = Tenant.objects.first()
    count = Customer.objects.filter(tenant=tenant).count()
    print(f"✅ 4. Tabela Customer: OK ({count} registros)")
except Exception as e:
    print(f"❌ 4. Tabela Customer: ERRO - {e}")

print("="*50)
print("\n🎯 DIAGNÓSTICO:")

import os
stat = os.stat('/app/src/scheduling/views/dashboard.py')
from datetime import datetime
mod_time = datetime.fromtimestamp(stat.st_mtime)
print(f"📅 Última modificação: {mod_time}")
print(f"📦 Tamanho do arquivo: {stat.st_size} bytes")

# Verificar se client_list está no arquivo
with open('/app/src/scheduling/views/dashboard.py', 'r') as f:
    content = f.read()
    if 'def client_list' in content:
        print("✅ 'client_list' ENCONTRADO no arquivo")
        # Contar linhas
        line_num = content[:content.find('def client_list')].count('\n') + 1
        print(f"   Linha: {line_num}")
    else:
        print("❌ 'client_list' NÃO ENCONTRADO no arquivo")
        print("   🚨 CÓDIGO DESATUALIZADO!")

print("\n" + "="*50)
print("\n💡 SOLUÇÃO:")
print("Se aparecer '❌ CÓDIGO DESATUALIZADO':")
print("1. No painel EasyPanel, clique em REDEPLOY")
print("2. Ou execute: cd /app && git pull origin main")
print("\n")
EOF
