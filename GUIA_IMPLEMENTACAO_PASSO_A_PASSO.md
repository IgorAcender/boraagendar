# 🔧 PASSO-A-PASSO: Implementar Sistema de Planos

## FASE 1: Preparação (15 minutos)

### Passo 1.1: Integrar os modelos ao Tenant

Edite `src/tenants/models.py` e adicione no final:

```python
# No topo, após outros imports
from .models_subscription import Plan, Subscription, FeatureUsage

# Isso já está no arquivo, você só está importando os modelos novos
```

Na verdade, você pode deixar `models_subscription.py` separado. É melhor assim.

---

## FASE 2: Criar as Migrations (5 minutos)

### Passo 2.1: Criar migration automática

```bash
cd /Users/user/Desktop/Programação/boraagendar/src

# Django detecta automaticamente os novos modelos
python manage.py makemigrations tenants
```

Você verá algo como:
```
Migrations for 'tenants':
  tenants/migrations/XXXX_add_subscription_models.py
    - Create model Plan
    - Create model Subscription
    - Create model FeatureUsage
```

### Passo 2.2: Aplicar a migration

```bash
python manage.py migrate tenants
```

Você verá:
```
Running migrations:
  Applying tenants.XXXX_add_subscription_models... OK
```

---

## FASE 3: Registrar no Admin Django (5 minutos)

### Passo 3.1: Editar `tenants/admin.py`

Adicione no final do arquivo:

```python
from .models_subscription import Plan, Subscription, FeatureUsage

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price_monthly', 'is_active')
    list_filter = ('is_active', 'plan_type')
    search_fields = ('name', 'slug')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('slug', 'name', 'description', 'plan_type')
        }),
        ('Preços', {
            'fields': ('price_monthly', 'price_annual')
        }),
        ('Limites', {
            'fields': ('max_professionals', 'max_services', 'max_monthly_bookings')
        }),
        ('Features', {
            'fields': (
                'has_dashboard', 'has_financial_module', 'has_advanced_analytics',
                'has_sms_notifications', 'has_email_campaigns', 'has_customer_reviews',
                'has_custom_domain', 'has_api_access', 'has_white_label'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'plan', 'status', 'billing_cycle', 'trial_ends_at')
    list_filter = ('status', 'billing_cycle', 'created_at')
    search_fields = ('tenant__name', 'stripe_customer_id')
    readonly_fields = ('created_at', 'updated_at', 'started_at')
    
    fieldsets = (
        ('Vínculo', {
            'fields': ('tenant', 'plan')
        }),
        ('Status', {
            'fields': ('status', 'billing_cycle', 'auto_renew')
        }),
        ('Datas', {
            'fields': ('trial_started_at', 'trial_ends_at', 'next_billing_date', 'cancelled_at')
        }),
        ('Pagamento', {
            'fields': ('payment_method', 'stripe_customer_id', 'stripe_subscription_id')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FeatureUsage)
class FeatureUsageAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'feature_name', 'monthly_usage', 'monthly_limit')
    list_filter = ('feature_name', 'reset_date')
    search_fields = ('subscription__tenant__name', 'feature_name')
```

---

## FASE 4: Criar os Planos (10 minutos)

### Passo 4.1: Abrir o Django Admin

```bash
# Certifique-se que está rodando
python manage.py runserver
```

Acesse: `http://localhost:8000/admin/`

### Passo 4.2: Criar Plano FREE

1. Vá para **Tenants > Plans**
2. Clique em **"Add Plan"**
3. Preencha assim:

```
Identificador (slug): free
Nome do Plano: Gratuito
Descrição: Plano gratuito com funcionalidades básicas
Tipo: free
Preço Mensal: 0.00
Preço Anual: 0.00

Máx. Profissionais: 1
Máx. Serviços: 5
Máx. Agendamentos/mês: 50

Acesso ao Dashboard: ✅ (marcado)
Módulo Financeiro: ❌ (desmarcado)
Análises Avançadas: ❌ (desmarcado)
SMS Notifications: ❌ (desmarcado)
Email Campaigns: ❌ (desmarcado)
Customer Reviews: ✅ (marcado)
Custom Domain: ❌ (desmarcado)
API Access: ❌ (desmarcado)
White Label: ❌ (desmarcado)

Ativo: ✅ (marcado)
```

**Clique em Save**

### Passo 4.3: Criar Plano PROFESSIONAL

1. Clique em **"Add Plan"**
2. Preencha assim:

