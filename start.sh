#!/bin/bash

# 🚀 BORAGENDAR - SCRIPTS DE INICIALIZAÇÃO RÁPIDA

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  BORAGENDAR - INICIAR LOCALMENTE          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Função para iniciar backend
start_backend() {
    echo -e "${GREEN}▶ Iniciando Backend (Django)...${NC}"
    cd /Users/user/Desktop/Programação/boraagendar
    .venv/bin/python src/manage.py runserver 0.0.0.0:8000
}

# Função para iniciar frontend
start_frontend() {
    echo -e "${GREEN}▶ Iniciando Frontend (React)...${NC}"
    cd /Users/user/Desktop/Programação/boraagendar/frontend
    
    # Verificar se dependencies estão instaladas
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}  > Instalando dependências...${NC}"
        npm install
    fi
    
    npm run dev
}

# Função para construir frontend
build_frontend() {
    echo -e "${GREEN}▶ Construindo Frontend...${NC}"
    cd /Users/user/Desktop/Programação/boraagendar/frontend
    npm run build
    echo -e "${GREEN}✅ Build concluído em: ./dist${NC}"
}

# Função para rodar testes backend
test_backend() {
    echo -e "${GREEN}▶ Executando testes (Backend)...${NC}"
    cd /Users/user/Desktop/Programação/boraagendar
    .venv/bin/python src/manage.py test
}

# Função para verificar status
check_status() {
    echo -e "${GREEN}▶ Verificando status...${NC}"
    echo ""
    
    echo -e "${BLUE}Backend (Django):${NC}"
    curl -s http://localhost:8000/healthz/ && echo -e "${GREEN}✅ OK${NC}" || echo -e "${YELLOW}⚠️  Não respondendo${NC}"
    
    echo ""
    echo -e "${BLUE}Frontend (React):${NC}"
    curl -s http://localhost:5173/ > /dev/null && echo -e "${GREEN}✅ OK${NC}" || echo -e "${YELLOW}⚠️  Não respondendo${NC}"
}

# Função para migrar banco
migrate_db() {
    echo -e "${GREEN}▶ Executando migrations...${NC}"
    cd /Users/user/Desktop/Programação/boraagendar
    .venv/bin/python src/manage.py migrate
    echo -e "${GREEN}✅ Migrations concluídas${NC}"
}

# Função para criar superuser
create_superuser() {
    echo -e "${GREEN}▶ Criando superuser...${NC}"
    cd /Users/user/Desktop/Programação/boraagendar
    .venv/bin/python src/manage.py createsuperuser
}

# Função para limpar cache
clean_cache() {
    echo -e "${GREEN}▶ Limpando cache...${NC}"
    cd /Users/user/Desktop/Programação/boraagendar
    .venv/bin/python src/manage.py cache_clear 2>/dev/null || true
    echo -e "${GREEN}✅ Cache limpo${NC}"
}

# Função para reiniciar (ambos)
start_all() {
    echo -e "${BLUE}Você precisa de 2 terminais para isso!${NC}"
    echo ""
    echo -e "${YELLOW}Terminal 1 (Backend):${NC}"
    echo "  $ start_backend"
    echo ""
    echo -e "${YELLOW}Terminal 2 (Frontend):${NC}"
    echo "  $ start_frontend"
    echo ""
    echo -e "${GREEN}Depois acesse: http://localhost:5173${NC}"
}

# Menu principal
show_menu() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Escolha uma opção:${NC}"
    echo ""
    echo "  1) Iniciar Backend (Django)"
    echo "  2) Iniciar Frontend (React)"
    echo "  3) Construir Frontend (prod)"
    echo "  4) Rodar testes (Backend)"
    echo "  5) Verificar status"
    echo "  6) Executar migrations"
    echo "  7) Criar superuser"
    echo "  8) Limpar cache"
    echo "  9) Instruções (iniciar ambos)"
    echo "  0) Sair"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Lógica principal
if [ $# -eq 0 ]; then
    # Modo interativo
    while true; do
        show_menu
        read -p "Digite sua escolha: " choice
        
        case $choice in
            1) start_backend ;;
            2) start_frontend ;;
            3) build_frontend ;;
            4) test_backend ;;
            5) check_status ;;
            6) migrate_db ;;
            7) create_superuser ;;
            8) clean_cache ;;
            9) start_all ;;
            0) echo "Saindo..."; exit 0 ;;
            *) echo "Opção inválida!" ;;
        esac
    done
else
    # Modo direto
    case $1 in
        backend) start_backend ;;
        frontend) start_frontend ;;
        build) build_frontend ;;
        test) test_backend ;;
        status) check_status ;;
        migrate) migrate_db ;;
        superuser) create_superuser ;;
        clean) clean_cache ;;
        help)
            echo "Uso: bash start.sh [comando]"
            echo ""
            echo "Comandos:"
            echo "  backend   - Iniciar backend"
            echo "  frontend  - Iniciar frontend"
            echo "  build     - Build frontend"
            echo "  test      - Rodar testes"
            echo "  status    - Verificar status"
            echo "  migrate   - Executar migrations"
            echo "  superuser - Criar superuser"
            echo "  clean     - Limpar cache"
            echo ""
            ;;
        *)
            echo "Comando desconhecido: $1"
            echo "Use: bash start.sh help"
            ;;
    esac
fi
