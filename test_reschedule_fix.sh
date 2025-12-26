#!/bin/bash
# 🧪 Script de Teste para Reagendamento - Execute no EasyPanel

echo "🔍 Testando correção do reagendamento..."
echo ""

cd /app/src

# Teste 1: Verificar imports
echo "✓ Teste 1: Verificando imports..."
python3 << 'EOF'
try:
    from django.utils import timezone
    from scheduling.views.public import reschedule_booking
    print("✅ Imports OK")
except Exception as e:
    print(f"❌ Erro nos imports: {e}")
    exit(1)
EOF

# Teste 2: Verificar se a view tem 'today' no contexto
echo ""
echo "✓ Teste 2: Verificando se view tem variável 'today'..."
grep -A 20 "def reschedule_booking" /app/src/scheduling/views/public.py | grep -q "today = timezone.now().date()"
if [ $? -eq 0 ]; then
    echo "✅ Variável 'today' encontrada na view"
else
    echo "❌ Variável 'today' NÃO encontrada - PRECISA ATUALIZAR!"
    exit 1
fi

# Teste 3: Verificar template
echo ""
echo "✓ Teste 3: Verificando template reschedule_booking.html..."
if [ -f "/app/src/templates/scheduling/public/reschedule_booking.html" ]; then
    echo "✅ Template existe"
else
    echo "❌ Template NÃO encontrado!"
    exit 1
fi

# Teste 4: Django check
echo ""
echo "✓ Teste 4: Verificando erros no Django..."
python3 manage.py check --deploy 2>&1 | head -20

echo ""
echo "🎉 Todos os testes passaram!"
echo ""
echo "📝 Agora tente acessar o reagendamento:"
echo "   https://seu-dominio.com/agendar/SEU-TENANT/meus-agendamentos/"