```
Identificador: professional
Nome: Profissional
Descrição: Acesso ao módulo financeiro e campanhas por email
Tipo: professional
Preço Mensal: 99.00
Preço Anual: 990.00

Máx. Profissionais: 10
Máx. Serviços: -1 (ilimitado)
Máx. Agendamentos/mês: -1 (ilimitado)

Acesso ao Dashboard: ✅
Módulo Financeiro: ✅ (IMPORTANTE!)
Análises Avançadas: ❌
SMS Notifications: ✅
Email Campaigns: ✅
Customer Reviews: ✅
Custom Domain: ✅
API Access: ❌
White Label: ❌

Ativo: ✅
```

**Clique em Save**

### Passo 4.4: Criar Plano PREMIUM (opcional)

Repita o processo com:

```
Identificador: premium
Nome: Premium
Preço Mensal: 199.00

Todas as features: ✅ (todas marcadas)
```

---

## FASE 5: Atribuir Plano ao Tenant de Teste (5 minutos)

### Passo 5.1: Acessar Django Shell

```bash
python manage.py shell
```

### Passo 5.2: Criar subscrição para o tenant de teste

```python
from tenants.models import Tenant
from tenants.models_subscription import Plan, Subscription
from django.utils import timezone

# Obter o tenant de teste
tenant = Tenant.objects.get(slug='test-clinic')

# Obter o plano FREE
free_plan = Plan.objects.get(slug='free')

# Criar a subscrição
subscription = Subscription.objects.create(
    tenant=tenant,
    plan=free_plan,
    status='trial',
    trial_started_at=timezone.now(),
    trial_ends_at=timezone.now() + timezone.timedelta(days=14)
)

print(f"✅ Subscrição criada para {tenant.name}")
print(f"   Plano: {subscription.plan.name}")
print(f"   Status: {subscription.status}")
print(f"   Teste expira em: {subscription.trial_days_remaining} dias")
```

Saia com `exit()`

---

## FASE 6: Testar a Verificação (10 minutos)

### Passo 6.1: Testar em Python

```bash
python manage.py shell
```

```python
from tenants.subscription_helpers import get_user_subscription, has_feature
from accounts.models import User

# Obter um usuário
user = User.objects.first()

# Obter a subscription
subscription = get_user_subscription(user)

# Verificar features
print(f"Subscription: {subscription}")
print(f"Plan: {subscription.plan.name}")
print(f"Has Financial Module: {subscription.plan.has_financial_module}")
print(f"Has Advanced Analytics: {subscription.plan.has_advanced_analytics}")

# Verificar com função helper
checker = has_feature('has_financial_module')
print(f"\nCan access financial module: {checker(subscription)}")
```

Você deve ver:
```
Subscription: test-clinic - Gratuito (trial)
Plan: Gratuito
Has Financial Module: False
Has Advanced Analytics: False

Can access financial module: False
```

Perfeito! Saia com `exit()`

---

## FASE 7: Integrar no Template (15 minutos)

### Passo 7.1: No seu `dashboard/index.html`

No topo do arquivo, após `{% extends ... %}`:

```html
{% extends "base_dashboard.html" %}
{% load subscription_tags %}  {# ← ADICIONE ESTA LINHA #}

{% block title %}Dashboard{% endblock %}

{% block content %}
    <!-- seu código existente -->
{% endblock %}
```

### Passo 7.2: Adicionar a Seção Financeira

Antes do `{% endblock %}` final, adicione:

```html
    <!-- SEÇÃO: MÓDULO FINANCEIRO -->
    <section class="dashboard-section financial-section" style="margin-top: 40px;">
        <h2>💰 Módulo Financeiro</h2>
        
        {% if user|has_feature_access:"has_financial_module" %}
            {# Conteúdo desbloqueado #}
            <div class="financial-unlocked">
                <p>Conteúdo financeiro aqui...</p>
                {# Por enquanto, você pode deixar assim #}
            </div>
        {% else %}
            {# Conteúdo bloqueado #}
            <div class="feature-locked" style="
                background: linear-gradient(135deg, #f9f9f9 0%, #f5f5f5 100%);
                border: 2px dashed #d1d5db;
                border-radius: 12px;
                padding: 60px 30px;
                text-align: center;
            ">
                <div style="font-size: 64px; margin-bottom: 20px;">🔒</div>
                
                <h3 style="color: #1F2937; margin: 15px 0;">
                    Módulo Financeiro - Recurso Premium
                </h3>
                
                <p style="color: #6B7280; margin: 15px 0;">
                    Desbloqueie análises completas de receita com relatórios detalhados.
                </p>
                
                <ul style="
                    text-align: left;
                    display: inline-block;
                    color: #555;
                    line-height: 2;
                    margin: 20px 0;
                ">
                    <li>✨ Relatórios de receita detalhados</li>
                    <li>📊 Gráficos de receita por período</li>
                    <li>👤 Análise por profissional</li>
                    <li>🛍️ Análise por serviço</li>
                    <li>📥 Exportar em PDF/CSV</li>
                </ul>
                
                <div style="margin: 25px 0;">
                    <p style="color: #333; margin: 5px 0;">
                        <strong>Plano atual:</strong> 
                        {% get_user_plan user as plan %}
                        {{ plan.name }}
                    </p>
                    <p style="color: #666; margin: 5px 0; font-size: 14px;">
                        <strong>Upgrade para:</strong> Professional ou Premium
                    </p>
                </div>
                
                <a href="#" style="
                    background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
                    color: white;
                    padding: 12px 32px;
                    border: none;
                    border-radius: 6px;
                    font-weight: 600;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                    margin-top: 15px;
                " onmouseover="this.style.boxShadow='0 8px 20px rgba(217, 119, 6, 0.3)'" onmouseout="this.style.boxShadow=''">
                    🚀 Fazer Upgrade Agora
                </a>
                
                <p style="color: #9CA3AF; font-size: 12px; margin-top: 15px;">
                    Professional: R$ 99/mês com todas as features
                </p>
                
                {% if subscription.is_trial %}
                <p style="color: #D97706; font-size: 13px; margin-top: 10px;">
                    ⏱️ Seu período de teste expira em 
                    <strong>{{ subscription.trial_days_remaining }} dias</strong>
                </p>
                {% endif %}
            </div>
        {% endif %}
    </section>
```

