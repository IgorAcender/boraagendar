# 🔒 Sistema de Planos e Features Premium

## Overview

Sistema completo de subscrição e controle de features para monetização do BorAgendar. Permite oferecer diferentes níveis de serviço com acesso controlado a features específicas.

---

## 📋 Estrutura de Planos

### Planos Disponíveis

```
┌──────────────────────────────────────────────────────────────┐
│ PLANO                                                         │
├──────────────────────────────────────────────────────────────┤
│ FREE (Gratuito)                                              │
│  - Máx 1 Profissional                                        │
│  - Máx 5 Serviços                                            │
│  - Máx 50 Agendamentos/mês                                   │
│  - Dashboard básico                                          │
│  - ❌ Módulo Financeiro                                      │
│  - ❌ Análises Avançadas                                     │
│                                                               │
│ STARTER ($29/mês)                                            │
│  - Máx 3 Profissionais                                       │
│  - Máx 20 Serviços                                           │
│  - Máx 500 Agendamentos/mês                                  │
│  - Dashboard completo                                        │
│  - ✅ Notificações SMS                                       │
│  - ❌ Módulo Financeiro                                      │
│                                                              │
│ PROFESSIONAL ($99/mês)                                       │
│  - Máx 10 Profissionais                                      │
│  - Ilimitado Serviços                                        │
│  - Ilimitado Agendamentos                                    │
│  - ✅ Módulo Financeiro Completo                             │
│  - ✅ Campanhas por Email                                    │
│  - ✅ Domínio Customizado                                    │
│  - ❌ Análises Avançadas                                     │
│                                                              │
│ PREMIUM ($199/mês)                                           │
│  - Ilimitado Tudo                                            │
│  - ✅ Todas as features                                      │
│  - ✅ Análises Avançadas com IA                              │
│  - ✅ White Label                                            │
│  - ✅ Acesso à API                                           │
│  - ✅ Suporte Prioritário                                    │
│                                                              │
│ ENTERPRISE (Customizado)                                     │
│  - Tudo do Premium +                                         │
│  - Suporte dedicado                                          │
│  - Implementação customizada                                 │
│  - SLA garantido                                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Implementação no Código

### 1. Criar um Plano (Admin)

```python
from tenants.models_subscription import Plan

# Criar plano FREE
free_plan = Plan.objects.create(
    slug='free',
    name='Gratuito',
    plan_type='free',
    price_monthly=0,
    max_professionals=1,
    max_services=5,
    max_monthly_bookings=50,
    has_dashboard=True,
    has_financial_module=False,
)

# Criar plano PROFESSIONAL
pro_plan = Plan.objects.create(
    slug='professional',
    name='Profissional',
    plan_type='professional',
    price_monthly=99.00,
    max_professionals=10,
    max_services=-1,  # Ilimitado
    max_monthly_bookings=-1,  # Ilimitado
    has_dashboard=True,
    has_financial_module=True,  # ✅ Feature Premium
    has_email_campaigns=True,
    has_custom_domain=True,
)
```

### 2. Vincular Plano ao Tenant

```python
from tenants.models_subscription import Subscription

# Criar subscrição
subscription = Subscription.objects.create(
    tenant=tenant,
    plan=free_plan,
    status='active',
    billing_cycle='monthly',
)

# Ou atualizar
subscription = tenant.subscription
subscription.plan = pro_plan
subscription.status = 'active'
subscription.save()
```

### 3. Verificar Acesso em Views

```python
from tenants.subscription_helpers import check_feature_access

# Método 1: Decorador em Views
@check_feature_access('has_financial_module')
def financial_dashboard_view(request):
    """Apenas usuários com plano que tem financial_module podem acessar."""
    return render(request, 'financial/dashboard.html')

# Método 2: Verificação Manual em Views
def some_view(request):
    subscription = request.user.tenant_memberships.first().tenant.subscription
    
    if not subscription.plan.has_financial_module:
        return HttpResponseForbidden("Acesso negado")
    
    return render(request, 'template.html')
