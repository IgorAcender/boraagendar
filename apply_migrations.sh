#!/bin/bash
# Script para aplicar as migrações pendentes no Easy Panel
# Use: bash apply_migrations.sh

# Detectar diretório do projeto (tolerante a diferentes layouts no EasyPanel)
KNOWN_DIRS=("/app/src" "/app" "./src" ".")
PROJECT_DIR=""
for dir in "${KNOWN_DIRS[@]}"; do
    if [ -f "$dir/manage.py" ]; then
        PROJECT_DIR="$dir"
        break
    fi
done

# Se não achou, tenta localizar manage.py com busca rápida
if [ -z "$PROJECT_DIR" ]; then
    FOUND_MANAGE=$(find /app -maxdepth 3 -name manage.py 2>/dev/null | head -n 1)
    if [ -n "$FOUND_MANAGE" ]; then
        PROJECT_DIR=$(dirname "$FOUND_MANAGE")
    fi
fi

if [ -z "$PROJECT_DIR" ]; then
    echo "❌ Erro: Não foi possível encontrar manage.py (procurei em /app/src, /app e ./src)."
    echo "👉 Execute 'find / -maxdepth 3 -name manage.py 2>/dev/null' para localizar e ajuste PROJECT_DIR."
    exit 1
fi

cd "$PROJECT_DIR"
echo "🚀 Usando diretório do projeto: $PROJECT_DIR"

echo ""
echo "📋 Verificando migrações pendentes..."
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
