# 🎯 Exemplo Prático: Implementar Financeiro no Dashboard

## Passo 1: Adicionar a Template Tag

No seu `dashboard/index.html`, no início:

```html
{% load subscription_tags %}
```

## Passo 2: Criar uma Seção Financeira BLOQUEADA

Exemplo de como adicionar ao seu dashboard (após a seção de histórico):

```html
<!-- SEÇÃO: MÓDULO FINANCEIRO (PAYWALL) -->
<section class="dashboard-section financial-module-section">
    <div class="section-header">
        <h2>💰 Módulo Financeiro</h2>
        <div class="section-badge">Premium</div>
    </div>

    {% if user|has_feature_access:"has_financial_module" %}
        
        {# CONTEÚDO DESBLOQUEADO #}
        <div class="financial-content-unlocked">
            
            {# Cards de Métricas Financeiras #}
            <div class="financial-metrics-grid">
                <div class="metric-card financial-highlight">
                    <div class="metric-label">💰 Receita Total</div>
                    <div class="metric-value">R$ {{ total_revenue|floatformat:2 }}</div>
                    <div class="metric-period">{{ period_display }}</div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">📊 Ticket Médio</div>
                    <div class="metric-value">R$ {{ avg_ticket|floatformat:2 }}</div>
                    <div class="metric-period">Por agendamento</div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">📈 Receita Hoje</div>
                    <div class="metric-value">R$ {{ revenue_today|floatformat:2 }}</div>
                    <div class="metric-period">Últimas 24h</div>
                </div>

                <div class="metric-card">
                    <div class="metric-label">💵 Receita Mês</div>
                    <div class="metric-value">R$ {{ revenue_month|floatformat:2 }}</div>
                    <div class="metric-period">Este mês</div>
                </div>
            </div>

            {# Gráfico de Receita #}
            <div class="financial-charts">
                <div class="chart-container">
                    <h3>Receita por Período</h3>
                    <canvas id="revenue-chart" height="80"></canvas>
                </div>
            </div>

            {# Tabela de Receita por Profissional #}
            <div class="financial-table-section">
                <h3>Receita por Profissional</h3>
                <div class="table-responsive">
                    <table class="financial-table">
                        <thead>
                            <tr>
                                <th>Profissional</th>
                                <th>Receita</th>
                                <th>Agendamentos</th>
                                <th>Ticket Médio</th>
                                <th>% do Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for prof in professionals_revenue %}
                            <tr>
                                <td class="prof-name">{{ prof.name }}</td>
                                <td class="value-main">R$ {{ prof.total_revenue|floatformat:2 }}</td>
                                <td>{{ prof.booking_count }}</td>
                                <td>R$ {{ prof.avg_price|floatformat:2 }}</td>
                                <td>
                                    <span class="percentage-badge">
                                        {{ prof.revenue_percentage|floatformat:1 }}%
                                    </span>
                                </td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="5" class="text-center text-muted">
                                    Nenhum dado de receita disponível
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            {# Tabela de Receita por Serviço #}
            <div class="financial-table-section">
                <h3>Receita por Serviço</h3>
                <div class="table-responsive">
                    <table class="financial-table">
                        <thead>
                            <tr>
                                <th>Serviço</th>
                                <th>Vendas</th>
                                <th>Receita</th>
                                <th>Preço Médio</th>
                                <th>% do Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for service in services_revenue %}
                            <tr>
                                <td class="service-name">{{ service.name }}</td>
                                <td>{{ service.booking_count }}</td>
                                <td class="value-main">R$ {{ service.total_revenue|floatformat:2 }}</td>
                                <td>R$ {{ service.avg_price|floatformat:2 }}</td>
                                <td>
                                    <span class="percentage-badge">
                                        {{ service.revenue_percentage|floatformat:1 }}%
                                    </span>
                                </td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="5" class="text-center text-muted">
                                    Nenhum dado de receita disponível
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>

    {% else %}

        {# CONTEÚDO BLOQUEADO - PAYWALL #}
        <div class="financial-content-locked">
            <div class="locked-card">
                
                <div class="locked-header">
                    <div class="lock-icon">🔒</div>
                    <h3>Módulo Financeiro</h3>
                    <span class="badge-premium">Premium</span>
                </div>

                <div class="locked-body">
                    <p class="locked-description">
                        Desbloqueie análises completas de receita com relatórios detalhados, gráficos em tempo real e muito mais.
                    </p>

                    <div class="locked-features">
                        <h4>O que você vai ganhar:</h4>
                        <ul>
                            <li>
                                <span class="feature-icon">📊</span>
                                <span>Relatórios detalhados de receita</span>
                            </li>
                            <li>
                                <span class="feature-icon">📈</span>
                                <span>Gráficos de receita por período</span>
                            </li>
                            <li>
                                <span class="feature-icon">👤</span>
                                <span>Análise de receita por profissional</span>
                            </li>
                            <li>
                                <span class="feature-icon">🛍️</span>
                                <span>Análise de receita por serviço</span>
                            </li>
                            <li>
                                <span class="feature-icon">📥</span>
                                <span>Exportar relatórios em PDF/CSV</span>
                            </li>
                            <li>
                                <span class="feature-icon">📊</span>
                                <span>Comparação período vs período</span>
                            </li>
                        </ul>
                    </div>

                    <div class="locked-footer">
                        <div class="plan-info">
                            <div class="current-plan">
                                <p><strong>Seu plano atual:</strong></p>
                                <p class="plan-name">
                                    {% get_user_plan user as user_plan %}
                                    {{ user_plan.name }}
                                </p>
                            </div>

                            <div class="upgrade-option">
                                <p><strong>Faça upgrade para:</strong></p>
                                <p class="upgrade-plan">Plano Professional ou Superior</p>
                                <p class="upgrade-price">a partir de <strong>R$ 99/mês</strong></p>
                            </div>
                        </div>

                        <a href="{% url 'pricing' %}" class="btn btn-primary btn-lg btn-upgrade">
                            🚀 Upgrade Agora
                        </a>

                        <p class="locked-subtext">
                            Acesso a todas as features premium do BorAgendar
                        </p>

                        {% if subscription.is_trial %}
                        <div class="trial-countdown">
                            <p>
                                ⏱️ Seu período de teste expira em 
                                <strong>{{ subscription.trial_days_remaining }} dias</strong>
                            </p>
                        </div>
                        {% endif %}
                    </div>
                </div>

            </div>
        </div>

    {% endif %}
</section>

<style>
/* ===== MÓDULO FINANCEIRO ===== */

.financial-module-section {
    margin-top: 40px;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.section-header h2 {
    font-size: 24px;
    color: var(--text-primary, #1F2937);
    margin: 0;
}

.section-badge {
    background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}

/* ===== CONTEÚDO DESBLOQUEADO ===== */

.financial-content-unlocked {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.financial-metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.metric-card {
    background: linear-gradient(135deg, #f9f9f9 0%, #f5f5f5 100%);
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 20px;
    transition: all 0.3s ease;
}

.metric-card:hover {
    border-color: #D97706;
    box-shadow: 0 4px 12px rgba(217, 119, 6, 0.1);
}

.metric-card.financial-highlight {
    background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
    color: white;
    border: none;
}

.metric-label {
    font-size: 12px;
    text-transform: uppercase;
    opacity: 0.8;
    margin-bottom: 8px;
    font-weight: 600;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
    margin: 10px 0;
}

.metric-period {
    font-size: 12px;
    opacity: 0.7;
}

.financial-charts {
    margin: 40px 0;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 8px;
}

.financial-charts h3 {
    margin-top: 0;
    color: #1F2937;
}

.financial-table-section {
    margin: 40px 0;
}

.financial-table-section h3 {
    color: #1F2937;
    margin-bottom: 20px;
}

.table-responsive {
    overflow-x: auto;
}

.financial-table {
    width: 100%;
    border-collapse: collapse;
}

.financial-table thead {
    background: #f3f4f6;
    border-bottom: 2px solid #e5e7eb;
}

.financial-table th {
    padding: 15px;
    text-align: left;
    font-weight: 600;
    color: #374151;
    font-size: 13px;
    text-transform: uppercase;
}

.financial-table td {
    padding: 15px;
    border-bottom: 1px solid #e5e7eb;
    color: #4B5563;
}

.financial-table tbody tr:hover {
    background: #f9f9f9;
}

.prof-name,
.service-name {
    font-weight: 600;
    color: #1F2937;
}

.value-main {
    font-weight: 700;
    color: #D97706;
    font-size: 15px;
}

.percentage-badge {
    background: #FEF3C7;
    color: #92400E;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}

/* ===== CONTEÚDO BLOQUEADO - PAYWALL ===== */

.financial-content-locked {
    background: linear-gradient(135deg, #f9f9f9 0%, #f5f5f5 100%);
    border: 2px dashed #d1d5db;
    border-radius: 12px;
    padding: 40px 20px;
}

.locked-card {
    max-width: 700px;
    margin: 0 auto;
    background: white;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    text-align: center;
}

.locked-header {
    margin-bottom: 30px;
}

.lock-icon {
    font-size: 64px;
    margin-bottom: 15px;
    display: block;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.locked-header h3 {
    font-size: 24px;
    color: #1F2937;
    margin: 15px 0;
}

.badge-premium {
    display: inline-block;
    background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    margin-left: 10px;
}

.locked-body {
    text-align: left;
}

.locked-description {
    color: #6B7280;
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 30px;
}

.locked-features {
    background: #f3f4f6;
    border-radius: 8px;
    padding: 25px;
    margin-bottom: 30px;
    text-align: left;
}

.locked-features h4 {
    color: #1F2937;
    margin-top: 0;
    margin-bottom: 15px;
}

.locked-features ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.locked-features li {
    display: flex;
    align-items: center;
    padding: 10px 0;
    color: #4B5563;
    border-bottom: 1px solid #e5e7eb;
}

.locked-features li:last-child {
    border-bottom: none;
}

.feature-icon {
    font-size: 18px;
    margin-right: 12px;
    min-width: 25px;
}

.locked-footer {
    text-align: center;
}

.plan-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 25px;
    padding-bottom: 25px;
    border-bottom: 1px solid #e5e7eb;
}

.current-plan,
.upgrade-option {
    text-align: left;
}

.current-plan p:first-child,
.upgrade-option p:first-child {
    font-size: 12px;
    color: #9CA3AF;
    margin: 0 0 5px 0;
    text-transform: uppercase;
    font-weight: 600;
}

.plan-name {
    font-size: 18px;
    color: #1F2937;
    font-weight: 700;
    margin: 0;
}

.upgrade-plan {
    font-size: 16px;
    color: #D97706;
    font-weight: 700;
    margin: 0 0 5px 0;
}

.upgrade-price {
    font-size: 14px;
    color: #6B7280;
    margin: 0;
}

.btn-upgrade {
    background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
    color: white;
    padding: 14px 40px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    transition: all 0.3s ease;
    margin-bottom: 15px;
}

.btn-upgrade:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(217, 119, 6, 0.3);
}

.locked-subtext {
    color: #9CA3AF;
    font-size: 13px;
    margin: 10px 0;
}

.trial-countdown {
    margin-top: 20px;
    padding: 15px;
    background: #FEF3C7;
    border-radius: 8px;
    color: #92400E;
    font-size: 14px;
}

.trial-countdown p {
    margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
    .plan-info {
        grid-template-columns: 1fr;
    }

    .financial-metrics-grid {
        grid-template-columns: 1fr;
    }

    .locked-card {
        padding: 25px;
    }

    .lock-icon {
        font-size: 48px;
    }
}
</style>
```

