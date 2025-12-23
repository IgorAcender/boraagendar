#!/bin/bash
set -e

echo "🚀 BoraAgendar - Setup Local com Docker"
echo "========================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando!${NC}"
    echo "Por favor, inicie o Docker Desktop e tente novamente."
    exit 1
fi

echo -e "${GREEN}✓ Docker está rodando${NC}"

# Verificar se .env existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado. Criando a partir de .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Arquivo .env criado${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANTE: Edite o arquivo .env se necessário antes de continuar${NC}"
    echo "Pressione ENTER para continuar ou CTRL+C para cancelar..."
    read
else
    echo -e "${GREEN}✓ Arquivo .env encontrado${NC}"
fi

echo ""
echo "📦 Parando containers existentes (se houver)..."
docker-compose down 2>/dev/null || true

echo ""
echo "🔨 Fazendo build das imagens..."
docker-compose build

echo ""
echo "🚀 Subindo os serviços..."
docker-compose up -d db redis

echo ""
echo "⏳ Aguardando banco de dados inicializar (10 segundos)..."
sleep 10

echo ""
echo "📊 Rodando migrations..."
docker-compose run --rm web python manage.py migrate

echo ""
echo "👤 Criando superuser (deixe em branco para pular)..."
echo -e "${YELLOW}Se quiser criar depois, use: docker-compose run --rm web python manage.py createsuperuser${NC}"
docker-compose run --rm web python manage.py createsuperuser || echo "Pulando criação de superuser..."

echo ""
echo "📁 Coletando arquivos estáticos..."
docker-compose run --rm web python manage.py collectstatic --noinput

echo ""
echo "🎉 Iniciando servidor web..."
docker-compose up -d web

echo ""
echo "✨ Workers Celery (opcional - pressione ENTER para subir ou CTRL+C para pular)..."
read -t 5 || true
docker-compose up -d worker beat 2>/dev/null || echo "Pulando workers Celery..."

echo ""
echo "================================================"
echo -e "${GREEN}✅ Setup completo!${NC}"
echo ""
echo "🌐 Acesse a aplicação em: http://localhost:8000"
echo "🔧 Admin Django: http://localhost:8000/admin"
echo "📊 Dashboard: http://localhost:8000/dashboard/"
echo ""
echo "📝 Comandos úteis:"
echo "  Ver logs:          docker-compose logs -f web"
echo "  Parar:             docker-compose down"
echo "  Reiniciar:         docker-compose restart web"
echo "  Migrations:        docker-compose run --rm web python manage.py migrate"
echo "  Shell Django:      docker-compose run --rm web python manage.py shell"
echo "  Criar superuser:   docker-compose run --rm web python manage.py createsuperuser"
echo ""
echo "================================================"