### Passo 7.3: Passar dados na view

Em `scheduling/views/dashboard.py`, no contexto:

```python
def index(request):
    # ... seu código existente ...
    
    # Obter a subscription
    try:
        tenant = request.user.tenant_memberships.first().tenant
        subscription = tenant.subscription
    except:
        subscription = None
    
    context = {
        # ... seus dados atuais ...
        'subscription': subscription,
    }
    
    return render(request, 'scheduling/dashboard/index.html', context)
```

---

## FASE 8: Testar no Browser (10 minutos)

### Passo 8.1: Acessar o Dashboard

1. Certifique-se que o servidor está rodando:
   ```bash
   python manage.py runserver
   ```

2. Acesse: `http://localhost:8000/dashboard/`

3. Role para baixo até ver a seção "Módulo Financeiro"

4. Você deve ver algo assim:
   ```
   💰 Módulo Financeiro
   
   🔒
   
   Módulo Financeiro - Recurso Premium
   Desbloqueie análises completas de receita...
   ```

### Passo 8.2: Testar mudança de plano

```bash
python manage.py shell
```

```python
from tenants.models import Tenant
from tenants.models_subscription import Plan

tenant = Tenant.objects.get(slug='test-clinic')
professional_plan = Plan.objects.get(slug='professional')

# Mudar para Professional
subscription = tenant.subscription
subscription.plan = professional_plan
subscription.save()

print("✅ Plano alterado para Professional")
```

Saia e **recarregue a página**. Agora você deve ver o conteúdo desbloqueado! 🎉

---

## FASE 9: Próximos Passos

### Para adicionar dados financeiros reais:

```python
# Em scheduling/views/dashboard.py

from django.db.models import Sum, Count, Q
from scheduling.models import Booking

def index(request):
    # ... código anterior ...
    
    # Calcular receita (se tiver acesso)
    if subscription and subscription.plan.has_financial_module:
        total_revenue = Booking.objects.filter(
            tenant=tenant,
            status='confirmed'
        ).aggregate(Sum('price'))['price__sum'] or 0
        
        context['total_revenue'] = total_revenue
        context['avg_ticket'] = total_revenue / Booking.objects.filter(
            tenant=tenant,
            status='confirmed'
        ).count() if Booking.objects.filter(
            tenant=tenant,
            status='confirmed'
        ).exists() else 0
    
    return render(request, '...', context)
```

---

## ✅ Checklist de Completude

- [ ] Migrations criadas e aplicadas
- [ ] Modelos registrados no admin
- [ ] Planos criados (FREE, PROFESSIONAL)
- [ ] Tenant vinculado ao plano
- [ ] Template tags carregadas
- [ ] Seção bloqueada aparecendo
- [ ] Verificação de feature funciona
- [ ] Mudança de plano funciona
- [ ] Teste no browser bem-sucedido

---

## 🎉 Parabéns!

Você agora tem um **sistema de planos premium funcional**! 

Próximos passos:
1. Implementar gráficos e tabelas de receita
2. Integrar com Stripe para pagamentos
3. Criar página de pricing
4. Adicionar mais features aos planos

Qualquer dúvida, consulte:
- `SISTEMA_PLANOS_PREMIUM.md` - Documentação completa
- `IMPLEMENTACAO_FINANCEIRO_BLOQUEADO.md` - Como implementar mais dados
- `ESTRATEGIA_PAYWALL.md` - Visão geral da estratégia