## Passo 3: Passar Dados na View

No seu `dashboard.py`, adicione ao contexto:

```python
def index(request):
    # ... seu código existente ...
    
    # Dados financeiros (calculados mesmo que bloqueado)
    context = {
        # ... seus dados atuais ...
        
        # Dados financeiros
        'total_revenue': calculate_total_revenue(tenant, period),
        'revenue_today': calculate_revenue_today(tenant),
        'revenue_month': calculate_revenue_month(tenant),
        'avg_ticket': calculate_avg_ticket(tenant, period),
        'professionals_revenue': get_professionals_revenue(tenant, period),
        'services_revenue': get_services_revenue(tenant, period),
        'subscription': tenant.subscription,
    }
    
    return render(request, 'scheduling/dashboard/index.html', context)
```

## Passo 4: (OPCIONAL) Implementar Cálculos de Receita

```python
# scheduling/views/dashboard.py

from django.db.models import Sum, Count, Avg
from scheduling.models import Booking

def calculate_total_revenue(tenant, period):
    """Calcula receita total do período."""
    bookings = get_bookings_for_period(tenant, period).filter(
        status='confirmed'
    )
    total = bookings.aggregate(Sum('price'))['price__sum'] or 0
    return total

def get_professionals_revenue(tenant, period):
    """Retorna receita por profissional."""
    bookings = get_bookings_for_period(tenant, period).filter(
        status='confirmed'
    )
    
    professionals_data = []
    professionals = Professional.objects.filter(tenant=tenant, is_active=True)
    
    for prof in professionals:
        prof_bookings = bookings.filter(professional=prof)
        total_revenue = prof_bookings.aggregate(Sum('price'))['price__sum'] or 0
        count = prof_bookings.count()
        avg_price = total_revenue / count if count > 0 else 0
        
        professionals_data.append({
            'name': prof.display_name,
            'total_revenue': total_revenue,
            'booking_count': count,
            'avg_price': avg_price,
            'revenue_percentage': (total_revenue / total_bookings_revenue * 100) if total_bookings_revenue > 0 else 0,
        })
    
    return sorted(professionals_data, key=lambda x: x['total_revenue'], reverse=True)
```

