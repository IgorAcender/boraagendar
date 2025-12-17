# 🚀 ROADMAP & RECOMENDAÇÕES TÉCNICAS

---

## 📋 PRIORIDADES POR CATEGORIA

### 🔴 CRÍTICO (Bloqueia Deploy)

#### 1. **Restaurar Dashboard Templates** ⚠️
**Status**: Erro 404 em `/dashboard/whatsapp/`  
**Causa**: Arquivo `dashboard.html` foi deletado  
**Impacto**: Dashboard não funciona, impossível gerenciar WhatsApp  
**Solução**:
```bash
# Opção 1: Restaurar via git
git checkout src/scheduling/templates/whatsapp/dashboard.html

# Opção 2: Verificar backup
ls -lh src/scheduling/templates/whatsapp/
```

**Tempo**: 15 minutos  
**Criticidade**: 🔴 BLOQUEADOR

---

#### 2. **Ativar Celery Workers** ⚠️
**Status**: Configurado mas não rodando  
**Causa**: workers não iniciados em docker-compose  
**Impacto**: WhatsApp não envia mensagens, lembretes não funcionam  
**Solução**:
```yaml
# docker-compose.yml - adicionar serviço
celery_worker:
  build: .
  command: celery -A config worker -l info
  depends_on:
    - redis
  environment:
    - DATABASE_URL=${DATABASE_URL}
    - REDIS_URL=redis://redis:6379/0

celery_beat:
  build: .
  command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
  depends_on:
    - redis
```

**Tempo**: 30 minutos  
**Criticidade**: 🔴 BLOQUEADOR

---

#### 3. **Rate Limiting em Autenticação** 🔒
**Status**: Não implementado  
**Risco**: Brute force attacks em login  
**Solução**:
```bash
pip install django-ratelimit
```

```python
# accounts/views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # Máx 5 tentativas por minuto por IP
    pass
```

**Tempo**: 45 minutos  
**Criticidade**: 🔴 SEGURANÇA

---

### 🟡 IMPORTANTE (Próximas 2 semanas)

#### 1. **Email Notifications**
**Status**: Views criadas mas Celery task incompleta  
**O que fazer**:
```python
# notifications/tasks.py (criar)
@shared_task
def send_booking_confirmation_email(booking_id):
    booking = Booking.objects.get(id=booking_id)
    send_email(
        to=booking.customer_email,
        subject=f"Agendamento confirmado - {booking.service.name}",
        template='booking_confirmation.html',
        context={'booking': booking}
    )

@shared_task
def send_reminder_24h_before():
    """Task rodada diariamente pelo beat"""
    tomorrow = timezone.now() + timedelta(days=1)
    bookings = Booking.objects.filter(
        scheduled_for__date=tomorrow.date(),
        status='confirmed'
    )
    for booking in bookings:
        send_booking_reminder_email.delay(booking.id)
```

**Tempo**: 2-3 horas  
**Criticidade**: 🟡 FEATURE

---

#### 2. **Payment Integration (Stripe/PagSeguro)**
**Status**: Não implementado  
**O que fazer**:

```python
# tenants/models.py - adicionar
class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, ...)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pendente'),
        ('succeeded', 'Processado'),
        ('failed', 'Falhou'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

# tenants/views.py
@login_required
def upgrade_plan(request):
    # Redirecionar para checkout Stripe
    # POST create checkout session
    # Webhook em /webhooks/stripe/ para confirmar
    pass
```

**Tempo**: 8-10 horas  
**Criticidade**: 🟡 MONETIZAÇÃO

---

#### 3. **Testes Completos**
**Status**: Cobertura 60%  
**O que fazer**:

```bash
# Adicionar testes para:
# 1. Views de dashboard (criar, editar, deletar)
# 2. API endpoints (permissões)
# 3. Disponibilidade (edge cases)
# 4. WhatsApp integration
# 5. Subscrições (paywall)

python src/manage.py test --cov=. --cov-report=html
```

**Target**: 85%+ cobertura  
**Tempo**: 20-30 horas  
**Criticidade**: 🟡 QUALIDADE

---

### 🟢 BOM TER (Próximo mês)

