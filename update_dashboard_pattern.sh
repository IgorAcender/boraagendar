#!/bin/bash
# Script para atualizar todos os templates do dashboard com o novo padrão visual

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎨 Aplicando novo padrão visual em todas as abas administrativas...${NC}\n"

# Lista de arquivos a atualizar
FILES=(
    "src/templates/scheduling/dashboard/calendar.html"
    "src/templates/scheduling/dashboard/default_availability.html"
    "src/templates/scheduling/dashboard/my_schedule.html"
    "src/templates/scheduling/dashboard/my_services.html"
    "src/templates/scheduling/dashboard/tenant_settings.html"
    "src/templates/scheduling/dashboard/booking_policies.html"
)

# Para cada arquivo, fazer backup e marcar para atualização
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        # Criar backup
        cp "$file" "${file%.html}_old.html"
        echo -e "${GREEN}✓${NC} Backup criado: ${file%.html}_old.html"
    else
        echo "⚠ Arquivo não encontrado: $file"
    fi
done

echo -e "\n${BLUE}📝 Próximo passo: Aplicar novo padrão manualmente ou criar versões novas${NC}"
echo -e "${BLUE}Arquivos prontos para serem atualizados:${NC}"
for file in "${FILES[@]}"; do
    echo "  - $file"
done
