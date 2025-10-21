# Barbearia Agenda SaaS

Sistema de agendamento multicliente (SaaS) inspirado em "Calendly para saloes", construido em Django + DRF. Cada empresa possui pagina publica de agendamento, painel interno, controle de usuarios e envio de lembretes via Evolution API.

## Principais recursos
- Multitenant com isolamento por TenantMembership (papeis: owner, manager, staff, professional)
- Pagina publica para clientes escolherem servico, profissional, data e horario
- Painel interno com resumo, agenda, cadastro de servicos e profissionais
- Disponibilidade inteligente (regras semanais, folgas e bloqueio por agendamentos existentes)
- API REST (servicos, profissionais, agendamentos) limitada ao tenant do usuario logado
- Stub de integracao com Evolution API para confirmar agendamentos via WhatsApp
- Testes basicos para disponibilidade, API e servicos de membros

## Stack tecnica
- Python 3.13, Django 5.1, Django REST Framework
- Postgres 16 + Redis (docker-compose)
- Celery preparado para futuros envios assinc. (worker/beat no compose)
- docker-compose para ambiente completo em VPS (Easypanel ou similar)

## Como iniciar

### 1. Preparar variaveis
```bash
cp .env.example .env
# ajuste SECRET_KEY, DATABASE_URL, Evolution API etc
```

### 2. Rodar com Docker
```bash
docker-compose up --build
# aplica migracoes
docker-compose exec web python manage.py migrate
# cria usuario admin
docker-compose exec web python manage.py createsuperuser
```
A aplicacao web respondera em http://localhost:8000.

### 3. Rodar localmente (sem Docker)
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python src/manage.py migrate
python src/manage.py runserver
```

## Comandos uteis
- `python src/manage.py createsuperuser`
- `python src/manage.py collectstatic`
- `python src/manage.py test scheduling tenants`
- `celery -A config worker -l info` (se rodar filas fora do compose)

## Estrutura
```text
src/
  accounts/            # User customizado
  tenants/             # Tenant, memberships e permissoes
  scheduling/          # Servicos, disponibilidade, views publicas e painel
  notifications/       # Evolution API client stub
  reports/             # Servicos de relatorios (WIP)
  templates/           # HTML publicos e dashboard
```

## Proximos passos sugeridos
1. Habilitar autenticacao (login/logout) e selecao de tenant para usuarios com multiplas empresas
2. Adicionar telas CRUD completas para disponibilidade, folgas e relatorios
3. Integrar envio de lembretes reais (Celery + Evolution API) e filas para relembrar 24h/2h antes
4. Criar operacoes de importacao/exportacao (planilhas, webhooks e automacoes)
5. Implementar personalizacao visual por tenant (logo upload, cores) e public booking page dedicada

Essas etapas levam o MVP para producao com notificacoes confiaveis, funil completo e integra ao ambiente multiempresa desejado.
