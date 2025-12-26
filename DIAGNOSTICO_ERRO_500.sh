#!/bin/bash
# ============================================================================
# DIAGNÓSTICO COMPLETO - Erro 500 Clientes
# Execute no Terminal do EasyPanel
# ============================================================================

echo "🔍 DIAGNÓSTICO DO ERRO 500 - ABA CLIENTES"
echo "=========================================="
echo ""

cd /app/src

echo "1️⃣ Verificando se o modelo Customer existe no código:"
python3 -c "from scheduling.models import Customer; print('✅ Modelo Customer encontrado!')" 2>&1

echo ""
echo "2️⃣ Verificando se a tabela existe no banco:"
python3 manage.py dbshell << 'EOF'
.tables
EOF

echo ""
echo "3️⃣ Verificando se a view client_list existe:"
python3 -c "from scheduling.views.dashboard import client_list; print('✅ View client_list encontrada!')" 2>&1

echo ""
echo "4️⃣ Verificando URLs registradas:"
python3 manage.py show_urls 2>/dev/null | grep client || python3 << 'EOF'
from django.urls import get_resolver
resolver = get_resolver()
for pattern in resolver.url_patterns:
    if hasattr(pattern, 'url_patterns'):
        for sub in pattern.url_patterns:
            if 'client' in str(sub.pattern):
                print(f"✅ {sub.pattern}")
EOF

echo ""
echo "5️⃣ Testando import completo:"
python3 << 'EOF'
try:
    from scheduling.models import Customer
    from scheduling.views import dashboard
    from tenants.models import Tenant
    
    print("✅ Imports OK")
    
    # Verificar se a view existe
    if hasattr(dashboard, 'client_list'):
        print("✅ client_list existe no dashboard")
    else:
        print("❌ client_list NÃO existe no dashboard")
        print("   Views disponíveis:", [v for v in dir(dashboard) if not v.startswith('_')])
        
except Exception as e:
    print(f"❌ Erro: {e}")
EOF

echo ""
echo "6️⃣ Verificando última data de modificação dos arquivos:"
ls -lh /app/src/scheduling/views/dashboard.py
ls -lh /app/src/scheduling/models.py

echo ""
echo "7️⃣ Procurando por 'client_list' no código:"
grep -n "def client_list" /app/src/scheduling/views/dashboard.py || echo "❌ client_list NÃO encontrada no arquivo"

echo ""
echo "=========================================="
echo "🎯 RESULTADO DO DIAGNÓSTICO:"
echo "=========================================="