---

## 🎉 Resultado Final

Quando o usuário **NÃO TEM** o plano Professional:

```
┌─────────────────────────────────────────────┐
│         💰 Módulo Financeiro  [Premium]     │
├─────────────────────────────────────────────┤
│                                             │
│                    🔒                        │
│                                             │
│            Módulo Financeiro                │
│                                             │
│  Desbloqueie análises completas de receita  │
│  com relatórios detalhados e muito mais.    │
│                                             │
│  ✨ Relatórios de receita detalhados        │
│  📊 Gráficos de receita por período         │
│  👤 Análise por profissional                │
│  🛍️ Análise por serviço                     │
│  📥 Exportar em PDF/CSV                     │
│  📈 Comparação período vs período           │
│                                             │
│  Seu plano atual: Gratuito                  │
│  Faça upgrade para: Professional ou mais    │
│  A partir de: R$ 99/mês                     │
│                                             │
│        [🚀 Upgrade Agora]                   │
│                                             │
│  ⏱️ Teste expira em 7 dias                   │
└─────────────────────────────────────────────┘
```

Quando o usuário **TEM** o plano Professional:

```
┌─────────────────────────────────────────────┐
│         💰 Módulo Financeiro  [Premium]     │
├─────────────────────────────────────────────┤
│                                             │
│  💰 Receita Total    📊 Ticket Médio        │
│  R$ 7.600,00         R$ 150,00              │
│                                             │
│  📈 Receita Hoje     💵 Receita Mês         │
│  R$ 450,00           R$ 2.150,00            │
│                                             │
│  [Gráfico de Receita por Período]           │
│                                             │
│  Receita por Profissional:                  │
│  ┌─────────────┬──────────┬────────────┐   │
│  │ Profissional│ Receita  │ %          │   │
│  ├─────────────┼──────────┼────────────┤   │
│  │ João Silva  │ R$4.500  │ 59,2%      │   │
│  │ Maria Santos│ R$3.100  │ 40,8%      │   │
│  └─────────────┴──────────┴────────────┘   │
│                                             │
│  Receita por Serviço:                       │
│  ┌─────────────┬──────────┬────────────┐   │
│  │ Serviço     │ Receita  │ %          │   │
│  ├─────────────┼──────────┼────────────┤   │
│  │ Corte       │ R$5.100  │ 67,1%      │   │
│  │ Barba       │ R$2.500  │ 32,9%      │   │
│  └─────────────┴──────────┴────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

Perfect! 🎉
