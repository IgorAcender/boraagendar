#!/bin/bash
# Script para aplicar migrações no Easy Panel

cd /app

echo "📋 Criando novas migrações..."
python manage.py makemigrations tenants

echo ""
echo "🔄 Aplicando migrações..."
python manage.py migrate tenants

echo ""
echo "✅ Migrações aplicadas com sucesso!"
python manage.py check
