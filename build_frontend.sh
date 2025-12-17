#!/bin/bash

# Script para compilar frontend React e servir através do Django
# Uso: ./build_frontend.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
STATIC_DIR="$PROJECT_ROOT/src/staticfiles/dist"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔨 Compilando Frontend React para Django"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado!"
    echo "📥 Instale de: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"
echo ""

# 2. Instalar dependências
echo "📦 Instalando dependências..."
cd "$FRONTEND_DIR"
npm install

# 3. Fazer build
echo "🏗️  Compilando assets..."
npm run build

# 4. Copiar para Django static
echo "📁 Copiando para Django..."
mkdir -p "$STATIC_DIR"

if [ -d "$FRONTEND_DIR/dist" ]; then
    cp -r "$FRONTEND_DIR/dist"/* "$STATIC_DIR/"
    echo "✅ Build copiado para: $STATIC_DIR"
else
    echo "❌ Diretório dist não encontrado!"
    exit 1
fi

# 5. Recolher estáticos
echo "🗂️  Coletando arquivos estáticos do Django..."
cd "$PROJECT_ROOT"
source .venv/bin/activate 2>/dev/null || true
python src/manage.py collectstatic --noinput --clear

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Build Completo!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Próximos passos:"
echo "  1. Inicie o servidor Django:"
echo "     python src/manage.py runserver"
echo ""
echo "  2. Abra no navegador:"
echo "     http://localhost:8000/app"
echo ""
