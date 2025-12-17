#!/bin/bash

# 🎉 SETUP RÁPIDO - Execute este script para começar

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      🎉 BoraAgendar + Balasis - Setup Rápido 🎉              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detectar localização
PROJECT_DIR="/Users/user/Desktop/Programação/boraagendar"

echo -e "${BLUE}📁 Diretório do projeto:${NC}"
echo "   $PROJECT_DIR"
echo ""

# Função para exibir próximos passos
show_next_steps() {
    echo ""
    echo -e "${GREEN}✅ Setup Concluído!${NC}"
    echo ""
    echo -e "${BLUE}📋 Próximos Passos:${NC}"
    echo ""
    echo "1️⃣  Terminal 1 - Backend:"
    echo "    cd $PROJECT_DIR"
    echo "    source .venv/bin/activate"
    echo "    python src/manage.py runserver 0.0.0.0:8000"
    echo ""
    echo "2️⃣  Terminal 2 - Frontend:"
    echo "    cd $PROJECT_DIR/frontend"
    echo "    npm install  (primeira vez)"
    echo "    npm run dev"
    echo ""
    echo "3️⃣  Navegador:"
    echo "    http://localhost:5173"
    echo ""
    echo -e "${YELLOW}📚 Documentação:${NC}"
    echo "    - BALASIS_IMPLEMENTACAO_FINALIZADA.md (visão geral)"
    echo "    - FRONTEND_BALASIS_GUIA.md (detalhes frontend)"
    echo "    - COMECE_AQUI_VISUAL.txt (quick start visual)"
    echo ""
}

