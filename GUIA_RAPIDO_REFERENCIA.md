# 🔍 GUIA RÁPIDO DE REFERÊNCIA - BoraAgendar

**Versão**: 1.0  
**Data**: 17 de dezembro de 2025  
**Para**: Desenvolvedores que querem entender o código rápido

---

## ⚡ 30 Segundos - O Que É?

**BoraAgendar** = Calendly para barbershops/salões em Django  
- Clientes agendaram online
- Donos gerenciam tudo
- Integração WhatsApp
- Múltiplos negócios (tenants)

---

## 🗺️ MAPA DO CÓDIGO

```
Pasta              O Que É                  Arquivo Principal
═════════════════════════════════════════════════════════════════
accounts/          Auth                     models.py → User
tenants/           Empresas (tenants)       models.py → Tenant, Plan
scheduling/        Agendamentos             models.py → Booking
notifications/     WhatsApp                 client.py, tasks.py
reports/           Relatórios               services.py
raffles/           Rifas/Sorteios          models.py
config/            Settings Django          settings.py
templates/         HTML                     base.html
static/            CSS/JS                   tailwind.css
```

---

## 🎯 PERGUNTAS FREQUENTES

### P: Onde clientes agendaram?
```
A: scheduling/views/public.py → booking_form()
   URL: /{tenant_slug}/ ou /scheduler/
   Template: scheduling/public/booking.html
```

### P: Onde donos gerenciam agenda?
```
A: scheduling/views/dashboard.py
   URL: /dashboard/
   Templates: scheduling/dashboard/*.html
```

### P: Onde fica a lógica de disponibilidade?
```
A: scheduling/services/availability.py → AvailabilityService
   Core: calculate_available_slots()
```

### P: Como tenants são isolados?
```
A: tenants/services.py → TenantMembership
   Filter: queryset.filter(tenant=request.tenant)
   Middleware: get_tenant_for_request()
```

### P: Onde está a integração WhatsApp?
```
A: scheduling/models.py → WhatsAppInstance, EvolutionAPI
   Tasks: notifications/tasks.py
   Client: notifications/client.py
```

### P: Onde estão os planos/subscrições?
```
A: tenants/models_subscription.py
   Models: Plan, Subscription, FeatureUsage
   Decorator: @require_feature('max_services')
```

---

## 🔗 MAIN FILES (Top 20)

| Arquivo | Linhas | O Que Faz |
|---------|--------|----------|
| `src/config/settings.py` | 138 | Configuração Django |
| `src/tenants/models.py` | 200+ | Tenant, TenantMembership |
| `src/scheduling/models.py` | 500+ | Service, Professional, Booking |
| `src/scheduling/services/availability.py` | 300+ | Cálculo disponibilidade |
| `src/scheduling/views/public.py` | 200+ | Página pública booking |
| `src/scheduling/views/dashboard.py` | 800+ | Dashboard views |
| `src/scheduling/api/viewsets.py` | 150+ | DRF endpoints |
| `src/tenants/services.py` | 150+ | Tenant selection logic |
| `src/notifications/client.py` | 100+ | Evolution API client |
| `src/accounts/models.py` | 80+ | Custom User |

---

## 🚀 COMEÇAR A PROGRAMAR

### Setup Inicial (5 min)
```bash
# 1. Ir para pasta
cd /Users/user/Desktop/Programação/boraagendar

# 2. Ativar venv
source .venv/bin/activate

# 3. Rodar servidor
python src/manage.py runserver

# 4. Acessar
open http://localhost:8000
```

### Criar Feature Nova (Generic)
```bash
# 1. Criar model em app específica
# src/scheduling/models.py → adicionar class

# 2. Fazer migration
python src/manage.py makemigrations scheduling
python src/manage.py migrate

# 3. Registrar no admin
# src/scheduling/admin.py → @admin.register(NovaClasse)

# 4. Criar view
# src/scheduling/views/dashboard.py → nova função

# 5. Adicionar URL
# src/config/urls.py → path('nova-feature/', views.nova_feature)

# 6. Criar template
# src/scheduling/templates/dashboard/nova_feature.html

# 7. Testar
# src/scheduling/tests/test_nova.py → TestNovaFeature
```

---

## 🧠 CONCEITOS-CHAVE

### 1. MULTI-TENANCY
```python
# Cada empresa é um Tenant
tenant = Tenant.objects.get(slug='meu-salao')

# Usuários têm acesso via TenantMembership
membership = TenantMembership.objects.get(
    user=request.user,
    tenant=tenant
)

# Query sempre filtra por tenant
bookings = Booking.objects.filter(tenant=tenant)
```

### 2. DISPONIBILIDADE
```python
# Começa com horário de negócio
business_hours = BusinessHours.objects.get(tenant=tenant, day=6)

# + Regras especiais (se houver)
rules = AvailabilityRule.objects.filter(tenant=tenant, day=6)

# - Folgas do profissional
timeoffs = TimeOff.objects.filter(professional=prof, start_date__lte=date)

# - Agendamentos existentes
bookings = Booking.objects.filter(professional=prof, date=date)

# = Slots disponíveis
slots = calculate_available_slots(...)
```

