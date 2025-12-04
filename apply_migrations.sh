#!/bin/bash
# Script para aplicar as migrações pendentes no Easy Panel
# Use: bash apply_migrations.sh

# Detectar se está rodando local ou no EasyPanel
if [ -d "/app/src" ]; then
    PROJECT_DIR="/app/src"
    echo "🚀 Detectado ambiente EasyPanel"
elif [ -d "./src" ]; then
    PROJECT_DIR="./src"
    echo "� Detectado ambiente local"
else
    echo "❌ Erro: Não foi possível encontrar o diretório do projeto"
    exit 1
fi

cd "$PROJECT_DIR"

echo ""
echo "�📋 Verificando migrações pendentes..."
python3 manage.py showmigrations | grep -E '^\w+$|^\s+\[ \]' || echo "Nenhuma migração pendente detectada"

echo ""
echo "🔄 Aplicando TODAS as migrações pendentes..."
python3 manage.py migrate

echo ""
echo "✅ Verificando status das apps principais..."
echo ""
echo "--- Tenants ---"
python3 manage.py showmigrations tenants | tail -5

echo ""
echo "--- Scheduling ---"
python3 manage.py showmigrations scheduling | tail -5

echo ""
echo "--- Raffles ---"
python3 manage.py showmigrations raffles | tail -5

echo ""
echo "🧪 Verificando integridade do sistema..."
python3 manage.py check

echo ""
echo "✨ Sucesso! Todas as migrações foram aplicadas."
echo ""
echo "🎯 Próximos passos:"
echo "   1. Teste o acesso à aba 'Cores e Marca'"
echo "   2. Verifique se não há erros 500"
echo "   3. Confirme que as cores estão sendo salvas"
