#!/bin/bash
# Script para criar e aplicar as migrações no Easy Panel

cd /app

echo "📋 Gerando migrações automáticas..."
python manage.py makemigrations tenants

echo ""
echo "🔄 Aplicando migrações..."
python manage.py migrate tenants

echo ""
echo "✅ Verificando integridade..."
python manage.py check

echo ""
echo "✨ Sucesso! Todas as mudanças foram aplicadas."