```

### 4. Verificar Acesso em Templates

```html
{# Método 1: Filter #}
{% load subscription_tags %}

{% if user|has_feature_access:"has_financial_module" %}
    <div class="financial-section">
        <!-- Conteúdo financeiro -->
    </div>
{% else %}
    <div class="upgrade-message">
        <p>Faça upgrade para acessar o módulo financeiro</p>
        <a href="{% url 'plans' %}" class="btn btn-primary">Upgrade</a>
    </div>
{% endif %}

{# Método 2: Simple Tag #}
{% get_user_plan user as user_plan %}

{% if user_plan.has_financial_module %}
    <!-- Conteúdo desbloqueado -->
{% endif %}
```

### 5. Mostrar Seção Bloqueada (Paywalled)

```html
{# Seção "Financeiro" bloqueada #}
<div class="dashboard-section financial-section">
    <h2>💰 Módulo Financeiro</h2>
    
    {% if user|has_feature_access:"has_financial_module" %}
        <!-- Conteúdo real do módulo financeiro -->
        {% include "financial/module.html" %}
    {% else %}
        <!-- Componente de bloqueio -->
        <div class="feature-locked">
            <div class="lock-icon">🔒</div>
            <h3>Recurso Premium</h3>
            <p>Este módulo está disponível apenas no plano Professional e acima.</p>
            
            <a href="{% url 'plans' %}" class="btn btn-primary btn-lg">
                Fazer Upgrade Agora
            </a>
            
            {% if subscription.is_trial %}
                <p class="text-muted">
                    Seu teste expira em {{ subscription.trial_days_remaining }} dias
                </p>
            {% endif %}
        </div>
    {% endif %}
</div>

<style>
.feature-locked {
    position: relative;
    padding: 60px 30px;
    text-align: center;
    background: linear-gradient(135deg, #f5f5f5 0%, #fafafa 100%);
    border: 2px dashed #ddd;
    border-radius: 8px;
    color: #666;
}

.lock-icon {
    font-size: 48px;
    margin-bottom: 20px;
}

.feature-locked h3 {
    color: #333;
    margin: 15px 0;
}

.feature-locked p {
    color: #999;
    margin: 10px 0;
}

.feature-locked .btn {
    margin-top: 20px;
}
</style>
```

---

## 🎨 Implementação no Dashboard Financeiro

### Exemplo Completo: Dashboard com Financeiro Bloqueado

```html
{% extends "base_dashboard.html" %}
{% load subscription_tags %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<div class="dashboard-container">
    <!-- SEÇÃO 1: Métricas Básicas (Sempre visível) -->
    <section class="dashboard-section metrics-section">
        <h2>📊 Resumo de Agendamentos</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>{{ total_bookings }}</h3>
                <p>Agendamentos</p>
            </div>
            <div class="metric-card">
                <h3>{{ confirmados }}%</h3>
                <p>Confirmados</p>
            </div>
            <div class="metric-card">
                <h3>{{ cancelamentos }}</h3>
                <p>Cancelamentos</p>
            </div>
        </div>
    </section>

    <!-- SEÇÃO 2: Ranking de Profissionais (Sempre visível) -->
    <section class="dashboard-section professionals-section">
        <h2>🏆 Melhores Profissionais</h2>
        <table class="professionals-table">
            <thead>
                <tr>
                    <th>Profissional</th>
                    <th>Agendamentos</th>
                    <th>Cancelamentos</th>
                </tr>
            </thead>
            <tbody>
                {% for prof in top_professionals %}
                <tr>
                    <td>{{ prof.name }}</td>
                    <td>{{ prof.bookings }}</td>
                    <td>{{ prof.cancellations }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </section>

    <!-- SEÇÃO 3: MÓDULO FINANCEIRO (BLOQUEADO/PREMIUM) -->
    <section class="dashboard-section financial-section">
        <h2>💰 Módulo Financeiro</h2>
        
        {% if user|has_feature_access:"has_financial_module" %}
            {# Conteúdo desbloqueado #}
            <div class="financial-content">
                <div class="financial-metrics">
                    <div class="metric-card highlight">
                        <h3>R$ {{ total_revenue }}</h3>
                        <p>Receita Total</p>
                    </div>
                    <div class="metric-card">
                        <h3>R$ {{ avg_ticket }}</h3>
                        <p>Ticket Médio</p>
                    </div>
                    <div class="metric-card">
                        <h3>R$ {{ revenue_today }}</h3>
                        <p>Receita Hoje</p>
                    </div>
                </div>

                <div class="financial-charts">
                    <div class="chart-container">
                        <h3>Receita por Período</h3>
                        <canvas id="revenue-chart"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>Receita por Serviço</h3>
                        <canvas id="service-revenue-chart"></canvas>
                    </div>
                </div>

                <div class="financial-details">
                    <h3>Receita por Profissional</h3>
                    <table class="financial-table">
                        <thead>
                            <tr>
                                <th>Profissional</th>
                                <th>Receita</th>
                                <th>Agendamentos</th>
                                <th>Ticket Médio</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for prof_revenue in professionals_revenue %}
                            <tr>
                                <td>{{ prof_revenue.professional }}</td>
                                <td>R$ {{ prof_revenue.revenue }}</td>
                                <td>{{ prof_revenue.bookings }}</td>
                                <td>R$ {{ prof_revenue.avg_ticket }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        {% else %}
            {# Conteúdo bloqueado com call-to-action #}
            <div class="feature-locked-container">
                <div class="feature-locked-card">
                    <div class="lock-icon">🔒</div>
                    
                    <h3>Módulo Financeiro - Recurso Premium</h3>
                    
                    <p class="lock-description">
                        Desbloqueie análises completas de receita, relatórios financeiros detalhados e muito mais com o plano Professional.
                    </p>
                    
                    <div class="locked-benefits">
                        <ul>
                            <li>✨ Relatórios de receita detalhados</li>
                            <li>📊 Gráficos de receita por período</li>
                            <li>💵 Análise por profissional e serviço</li>
                            <li>📈 Comparação período vs período</li>
                            <li>📥 Exportar relatórios em PDF/CSV</li>
                        </ul>
                    </div>
                    
                    <a href="{% url 'plans' %}" class="btn btn-primary btn-lg">
                        🚀 Upgrade para Professional
                    </a>
                    
                    <p class="lock-price">
                        <strong>Professional: R$ 99/mês</strong> com todas as features
                    </p>
                    
                    {% if subscription.is_trial %}
                    <p class="trial-info">
                        ⏱️ Seu período de teste expira em <strong>{{ subscription.trial_days_remaining }} dias</strong>
                    </p>
                    {% endif %}
                </div>
            </div>
        {% endif %}
    </section>

    <!-- SEÇÃO 4: Análises Avançadas (PREMIUM) -->
    <section class="dashboard-section analytics-section">
        <h2>📈 Análises Avançadas</h2>
        
        {% if user|has_feature_access:"has_advanced_analytics" %}
            <!-- Conteúdo de análises avançadas -->
            {% include "dashboard/advanced_analytics.html" %}
        {% else %}
            <div class="feature-locked-container">
                <div class="feature-locked-card">
                    <div class="lock-icon">🔒</div>
                    <h3>Análises Avançadas - Recurso Premium</h3>
                    <p>Disponível apenas no plano Premium</p>
                    <a href="{% url 'plans' %}" class="btn btn-secondary">Upgrade para Premium</a>
                </div>
            </div>
        {% endif %}
    </section>

</div>

<style>
.feature-locked-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    background: linear-gradient(135deg, #f9f9f9 0%, #f5f5f5 100%);
    border-radius: 12px;
    border: 2px dashed #e0e0e0;
}

.feature-locked-card {
    text-align: center;
    padding: 40px;
    max-width: 500px;
}

.lock-icon {
    font-size: 64px;
    margin-bottom: 20px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

.feature-locked-card h3 {
    font-size: 24px;
    color: #333;
    margin: 20px 0 10px;
}

.lock-description {
    color: #666;
    margin: 15px 0 25px;
    line-height: 1.6;
}

.locked-benefits {
    text-align: left;
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.locked-benefits ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.locked-benefits li {
    padding: 10px 0;
    color: #555;
    border-bottom: 1px solid #f0f0f0;
}

.locked-benefits li:last-child {
    border-bottom: none;
}

.btn {
    display: inline-block;
    padding: 12px 32px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    margin: 20px 0;
    transition: all 0.3s ease;
}

.btn-primary {
    background-color: #D97706;
    color: white;
}

.btn-primary:hover {
    background-color: #B45309;
    transform: translateY(-2px);
}

.lock-price {
    color: #999;
    font-size: 14px;
    margin-top: 15px;
}

.trial-info {
    color: #D97706;
    font-size: 13px;
    margin-top: 10px;
}
</style>

{% endblock %}
```

---

## 📊 Views com Verificação de Features

```python
# scheduling/views/dashboard.py

from django.shortcuts import render
from tenants.subscription_helpers import check_feature_access, get_user_subscription

@check_feature_access('has_financial_module')
def financial_dashboard_view(request):
    """Dashboard financeiro - apenas usuários com feature."""
    # Lógica para gerar dados financeiros
    context = {
        'total_revenue': 7600.00,
        'revenue_today': 450.00,
        'professionals_revenue': [...]
    }
    return render(request, 'dashboard/financial.html', context)


def main_dashboard_view(request):
    """Dashboard principal - sempre acessível."""
    subscription = get_user_subscription(request.user)
    
    context = {
        'subscription': subscription,
        'has_financial_access': subscription.plan.has_financial_module if subscription else False,
        'has_analytics_access': subscription.plan.has_advanced_analytics if subscription else False,
    }
    return render(request, 'dashboard/index.html', context)
```

---

## 🔧 Migration para Aplicar

```python
# tenants/migrations/00XX_add_subscription_models.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0XXX_previous_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True, verbose_name='Identificador')),
                ('name', models.CharField(max_length=100, verbose_name='Nome do Plano')),
                # ... outros campos
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'Ativo'), ...], default='trial', max_length=20, verbose_name='Status')),
                # ... outros campos
                ('plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tenants.plan')),
                ('tenant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='tenants.tenant')),
            ],
        ),
    ]
```

---

## 🚀 Próximos Passos

1. **Criar Planos no Admin**: Defina FREE, STARTER, PROFESSIONAL, PREMIUM
2. **Aplicar Migrations**: `python manage.py migrate`
3. **Implementar Seção Financeiro**: Use template tags para bloquear
4. **Teste**: Mude plano de um tenant e veja bloqueio funcionando
5. **Stripe Integration** (opcional): Integrar pagamentos reais
6. **Feature Tracking**: Rastrear uso (bookings por mês, etc)

---

## 💡 Customizações Possíveis

- Adicionar mais features aos planos
- Integrar com Stripe para pagamentos
- Criar trial automático (14 dias)
- Enviar emails de upgrade
- Mostrar uso de features em tempo real
- Limites dinâmicos de bookings/mês