#### 1. **Google Calendar Integration**
```python
# scheduling/services/google_calendar.py (criar)
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class GoogleCalendarService:
    def __init__(self, tenant):
        self.tenant = tenant
        self.calendar_service = build('calendar', 'v3', credentials=self.get_credentials())
    
    def sync_booking(self, booking):
        """Criar evento no Google Calendar quando agendamento é criado"""
        event = {
            'summary': f"{booking.service.name} - {booking.customer_name}",
            'start': {'dateTime': booking.scheduled_for.isoformat()},
            'end': {'dateTime': (booking.scheduled_for + timedelta(minutes=booking.duration_minutes)).isoformat()},
            'description': booking.notes,
        }
        self.calendar_service.events().insert(calendarId='primary', body=event).execute()
```

**Tempo**: 6-8 horas  
**Criticidade**: 🟢 CONVENIÊNCIA

---

#### 2. **Mobile App (React Native)**
**Status**: 0%  
**Escopo**:
- Authenticação OAuth2
- View de agendamentos (cliente)
- View de agenda (profissional)
- Push notifications
- Offline mode

**Tempo**: 2-3 sprints (80-120 horas)  
**Criticidade**: 🟢 EXPANSÃO

---

#### 3. **Analytics Dashboard**
**Status**: ReportService começado mas incompleto  
**O que fazer**:

```python
# reports/views.py (expandir)
class DashboardAnalyticsView(TemplateView):
    template_name = 'reports/analytics.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.request.tenant
        
        ctx.update({
            'total_bookings': Booking.objects.filter(tenant=tenant).count(),
            'total_revenue': Booking.objects.filter(tenant=tenant).aggregate(
                total=Sum('price')
            ),
            'bookings_by_service': self._get_bookings_by_service(tenant),
            'professional_performance': self._get_professional_performance(tenant),
            'booking_trend': self._get_booking_trend(tenant),  # Últimos 30 dias
            'cancellation_rate': self._get_cancellation_rate(tenant),
        })
        return ctx
```

**Incluir**:
- Gráficos de receita
- Performance por profissional
- Taxa de conversão
- Horários mais populares
- Análise de cancelamento

**Tempo**: 10-12 horas  
**Criticidade**: 🟢 INSIGHTS

---

## 🔧 MELHORIAS TÉCNICAS

### Performance

#### 1. **Database Indexing**
```python
# scheduling/models.py
class Booking(models.Model):
    # ... fields ...
    
    class Meta:
        # Adicionar índices para queries frequentes
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['scheduled_for', 'status']),
            models.Index(fields=['professional', 'scheduled_for']),
            models.Index(fields=['created_at', 'status']),
        ]

# Migração:
# python manage.py makemigrations
# python manage.py migrate
```

**Impacto**: -60% tempo de query  
**Tempo**: 1-2 horas

---

#### 2. **Caching Strategy**
```python
# scheduling/services/availability.py
from django.core.cache import cache
from django.views.decorators.cache import cache_page

def get_available_slots(tenant, service, professional, date):
    # Cache key inclui todos os parâmetros
    cache_key = f"availability:{tenant.id}:{service.id}:{professional.id}:{date}"
    
    slots = cache.get(cache_key)
    if slots is None:
        slots = _calculate_slots(tenant, service, professional, date)
        # Cache por 24h
        cache.set(cache_key, slots, 60*60*24)
    
    return slots

# Invalidar cache quando necessário:
def save_booking(booking):
    # Invalidar disponibilidade do profissional naquele dia
    cache_key = f"availability:{booking.tenant.id}:*:{booking.professional.id}:{booking.scheduled_for.date()}"
    cache.delete_pattern(cache_key)
```

**Impacto**: -80% tempo da lógica de disponibilidade  
**Tempo**: 4-6 horas

---

#### 3. **Query Optimization**
```python
# Antes (N+1 queries):
bookings = Booking.objects.filter(tenant=tenant)
for booking in bookings:
    print(booking.service.name)  # +1 query por booking!

# Depois (1 query):
bookings = Booking.objects.filter(tenant=tenant).select_related(
    'service',
    'professional',
    'tenant'
)

# Ou em caso de M2M:
professionals = Professional.objects.filter(tenant=tenant).prefetch_related(
    'services'
)
```

**Impacto**: -70% queries em listagens grandes  
**Tempo**: 2-3 horas

---

### Segurança

#### 1. **HTTPS & SSL Hardening**
```python
# config/settings.py (produção)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Gerar certificado:
# certbot certonly --standalone -d seu-dominio.com
```

**Tempo**: 1-2 horas

---

#### 2. **Encryption de Dados Sensíveis**
```bash
pip install django-encrypted-model-fields
```

