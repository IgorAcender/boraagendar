#!/bin/bash
# ============================================================================
# COMANDO ÚNICO PARA RESOLVER ERRO 500 - CLIENTES
# ============================================================================
# Copie e cole ESTE COMANDO COMPLETO no Terminal do EasyPanel:
# ============================================================================

cd /app/src && \
echo "🔄 Aplicando migration do Customer..." && \
python3 manage.py migrate scheduling && \
echo "✅ Migration aplicada!" && \
echo "" && \
echo "📊 Verificando tabelas criadas:" && \
python3 manage.py dbshell << 'EOF'
.tables
.quit
EOF
echo "" && \
echo "🎉 PRONTO! Acesse: https://robo-de-agendamento-igor.lvh.cm.easypanel.host/dashboard/clientes/"
