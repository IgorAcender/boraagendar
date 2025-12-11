# ⚡ Quick Start: 5 Minutos

Se você quer começar AGORA sem ler tudo, aqui está o essencial.

---

## O Que Você Tem

Um **sistema completo** para vender o Módulo Financeiro como Premium.

---

## 3 Passos Para Começar

### 1️⃣ Rodar Migrations (2 min)

```bash
cd /Users/user/Desktop/Programação/boraagendar/src
python manage.py makemigrations tenants
python manage.py migrate tenants
```

Pronto! Banco de dados atualizado.

---

### 2️⃣ Criar Planos no Admin (2 min)

1. Abra: `http://localhost:8000/admin/`
2. Vá em **Tenants > Plans** e crie 2 planos:

**PLANO 1: FREE**
```
Slug: free
Nome: Gratuito
Preço: 0.00
Módulo Financeiro: ❌ (desmarcado)
Ativo: ✅
```

**PLANO 2: PROFESSIONAL**
```
Slug: professional
Nome: Profissional
Preço: 99.00
Módulo Financeiro: ✅ (marcado)
Ativo: ✅
```

Save! Pronto!

---

### 3️⃣ Testar (1 min)

```bash
python manage.py shell
```

```python
from tenants.models import Tenant
from tenants.models_subscription import Plan, Subscription
from django.utils import timezone

# Obter tenant
tenant = Tenant.objects.get(slug='test-clinic')

# Obter plano FREE
free_plan = Plan.objects.get(slug='free')

# Criar subscrição
subscription = Subscription.objects.create(
    tenant=tenant,
    plan=free_plan,
    status='trial',
    trial_ends_at=timezone.now() + timezone.timedelta(days=14)
)

print("✅ Pronto! Subscription criada")
```

Saia com `exit()`

---

## Como Usar no Template

No seu `dashboard/index.html`:

```html
{% load subscription_tags %}

{% if user|has_feature_access:"has_financial_module" %}
    {# Conteúdo financeiro aqui #}
    <div>Dados de receita...</div>
{% else %}
    {# Bloqueio #}
    <div style="text-align: center; padding: 40px;">
        <h2>🔒 Módulo Financeiro</h2>
        <p>Faça upgrade para Professional (R$ 99/mês)</p>
        <a href="#" class="btn btn-primary">Upgrade Agora</a>
    </div>
{% endif %}
```

---

## Testar No Navegador

1. Acesse: `http://localhost:8000/dashboard/`
2. Você verá a seção financeira BLOQUEADA (com o bloqueio)
3. Agora mude o plano:

```bash
python manage.py shell
```

```python
from tenants.models import Tenant
from tenants.models_subscription import Plan

tenant = Tenant.objects.get(slug='test-clinic')
prof_plan = Plan.objects.get(slug='professional')

subscription = tenant.subscription
subscription.plan = prof_plan
subscription.save()

print("✅ Plano alterado!")
```

4. Recarregue a página
5. **Magia**: A seção agora está DESBLOQUEADA! 🎉

---

## Próximos Passos

- Leia `VISUAL_RESUMO_PLANOS.md` para entender melhor
- Siga `GUIA_IMPLEMENTACAO_PASSO_A_PASSO.md` para integrar no dashboard
- Leia `IMPLEMENTACAO_FINANCEIRO_BLOQUEADO.md` para adicionar dados de receita

---

## 🎉 Pronto!

Você agora tem um **sistema de planos funcionando**.

Qualquer dúvida, procure nos docs criados.

**Próximo: Integrar dados reais de receita no financeiro!**