```python
from encrypted_model_fields.fields import EncryptedCharField

class EvolutionAPI(models.Model):
    api_key = EncryptedCharField(max_length=255)  # Criptografado em rest
    
# Migração necessária para dados existentes
```

**Tempo**: 3-4 horas

---

#### 3. **Audit Logging**
```bash
pip install django-audit-log
```

```python
# Rastrear todas as alterações de dados
@transaction.atomic
def delete_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    # Log automaticamente
    audit_log.log_action(
        actor=request.user,
        action='DELETE',
        object=booking,
        changes={'id': booking.id}
    )
    
    booking.delete()
```

**Tempo**: 2-3 horas

---

### Code Quality

#### 1. **Linting & Formatting**
```bash
pip install black flake8 isort pylint
```

```bash
# Formatar código
black src/
isort src/

# Verificar qualidade
flake8 src/ --max-line-length=100
pylint src/ --load-plugins pylint_django
```

**Tempo**: 2 horas (setup) + 10 horas (refactor)

---

#### 2. **Type Hints**
```python
# Antes
def get_tenant_slots(request, service, date):
    # Sem type hints
    pass

# Depois
from typing import List, Optional
from django.http import HttpRequest
from datetime import date as date_type

def get_tenant_slots(
    request: HttpRequest,
    service: Service,
    date: date_type
) -> List[str]:
    """Retorna slots disponíveis para serviço em uma data"""
    pass

# Usar mypy para verificar
mypy src/ --strict
```

**Tempo**: 15-20 horas

---

## 📱 ROADMAP DE FEATURES

### Q1 2025

#### Semana 1-2: Fix & Stabilization
- [x] Restaurar templates deletados
- [x] Ativar Celery workers
- [x] Implementar rate limiting
- [ ] Testes para views críticas
- [ ] Documentação de deploy

**Deliverable**: App estável pronto para MVP

---

#### Semana 3-4: Email Notifications
- [ ] Setup SMTP (Gmail/SendGrid)
- [ ] Templates de email
- [ ] Celery tasks para envio
- [ ] Reminder 24h antes
- [ ] Testes E2E

**Deliverable**: Clientes recebem lembretes por email

---

#### Semana 5-6: Analytics Básico
- [ ] Dashboard de receita
- [ ] Performance por profissional
- [ ] Taxa de conversão
- [ ] CSV export
- [ ] Gráficos (Chart.js)

**Deliverable**: Donos veem dados do negócio

---

#### Semana 7-8: Deployment & Monitoring
- [ ] Setup CI/CD (GitHub Actions)
- [ ] Deploy em produção (Easypanel)
- [ ] Monitoring (Sentry)
- [ ] Logging estruturado
- [ ] Alertas de erro

**Deliverable**: App em produção com monitoramento

---

### Q2 2025

#### Sprint 1: Google Calendar Sync
- [ ] OAuth2 flow
- [ ] Sync bidirecional
- [ ] Conflict detection
- [ ] Testes

**Deliverable**: Calendários sincronizados

---

#### Sprint 2: Payment Integration
- [ ] Stripe/PagSeguro setup
- [ ] Webhook handling
- [ ] Invoice generation
- [ ] Subscription management

**Deliverable**: Monetização ativa

---

#### Sprint 3: SEO & Marketing
- [ ] Schema.org structured data
- [ ] Open Graph tags
- [ ] Meta descriptions
- [ ] Sitemap.xml
- [ ] Google Search Console

**Deliverable**: Melhor ranking em search

---

#### Sprint 4: Dark Mode
- [ ] CSS variables
- [ ] Preference detection
- [ ] Persistent user preference
- [ ] Testing

**Deliverable**: Dark mode funcional

---

### Q3 2025

#### Mobile App MVP
- [ ] React Native setup
- [ ] Auth (OAuth2)
- [ ] Booking list (cliente)
- [ ] Schedule view (profissional)
- [ ] Push notifications

**Deliverable**: Apps iOS & Android no beta

---

## 💰 ESTIMATIVAS DE ESFORÇO