### 3. SEGURANÇA (Roles)
```python
# Owner: Acesso total
# Manager: Dashboard (sem config)
# Professional: Só próprios agendamentos
# Staff: Apenas-leitura

# Validar em views:
from tenants.decorators import require_role
@require_role(['owner', 'manager'])
def criar_servico(request):
    pass
```

### 4. PLANOS
```python
# Free, Pro, Enterprise
plan = subscription.plan

# Check limite
if FeatureUsage.get_usage(subscription, 'max_services') >= plan.max_services:
    return error("Limite atingido, faça upgrade")

# Paywall em template
{% if not can_use_feature 'raffles' %}
    <div class="paywall">Upgrade para usar</div>
{% endif %}
```

---

## 📡 API REST (DRF)

### Endpoints Principais
```
GET  /api/services/              # List serviços do tenant
POST /api/services/              # Criar novo
GET  /api/services/{id}/         # Detalhe
PUT  /api/services/{id}/         # Editar
DELETE /api/services/{id}/       # Deletar

GET  /api/professionals/         # List profissionais
POST /api/bookings/              # Criar agendamento
GET  /api/bookings/              # List agendamentos
```

### Autenticação
```python
# Precisa estar logado + ter membership
IsAuthenticated + TenantScoped
```

### Exemplo Curl
```bash
curl -X GET http://localhost:8000/api/services/ \
  -H "Cookie: sessionid=xxx"
```

---

## 🐛 DEBUGGING

### Log padrão
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Booking criado: {booking.id}")
logger.error(f"Erro ao enviar WhatsApp: {e}")
```

### Django shell
```bash
python src/manage.py shell

# Testar queries
from scheduling.models import Booking
bookings = Booking.objects.filter(tenant__slug='meu-salao')
print(bookings.count())
```

### Breakpoint
```python
# Em views:
def minha_view(request):
    breakpoint()  # Debugger para aqui
    return render(...)

# Rodar: python src/manage.py runserver
# Vai entrar em shell interativo
```

---

## 📊 ESTRUTURA TÍPICA DE UMA VIEW

```python
# src/scheduling/views/dashboard.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from tenants.models import TenantMembership
from scheduling.models import Booking

@login_required
def schedule_list(request):
    # 1. Validar membership
    membership = TenantMembership.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    if not membership:
        raise PermissionDenied("Sem acesso")
    
    # 2. Obter tenant
    tenant = membership.tenant
    
    # 3. Filter queryset por tenant
    bookings = Booking.objects.filter(
        tenant=tenant
    ).select_related(
        'service', 'professional'
    ).order_by('-scheduled_for')
    
    # 4. Contexto para template
    context = {
        'tenant': tenant,
        'bookings': bookings,
        'title': 'Agenda'
    }
    
    # 5. Render
    return render(request, 'scheduling/dashboard/schedule.html', context)
```

---

## 📝 ESTRUTURA TÍPICA DE UM MODEL

```python
# src/scheduling/models.py

from django.db import models
from tenants.models import Tenant

class Service(models.Model):
    # 1. Relacionamento com Tenant (FK)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='services'
    )
    
    # 2. Campos principais
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=30)
    
    # 3. Relacionamentos M2M
    professionals = models.ManyToManyField(
        Professional,
        related_name='services'
    )
    
    # 4. Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 5. Meta
    class Meta:
        verbose_name = "Serviço"
        ordering = ['name']
    
    # 6. String representation
    def __str__(self):
        return f"{self.name} - {self.tenant.name}"
```

---

## 🧪 EXEMPLO DE TESTE

```python
# src/scheduling/tests/test_booking.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from tenants.models import Tenant, TenantMembership
from scheduling.models import Booking, Service

User = get_user_model()

class BookingTestCase(TestCase):
    def setUp(self):
        # 1. Criar dados de teste
        self.user = User.objects.create_user(
            email='test@test.com',
            password='pass123'
        )
        self.tenant = Tenant.objects.create(
            name='Salão Test',
            slug='salao-test'
        )
        TenantMembership.objects.create(
            user=self.user,
            tenant=self.tenant,
            role='owner'
        )
        self.service = Service.objects.create(
            tenant=self.tenant,
            name='Corte',
            price=50.00
        )
    
    def test_criar_booking(self):
        # 2. Executar ação
        booking = Booking.objects.create(
            tenant=self.tenant,
            service=self.service,
            customer_name='João',
            customer_phone='11999999999',
            scheduled_for='2025-12-20 14:00:00',
            status='pending'
        )
        
        # 3. Verificar resultado
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.tenant, self.tenant)
        self.assertTrue(Booking.objects.filter(id=booking.id).exists())
```

---

## 🎨 ESTRUTURA TÍPICA DE TEMPLATE

```html
<!-- src/scheduling/templates/dashboard/schedule.html -->

{% extends "dashboard/base.html" %}

{% block title %}Agenda{% endblock %}

