#!/bin/bash

# 🚀 INSTRUÇÕES PASSO A PASSO PARA CORRIGIR O QR CODE DO WHATSAPP

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     ✅ SOLUÇÃO: QR Code do WhatsApp não estava aparecendo     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# CORES
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 PASSO 1: Entender o Problema${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "❌ ANTES: Clicava em 'Conectar WhatsApp', modal abria mas:"
echo "   - Spinner infinito"
echo "   - Nenhum erro era mostrado"
echo "   - Nunca aparecia o QR code"
echo ""
echo "🔍 CAUSA: Não havia nenhuma 'EvolutionAPI' no banco de dados!"
echo "   A view procurava por uma EvolutionAPI mas não encontrava."
echo ""

echo -e "${BLUE}🔧 PASSO 2: Executar o Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}Escolha UMA opção:${NC}"
echo ""
echo "📌 OPÇÃO 1 (Recomendada): Executar script Python"
echo "   $ python3 setup_evolution_quick.py"
echo ""
echo "📌 OPÇÃO 2: Verificar e criar se necessário"
echo "   $ python3 check_evolution_api.py"
echo ""
echo "📌 OPÇÃO 3: Usar Shell script"
echo "   $ bash setup_evolution_api_simple.sh"
echo ""

read -p "Deseja executar agora? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${GREEN}🚀 Executando setup...${NC}"
    python3 setup_evolution_quick.py
fi

echo ""
echo -e "${BLUE}✅ PASSO 3: Testar${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Agora você pode:"
echo "1. Abra o dashboard em: http://localhost:8000/dashboard/whatsapp/"
echo "2. Clique no botão '+ Conectar WhatsApp'"
echo "3. O QR code deve aparecer no modal! 📱"
echo ""

echo -e "${BLUE}🐛 PASSO 4: Debugar se Necessário${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Se ainda não funcionar:"
echo "1. Abra o console do navegador: F12"
echo "2. Clique em 'Conectar WhatsApp'"
echo "3. Verifique o console para mensagens de erro"
echo "4. Procure por 'Response status' e veja o código HTTP"
echo ""

echo -e "${GREEN}✨ Documentação Adicional:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 Leia: SOLUCAO_WHATSAPP_QR_CODE.md"
echo "📖 Leia: RESUMO_CORRECOES_WHATSAPP.md"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Setup concluído! Próximo passo: testar no dashboard       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