| Task | Horas | Dificuldade | Prioridade |
|------|-------|-------------|-----------|
| Restaurar templates | 0.5 | ⭐ | 🔴 |
| Ativar Celery | 1 | ⭐⭐ | 🔴 |
| Rate limiting | 2 | ⭐ | 🔴 |
| Email notifications | 4 | ⭐⭐ | 🟡 |
| Payment integration | 12 | ⭐⭐⭐ | 🟡 |
| Testes (80% cobertura) | 30 | ⭐⭐ | 🟡 |
| Analytics dashboard | 10 | ⭐⭐ | 🟢 |
| Google Calendar | 8 | ⭐⭐ | 🟢 |
| Mobile app MVP | 120 | ⭐⭐⭐⭐ | 🟢 |
| **TOTAL (até Q2)** | **~180** | | |

**Velocidade estimada**: 20-30 horas/semana = 6-9 semanas para stabilização + features principais

---

## 🎯 KPIs DE SUCESSO

### Técnicos
- [ ] 85%+ test coverage
- [ ] <200ms page load time (p95)
- [ ] 99.9% uptime
- [ ] 0 production errors (SLA)
- [ ] <1min deploy time

### Business
- [ ] 100+ tenants ativos
- [ ] $10k+ MRR
- [ ] <5% churn rate
- [ ] 4.5+ stars nas reviews
- [ ] 50% organic traffic

### User Experience
- [ ] <3 min onboarding
- [ ] 90%+ feature adoption
- [ ] 80%+ booking completion rate
- [ ] <24h support response
- [ ] NPS > 50

---

## 🚨 RISCOS TÉCNICOS

### Alto
1. **WhatsApp Integration Complexa**
   - Risco: Evolution API mudança de API
   - Mitigação: Fallback para SMS/Email
   - Plano B: Integração com Twilio

2. **Database Scalability**
   - Risco: 10M+ bookings por mês
   - Mitigação: Read replicas, sharding
   - Timeline: Q3 2025

3. **Concurrent Bookings**
   - Risco: Double booking em slot mesmo
   - Mitigação: Pessimistic locking em DB
   - Fix: URGENT antes de MVP

---

### Médio
1. **Tenant Isolation**
   - Risco: Data leak entre tenants
   - Mitigação: Testes de segurança
   - Timeline: Q2 2025

2. **Payment Processing**
   - Risco: Falha em charge
   - Mitigação: Retry logic + webhooks
   - Timeline: Q2 2025

3. **Email Deliverability**
   - Risco: Emails caem em spam
   - Mitigação: SPF/DKIM/DMARC setup
   - Timeline: Q1 2025

---

## ✅ CHECKLIST DE PRODUÇÃO

### Infraestrutura
- [ ] Database PostgreSQL em produção
- [ ] Redis para caching/broker
- [ ] SSL/TLS certificado válido
- [ ] Backups automáticos (daily)
- [ ] CDN para assets
- [ ] Monitoring (Sentry/DataDog)

### Código
- [ ] 85%+ test coverage
- [ ] Sem hardcoded secrets
- [ ] Logging estruturado
- [ ] Error tracking setup
- [ ] Rate limiting ativo

### Segurança
- [ ] Autenticação 2FA
- [ ] Encryption at rest
- [ ] CORS headers
- [ ] CSP policy
- [ ] Audit logging
- [ ] Penetration test

### Performance
- [ ] Caching otimizado
- [ ] Database indexes
- [ ] Query N+1 fixes
- [ ] Image optimization
- [ ] GZIP compression
- [ ] <200ms p95 load time

### DevOps
- [ ] CI/CD pipeline
- [ ] Docker production ready
- [ ] Health checks
- [ ] Auto-scaling policies
- [ ] Disaster recovery plan
- [ ] Runbooks documentados

### Documentação
- [ ] README completo
- [ ] API documentation
- [ ] Deployment guide
- [ ] Troubleshooting guide
- [ ] Architecture docs
- [ ] Runbooks

---

## 📞 PRÓXIMOS PASSOS

### Hoje (Dia 1)
1. ✅ Ler análise completa
2. ✅ Restaurar templates
3. ✅ Ativar Celery workers
4. ⏳ Testar app localmente

### Semana 1
1. Implementar rate limiting
2. Setup SMTP para emails
3. Criar base de testes
4. Documentar arquitetura

### Mês 1
1. Completar testes (80%+)
2. Email notifications funcional
3. Analytics básico
4. Deploy em staging

### Mês 2-3
1. Payment integration
2. Google Calendar sync
3. SEO optimizations
4. Production deployment

---

**Roadmap Completo** ✅  
**Última atualização**: 17 de dezembro de 2025  
**Estimativa total**: 180+ horas até Q2 2025