{% block content %}
<div class="container">
    <h1>{{ tenant.name }} - Agenda</h1>
    
    <!-- Filtros -->
    <form method="get" class="mb-4">
        <input type="date" name="date" value="{{ request.GET.date }}">
        <button type="submit">Filtrar</button>
    </form>
    
    <!-- Lista -->
    <div class="space-y-4">
        {% for booking in bookings %}
            <div class="bg-white p-4 rounded border">
                <h3>{{ booking.customer_name }}</h3>
                <p>{{ booking.service.name }} às {{ booking.scheduled_for|date:"H:i" }}</p>
                <span class="badge badge-{{ booking.status }}">
                    {{ booking.get_status_display }}
                </span>
            </div>
        {% empty %}
            <p class="text-gray-500">Nenhum agendamento</p>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

---

## 🔑 KEY FILES POR TAREFA

| Tarefa | Arquivo |
|--------|---------|
| Adicionar novo model | `src/scheduling/models.py` |
| Criar view | `src/scheduling/views/public.py` ou `dashboard.py` |
| Adicionar URL | `src/config/urls.py` |
| Criar template | `src/templates/scheduling/...` |
| Testar | `src/scheduling/tests/test_*.py` |
| Integração WhatsApp | `src/notifications/client.py`, `tasks.py` |
| Admin | `src/scheduling/admin.py` |
| API | `src/scheduling/api/viewsets.py` |
| Regras de negócio | `src/scheduling/services/` |
| Tenant logic | `src/tenants/services.py` |

---

## 🚦 FLUXO DE DEPLOYMENT

```bash
# 1. Testar localmente
python src/manage.py test

# 2. Coletar assets
python src/manage.py collectstatic --noinput

# 3. Aplicar migrations em produção
python src/manage.py migrate --settings=config.settings

# 4. Criar superuser (se novo)
python src/manage.py createsuperuser

# 5. Rodar via Docker
docker-compose -f docker-compose.prod.yml up -d

# 6. Verificar saúde
curl http://localhost/admin/
```

---

## 💾 DATABASE QUERIES ÚTEIS

### Admin Django (shell)
```bash
python src/manage.py shell
```

```python
# Achar booking específico
from scheduling.models import Booking
booking = Booking.objects.get(id=123)
print(booking.customer_name)

# Listar agendamentos de um tenant
from tenants.models import Tenant
tenant = Tenant.objects.get(slug='meu-salao')
bookings = tenant.bookings.all()

# Contar agendamentos por status
from django.db.models import Count
stats = Booking.objects.filter(tenant=tenant).values('status').annotate(count=Count('id'))

# Receita total
from django.db.models import Sum
revenue = Booking.objects.filter(tenant=tenant).aggregate(total=Sum('price'))['total']
```

---

## 🎯 CHECKLIST ANTES DE MERGE

```
[ ] Código segue PEP8
[ ] Testes passam (pytest ou manage.py test)
[ ] Sem erros de linting (flake8)
[ ] Migrations criadas (makemigrations)
[ ] Documentação atualizada
[ ] No console errors/warnings
[ ] Funcionamento no browser testado
[ ] Rebase/merge com main sem conflitos
```

---

## 🆘 PROBLEMAS COMUNS

### Error: "Sem empresa associada"
```python
# Significa: usuário não tem TenantMembership
# Solução: criar membership via admin ou shell
```

### Error: 404 em dashboard
```python
# Significado: Template não encontrado
# Solução: verificar se arquivo existe em templates/
```

### WhatsApp não envia
```python
# Causa: Celery worker não rodando
# Solução: ativar workers em docker-compose
```

### Booking permite double-booking
```python
# Causa: Race condition sem lock
# Solução: usar pessimistic_locking em DB
```

---

## 📚 DOCUMENTAÇÃO RELACIONADA

```
ANALISE_COMPLETA_APP.md
├─ Stack & arquitetura completa
├─ Todos os models detalhados
├─ Features & implementação
└─ Security & deployment

ANALISE_VISUAL_FLUXOS.md
├─ Diagramas ASCII
├─ Fluxo de agendamento
├─ Fluxo de login
├─ Entity Relationship Diagram
└─ Metrics & performance

ROADMAP_TECNICO_DETALHADO.md
├─ Prioridades & fixes
├─ Roadmap Q1-Q3
├─ Recomendações técnicas
└─ Checklist produção
```

---

## 🎓 RECURSOS EXTERNOS

```
Django Docs:      https://docs.djangoproject.com
DRF Docs:         https://www.django-rest-framework.org
PostgreSQL:       https://www.postgresql.org/docs
Redis:            https://redis.io/docs
Docker:           https://docs.docker.com
Evolution API:    https://docs.evolution.rocks
```

---

## ✅ VOCÊ ESTÁ PRONTO!

Agora você conhece:
- ✅ Arquitetura do projeto
- ✅ Onde encontrar cada coisa
- ✅ Como estrutura models/views/templates
- ✅ Como testar mudanças
- ✅ Como fazer deploy

**Próximo passo**: Abrir arquivo com problema e começar a corrigir!

---

**Última atualização**: 17 de dezembro de 2025