# Menu principal
show_menu() {
    echo -e "${BLUE}🔧 O que você deseja fazer?${NC}"
    echo ""
    echo "1) 🚀 Frontend: npm install + npm run dev"
    echo "2) 🐍 Backend: python runserver"
    echo "3) 📝 Migrations: makemigrations + migrate"
    echo "4) 🔓 Criar superuser admin"
    echo "5) 🧹 Limpar cache e build"
    echo "6) 📊 Ver status dos serviços"
    echo "7) 📚 Abrir guias de documentação"
    echo "8) 🚀 Versão completa: Backend + Frontend (2 terminais)"
    echo "9) ❌ Sair"
    echo ""
    read -p "Escolha uma opção (1-9): " choice

    case $choice in
        1)
            echo ""
            echo -e "${BLUE}▶️  Iniciando Frontend (npm install + npm run dev)...${NC}"
            echo ""
            cd "$PROJECT_DIR/frontend" || exit
            echo -e "${YELLOW}📦 Instalando dependências...${NC}"
            npm install
            echo ""
            echo -e "${GREEN}✅ Dependências instaladas!${NC}"
            echo ""
            echo -e "${YELLOW}🚀 Iniciando dev server (Vite)...${NC}"
            npm run dev
            ;;
        2)
            echo ""
            echo -e "${BLUE}▶️  Iniciando Backend (Django runserver)...${NC}"
            echo ""
            cd "$PROJECT_DIR" || exit
            if [ ! -f ".venv/bin/activate" ]; then
                echo -e "${YELLOW}⚠️  Virtual env não encontrada. Criando...${NC}"
                python3 -m venv .venv
            fi
            source .venv/bin/activate
            echo -e "${YELLOW}🐍 Iniciando servidor Django...${NC}"
            python src/manage.py runserver 0.0.0.0:8000
            ;;
        3)
            echo ""
            echo -e "${BLUE}▶️  Aplicando Migrations...${NC}"
            echo ""
            cd "$PROJECT_DIR" || exit
            source .venv/bin/activate
            echo -e "${YELLOW}📝 Executando makemigrations...${NC}"
            python src/manage.py makemigrations
            echo ""
            echo -e "${YELLOW}📝 Executando migrate...${NC}"
            python src/manage.py migrate
            echo ""
            echo -e "${GREEN}✅ Migrations aplicadas!${NC}"
            show_next_steps
            ;;
        4)
            echo ""
            echo -e "${BLUE}▶️  Criar Superuser Admin...${NC}"
            echo ""
            cd "$PROJECT_DIR" || exit
            source .venv/bin/activate
            python src/manage.py createsuperuser
            echo ""
            echo -e "${GREEN}✅ Superuser criado!${NC}"
            echo -e "${YELLOW}💡 Acesse em: http://localhost:8000/admin${NC}"
            show_next_steps
            ;;
        5)
            echo ""
            echo -e "${BLUE}▶️  Limpando cache e builds...${NC}"
            echo ""
            cd "$PROJECT_DIR" || exit
            echo -e "${YELLOW}🧹 Limpando __pycache__...${NC}"
            find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
            find . -type f -name "*.pyc" -delete
            echo -e "${YELLOW}🧹 Limpando .pytest_cache...${NC}"
            find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
            cd "$PROJECT_DIR/frontend" || exit
            echo -e "${YELLOW}🧹 Limpando node_modules cache...${NC}"
            rm -rf dist build .next
            echo ""
            echo -e "${GREEN}✅ Cache limpo!${NC}"
            show_next_steps
            ;;
        6)
            echo ""
            echo -e "${BLUE}▶️  Status dos Serviços...${NC}"
            echo ""
            echo -e "${YELLOW}🔍 Django (port 8000):${NC}"
            curl -s http://localhost:8000/ > /dev/null && echo "✅ ONLINE" || echo "❌ OFFLINE"
            echo ""
            echo -e "${YELLOW}🔍 Frontend (port 5173):${NC}"
            curl -s http://localhost:5173/ > /dev/null && echo "✅ ONLINE" || echo "❌ OFFLINE"
            echo ""
            echo -e "${YELLOW}🔍 Banco de dados:${NC}"
            cd "$PROJECT_DIR" || exit
            source .venv/bin/activate
            python -c "import django; django.setup()" > /dev/null 2>&1 && echo "✅ CONECTADO" || echo "❌ DESCONECTADO"
            echo ""
            show_next_steps
            ;;
        7)
            echo ""
            echo -e "${BLUE}📚 Guias de Documentação:${NC}"
            echo ""
            echo "1) Abrir BALASIS_IMPLEMENTACAO_FINALIZADA.md (Overview)"
            echo "2) Abrir FRONTEND_BALASIS_GUIA.md (Guia Frontend - 900+ linhas)"
            echo "3) Abrir COMECE_AQUI_VISUAL.txt (Quick Start Visual)"
            echo "4) Abrir PROGRESSO_BALASIS.md (Detalhes Backend)"
            echo "5) Abrir ESTRATEGIAS_DESENVOLVIMENTO.md (Roadmap)"
            echo "0) Voltar ao menu"
            echo ""
            read -p "Escolha um guia (0-5): " doc_choice
            case $doc_choice in
                1) open "$PROJECT_DIR/BALASIS_IMPLEMENTACAO_FINALIZADA.md" 2>/dev/null || echo "Abra: $PROJECT_DIR/BALASIS_IMPLEMENTACAO_FINALIZADA.md";;
                2) open "$PROJECT_DIR/FRONTEND_BALASIS_GUIA.md" 2>/dev/null || echo "Abra: $PROJECT_DIR/FRONTEND_BALASIS_GUIA.md";;
                3) open "$PROJECT_DIR/COMECE_AQUI_VISUAL.txt" 2>/dev/null || echo "Abra: $PROJECT_DIR/COMECE_AQUI_VISUAL.txt";;
                4) open "$PROJECT_DIR/PROGRESSO_BALASIS.md" 2>/dev/null || echo "Abra: $PROJECT_DIR/PROGRESSO_BALASIS.md";;
                5) open "$PROJECT_DIR/ESTRATEGIAS_DESENVOLVIMENTO.md" 2>/dev/null || echo "Abra: $PROJECT_DIR/ESTRATEGIAS_DESENVOLVIMENTO.md";;
                0) show_menu;;
            esac
            echo ""
            show_menu
            ;;
        8)
            echo ""
            echo -e "${GREEN}🚀 Versão Completa${NC}"
            echo ""
            echo "⚠️  Este script abrirá 2 terminais automaticamente"
            echo ""
            echo "1) Backend em: http://localhost:8000"
            echo "2) Frontend em: http://localhost:5173"
            echo ""
            echo "Digite seu senha (sudo) quando solicitado."
            echo ""
            read -p "Pressione ENTER para continuar..."
            
            # Terminal 1: Backend
            osascript -e "tell app \"Terminal\"
            do script \"cd '$PROJECT_DIR' && source .venv/bin/activate && python src/manage.py runserver 0.0.0.0:8000\"
            end tell" 2>/dev/null &
            
            sleep 2
            
            # Terminal 2: Frontend
            osascript -e "tell app \"Terminal\"
            do script \"cd '$PROJECT_DIR/frontend' && npm run dev\"
            end tell" 2>/dev/null &
            
            echo ""
            echo -e "${GREEN}✅ Terminais abertos!${NC}"
            echo ""
            echo -e "${BLUE}📊 Esperando serviços iniciarem...${NC}"
            sleep 5
            echo ""
            echo -e "${YELLOW}🌐 Abrindo navegador em http://localhost:5173${NC}"
            open "http://localhost:5173" 2>/dev/null || echo "Acesse: http://localhost:5173"
            echo ""
            echo -e "${GREEN}✅ Pronto! Frontend e Backend rodando!${NC}"
            ;;
        9)
            echo ""
            echo -e "${GREEN}👋 Até logo!${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${YELLOW}❌ Opção inválida!${NC}"
            show_menu
            ;;
    esac
}

# Verificar requisitos
check_requirements() {
    echo -e "${BLUE}🔍 Verificando Requisitos...${NC}"
    echo ""
    
    # Python
    if command -v python3 &> /dev/null; then
        echo "✅ Python: $(python3 --version)"
    else
        echo "❌ Python não encontrado. Instale de https://www.python.org/"
        exit 1
    fi
    
    # Node.js
    if command -v node &> /dev/null; then
        echo "✅ Node.js: $(node --version)"
    else
        echo "❌ Node.js não encontrado. Instale de https://nodejs.org/"
        exit 1
    fi
    
    # npm
    if command -v npm &> /dev/null; then
        echo "✅ npm: $(npm --version)"
    else
        echo "❌ npm não encontrado"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Todos os requisitos atendidos!${NC}"
    echo ""
}

# Executar
check_requirements
show_menu
