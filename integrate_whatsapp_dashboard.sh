#!/bin/bash

#############################################
# 🚀 INTEGRAÇÃO AUTOMÁTICA DO DASHBOARD WHATSAPP
# Script para integrar todas as partes
#############################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 INTEGRAÇÃO WHATSAPP DASHBOARD                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ==========================================
# PASSO 1: Verificar estrutura de pastas
# ==========================================
echo -e "${YELLOW}[1/5] Verificando estrutura de diretórios...${NC}"

REQUIRED_FILES=(
    "src/scheduling/models.py"
    "src/scheduling/views/whatsapp_manager.py"
    "src/scheduling/urls/whatsapp.py"
    "src/scheduling/templates/whatsapp/dashboard.html"
    "src/scheduling/templates/whatsapp/detail.html"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file NÃO ENCONTRADO!"
        exit 1
    fi
done

# ==========================================
# PASSO 2: Atualizar config/urls.py
# ==========================================
echo ""
echo -e "${YELLOW}[2/5] Atualizando config/urls.py...${NC}"

URLS_FILE="src/config/urls.py"

# Verificar se já existe a importação
if grep -q "from scheduling.urls import whatsapp" "$URLS_FILE"; then
    echo -e "${YELLOW}⚠${NC} Import já existe em $URLS_FILE"
else
    # Adicionar import no topo (após os imports existentes)
    sed -i.bak '1,/^from django.contrib import admin/a\
from scheduling.urls import whatsapp as whatsapp_urls
' "$URLS_FILE"
    echo -e "${GREEN}✓${NC} Import adicionado ao $URLS_FILE"
fi

# Verificar se já existe a rota
if grep -q "path('whatsapp/', include(whatsapp_urls))" "$URLS_FILE"; then
    echo -e "${YELLOW}⚠${NC} Rota '/whatsapp/' já existe em $URLS_FILE"
else
    # Adicionar rota antes de admin (procurar por "path('admin/'")
    sed -i.bak '/path.*admin/i\
    path('\''whatsapp/'\'', include(whatsapp_urls)),
' "$URLS_FILE"
    echo -e "${GREEN}✓${NC} Rota '/whatsapp/' adicionada ao $URLS_FILE"
fi

# ==========================================
# PASSO 3: Gerar Migration (se necessário)
# ==========================================
echo ""
echo -e "${YELLOW}[3/5] Verificando migrations...${NC}"

MIGRATION_FILE="src/scheduling/migrations/0011_whatsappinstance_*.py"

if ls $MIGRATION_FILE 1> /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Migration 0011 já existe"
else
    echo -e "${YELLOW}ℹ${NC} Gerando migration 0011..."
    cd src
    python manage.py makemigrations scheduling
    cd ..
    echo -e "${GREEN}✓${NC} Migration 0011 gerada"
fi

# ==========================================
# PASSO 4: Instalar dependências
# ==========================================
echo ""
echo -e "${YELLOW}[4/5] Verificando dependências...${NC}"

# Verificar se qrcode está instalado
if python -c "import qrcode" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} qrcode já instalado"
else
    echo -e "${YELLOW}ℹ${NC} Instalando qrcode..."
    pip install qrcode[pil]
    echo -e "${GREEN}✓${NC} qrcode instalado"
fi

# ==========================================
# PASSO 5: Resumo e próximos passos
# ==========================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ✅ INTEGRAÇÃO COMPLETADA!                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}PRÓXIMAS AÇÕES (CRÍTICAS):${NC}"
echo ""
echo -e "${YELLOW}1. APLICAR MIGRATION NO EASYPANEL:${NC}"
echo "   docker exec -it seu_container bash"
echo "   python manage.py migrate"
echo ""
echo -e "${YELLOW}2. REINICIAR SERVIDOR:${NC}"
echo "   docker restart seu_container"
echo ""
echo -e "${YELLOW}3. TESTAR NO NAVEGADOR:${NC}"
echo "   https://seu-dominio.com/whatsapp/"
echo ""

echo -e "${GREEN}ARQUIVOS CRIADOS/MODIFICADOS:${NC}"
echo "  ✓ scheduling/models.py (extended)"
echo "  ✓ scheduling/views/whatsapp_manager.py (novo)"
echo "  ✓ scheduling/urls/whatsapp.py (novo)"
echo "  ✓ scheduling/templates/whatsapp/dashboard.html (novo)"
echo "  ✓ scheduling/templates/whatsapp/detail.html (novo)"
echo "  ✓ scheduling/migrations/0011_*.py (novo)"
echo "  ✓ config/urls.py (modificado)"
echo ""

echo -e "${BLUE}ℹ  Para guia detalhado, ver: INTEGRACAO_WHATSAPP_DASHBOARD.md${NC}"
echo -e "${BLUE}ℹ  Para modo de uso, ver: GUIA_GERENCIAR_WHATSAPP.md${NC}"
echo ""

echo -e "${GREEN}🎉 Integração pronta! Siga os próximos passos acima.${NC}"
echo ""
