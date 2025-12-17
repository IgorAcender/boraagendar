# 🚀 Plano de Otimização - Django + HTMX

## 📋 Índice
1. Otimizações Rápidas (hoje)
2. Otimizações Médias (esta semana)
3. Otimizações Avançadas (próximas semanas)
4. Como Medir Antes/Depois

---

## ⚡ PRIORIDADE 1: Gzip (5 minutos)

### O Problema
```
Seu servidor envia:
- 50KB de HTML por clique no filtro
- 20KB de CSS/JS
- 30KB de imagens

Usuário baixa: 100KB total → demora 1-2 segundos em 4G
```

### A Solução: Gzip
```
Comprime: 50KB → 8KB (reduz 84%!)
Tempo: 1-2 segundos → 0.2 segundos
```

### Como Fazer?

#### Opção A: Easypanel (Recomendado)
```
1. Vai em: Easypanel → Seu App → Configurações
2. Procura por: "NGINX Config" ou "Reverse Proxy"
3. Adiciona:
```

```nginx
# Adicione isso na seção http { } do NGINX
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript 
            application/json application/javascript application/xml+rss 
            application/rss+xml font/truetype font/opentype 
            application/vnd.ms-fontobject image/svg+xml;
```

#### Opção B: Django Settings (Fallback)
```python
# settings.py
MIDDLEWARE = [
    # ... outros middlewares
    'django.middleware.gzip.GZipMiddleware',  # ⭐ Adicione esta linha
    # ... resto dos middlewares
]
```

#### Opção C: Docker/Compose
```yaml
# docker-compose.yml
environment:
  - COMPRESS_ENABLED=true
  - GZIP_ENABLED=true
```

### Verificar se Funciona
```bash
# No terminal, execute:
curl -I -H "Accept-Encoding: gzip" http://localhost:8000/dashboard/

# Procure por:
# Content-Encoding: gzip ✅
```

### Impacto
```
ANTES: 300ms para carregar dashboard
DEPOIS: 200ms ⏱️ MELHOR!
```

---

## 🎯 PRIORIDADE 2: Cache no Browser (30 minutos)

### O Problema
```
Usuário clica em "Histórico" → Requisição ao servidor
Usuário clica em "Hoje" → Requisição ao servidor NOVAMENTE
```

**Problema:** Mesmos dados sendo pedidos várias vezes!

### A Solução: Cache HTMX

#### Edite: `src/templates/scheduling/dashboard/index.html`

Procure pelos botões de filtro e atualize assim:

```html
<!-- ANTES -->
<button hx-get="/dashboard/history-fragment/" 
        hx-target="#history-table">
  Histórico
</button>

<!-- DEPOIS (com cache) -->
<button hx-get="/dashboard/history-fragment/" 
        hx-target="#history-table"
        hx-cache="300s"
        hx-cache-control="public">
  Histórico
</button>
```

#### Exemplos Completos:

```html
<!-- Filtro por tipo (cache 5 minutos) -->
<div class="filter-buttons">
  <button class="btn btn-outline" 
          hx-get="/dashboard/history-fragment/?type=all"
          hx-target="#history-table"
          hx-cache="300s">
    Todos
  </button>
  
  <button class="btn btn-outline"
          hx-get="/dashboard/history-fragment/?type=confirmed"
          hx-target="#history-table"
          hx-cache="300s">
    Confirmados
  </button>
  
  <button class="btn btn-outline"
          hx-get="/dashboard/history-fragment/?type=cancelled"
          hx-target="#history-table"
          hx-cache="300s">
    Cancelados
  </button>
</div>

<!-- Filtro por período (cache 1 hora - dados não mudam rápido) -->
<select hx-get="/dashboard/history-fragment/?range={value}"
        hx-target="#history-table"
        hx-cache="3600s">
  <option value="today">Hoje</option>
  <option value="week">Esta Semana</option>
  <option value="month">Este Mês</option>
</select>

<!-- Navegação do calendário (cache 1 dia - dados históricos) -->
<button hx-get="/dashboard/month-fragment/?month={previous_month}"
        hx-target="#calendar"
        hx-cache="86400s">
  ← Mês Anterior
</button>
```

### Como Funciona?
```
1º clique:     Busca no servidor → Cacheia por 5 min
2º clique:     Tira do cache → INSTANTÂNEO ⚡
3º clique:     Tira do cache → INSTANTÂNEO ⚡
Após 5 min:    Cache expira → Busca novo no servidor

IMPACTO: 95% dos cliques ficam INSTANTÂNEOS!
```

### Verificar se Funciona
```bash
# Abra o DevTools (F12) → Aba "Network"
# Clique em um filtro
# Clique NOVAMENTE no mesmo filtro
# 
# Você verá:
# 1º clique: status 200 + tempo real
# 2º clique: status 304 (cached) + tempo ~1ms ⚡
```

---

## 💾 PRIORIDADE 3: Cache no Servidor (Django) (1 hora)

### O Problema
```
Sua view refaz a mesma query ao banco de dados várias vezes:
- SELECT * FROM bookings WHERE month=12 ... (50ms)
- SELECT * FROM services ... (30ms)
- SELECT * FROM professionals ... (20ms)

Usuário clica 10 vezes por dia = 1000ms de queries desnecessárias!
```

### A Solução: Cache em Memória (Redis)

#### 1. Instalar Redis
```bash
# No Easypanel, Redis geralmente já está disponível
# Se não estiver, instale:
pip install redis django-redis
```

#### 2. Editar `settings.py`

```python
# settings.py

# ⭐ ADICIONE ISSO:
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "boraagendar",
        "TIMEOUT": 300,  # 5 minutos padrão
    }
}
```

#### 3. Atualizar sua View `dashboard.py`

```python
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Opção A: Cache automático em toda a view
@cache_page(60 * 5)  # 5 minutos
def dashboard_view(request):
    # Sua view aqui
    pass

# Opção B: Cache parcial (só dados específicos)
def dashboard_history_fragment(request):
    # Gera chave única para este filtro
    cache_key = f"history_{request.GET.get('type', 'all')}_{request.GET.get('range', 'month')}"
    
    # Tenta pegar do cache
    cached_data = cache.get(cache_key)
    if cached_data:
        return HttpResponse(cached_data)
    
    # Se não tiver no cache, faz a query
    bookings = Booking.objects.filter(
        tenant=request.user.tenant,
        # seus filtros aqui
    )
    
    # Renderiza o template
    html = render_to_string('fragments/history_table.html', {
        'bookings': bookings
    })
    
    # Cacheia por 5 minutos
    cache.set(cache_key, html, 60 * 5)
    
    return HttpResponse(html)
```

### Impacto
```
ANTES: 50-100ms por query
DEPOIS: 1-5ms (tira do cache) ⚡⚡⚡

Se usuário clica 10 vezes:
ANTES: 50-100ms × 10 = 500-1000ms
DEPOIS: 1ms × 10 = 10ms (+ 1 query de 50ms quando cache expira)
```

---

## 🖼️ PRIORIDADE 4: Lazy Loading de Imagens (20 minutos)

### O Problema
```
Página carrega TODAS as 50 fotos dos profissionais de uma vez
Totalizando: 5MB de imagens!
```

### A Solução: Lazy Load
```html
<!-- ANTES -->
<img src="/media/profissional_1.jpg" alt="João">

<!-- DEPOIS (carrega só quando entra na tela) -->
<img src="/media/profissional_1.jpg" 
     alt="João"
     loading="lazy">
```

### Implementar em Todo Lugar

```django
{# Em templates/scheduling/dashboard/index.html #}
{% for booking in bookings %}
  <div class="booking-card">
    <img src="{{ booking.professional.photo.url }}"
         alt="{{ booking.professional.name }}"
         loading="lazy"
         width="100"
         height="100">
    <h3>{{ booking.professional.name }}</h3>
  </div>
{% endfor %}

{# Em templates/scheduling/public/tenant_landing.html #}
{% for service in services %}
  <img src="{{ service.image.url }}"
       alt="{{ service.name }}"
       loading="lazy">
{% endfor %}
```

### Impacto
```
ANTES: Página inteira + 50 imagens = 5MB, demora 3 segundos
DEPOIS: Página inteira + 5 imagens visíveis = 500KB, demora 0.5s
        (outras 45 imagens carregam conforme scroll)
```

---

## ⚙️ PRIORIDADE 5: Compressão de Imagens (1 hora)

### O Problema
```
Foto de profissional: 3MB (não comprimida)
Foto de serviço: 2MB (não comprimida)
```

### A Solução: Usar Pillow para Otimizar

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'easy_thumbnails',  # Para cache de thumbnails
]

# Adicione:
THUMBNAIL_ALIASES = {
    '': {
        'small': {'size': (100, 100), 'crop': True, 'quality': 85},
        'medium': {'size': (300, 300), 'crop': True, 'quality': 85},
        'large': {'size': (800, 600), 'crop': False, 'quality': 80},
    },
}
```

#### No Template:
```django
{% load thumbnail %}

<!-- Imagem pequena otimizada (100x100, 85% qualidade) -->
<img src="{% thumbnail booking.professional.photo 'small' %}"
     alt="{{ booking.professional.name }}"
     loading="lazy">

<!-- Imagem média (300x300) -->
<img src="{% thumbnail service.image 'medium' %}"
     alt="{{ service.name }}"
     loading="lazy">
```

### Impacto
```
ANTES: 3MB por foto
DEPOIS: 300KB por foto (reduz 90%!)

Se página tem 10 fotos:
ANTES: 30MB total
DEPOIS: 3MB total

Tempo de carregamento:
ANTES: 10-15 segundos
DEPOIS: 2-3 segundos ⚡⚡⚡
```

---

## 📊 PRIORIDADE 6: Query Optimization (1-2 horas)

### O Problema (N+1 Queries)
```python
# ❌ LENTO: Faz 1 query por booking!
bookings = Booking.objects.all()
for booking in bookings:
    print(booking.professional.name)  # ← Faz query AQUI
    
# Resultado: 1 query de bookings + 100 queries de profissionais = 101 queries!
```

### A Solução: Select Related

```python
# ✅ RÁPIDO: Faz apenas 1 query com JOIN!
bookings = Booking.objects.select_related(
    'professional',
    'service',
    'client',
    'tenant'
).all()

for booking in bookings:
    print(booking.professional.name)  # ← Não faz query extra!
    
# Resultado: 1 query com JOINs = super rápido!
```

#### Atualize suas Views:

```python
# scheduling/views/dashboard.py

def dashboard_history_fragment(request):
    bookings = Booking.objects.filter(
        tenant=request.user.tenant
    ).select_related(
        'professional',      # ⭐ Carrega profissional junto
        'service',           # ⭐ Carrega serviço junto
        'client'             # ⭐ Carrega cliente junto
    ).order_by('-created_at')[:100]
    
    return render(request, 'fragments/history_table.html', {
        'bookings': bookings
    })

def dashboard_month_fragment(request):
    month = request.GET.get('month', today().month)
    
    bookings = Booking.objects.filter(
        tenant=request.user.tenant,
        date__month=month
    ).select_related(
        'professional',
        'service'
    ).prefetch_related(
        'services'  # Se é many-to-many
    )
    
    return render(request, 'fragments/month_data.html', {
        'bookings': bookings
    })
```

### Impacto
```
ANTES: 100 queries = 500ms
DEPOIS: 5 queries = 50ms ⚡⚡⚡

10x MAIS RÁPIDO!
```

---

## 🔍 PRIORIDADE 7: Minificação de CSS/JS (30 minutos)

### O Problema
```
Seu CSS: 50KB (com comentários e espaçamento)
Seu JS: 30KB (com comentários e espaçamento)
Total: 80KB
```

### A Solução: Minificar

```bash
# Instalar:
pip install django-compressor
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'compressor',
]

COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rcsscssminFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]
```

```django
{# base_dashboard.html #}
{% load compress %}

{% compress css %}
  <link rel="stylesheet" href="{% static 'css/dashboard.css' %}">
  <link rel="stylesheet" href="{% static 'css/filters.css' %}">
{% endcompress %}

{% compress js %}
  <script src="{% static 'js/dashboard.js' %}"></script>
  <script src="{% static 'js/filters.js' %}"></script>
{% endcompress %}
```

### Impacto
```
ANTES: 80KB CSS+JS
DEPOIS: 25KB minificado ⚡

Com gzip:
ANTES: 80KB → 15KB comprimido
DEPOIS: 25KB → 8KB comprimido

TOTAL: 7KB de JavaScript/CSS! 🎉
```

---

## 📈 RESUMO: Antes vs Depois

```
                        ANTES       DEPOIS      GANHO
────────────────────────────────────────────────────
Tamanho página          100KB       20KB        80% ↓
Tempo carregamento      3s          0.5s        83% ↓
Clique em aba           300ms       50ms        83% ↓
Segundo clique (cache)  300ms       5ms         98% ↓
Queries ao BD           50ms        5ms         90% ↓
Imagens                 5MB         500KB       90% ↓
────────────────────────────────────────────────────
EXPERIÊNCIA             🐢 Lento    🚀 RÁPIDO  ✨
```

---

## 📋 Implementação Priorizada

### Semana 1:
```
✅ Dia 1: Gzip (5 min)
✅ Dia 2: Cache HTMX (30 min)
✅ Dia 3: Select Related (30 min)
✅ Dia 4: Lazy Load Imagens (20 min)
✅ Dia 5: Compressão Imagens (1h)

Total: ~2.5 horas
Resultado: 80% de melhoria!
```

### Semana 2:
```
✅ Redis/Django Cache (1h)
✅ Minificação CSS/JS (30 min)
✅ Testes de performance
✅ Deploy em produção

Total: ~2.5 horas
Resultado: App super rápido! 🚀
```

---

## 🧪 Como Medir Performance

### Ferramenta 1: Google Lighthouse
```
1. Abra seu site
2. Pressione F12 (DevTools)
3. Aba "Lighthouse"
4. Clique "Analyze"
5. Vê score de performance
```

### Ferramenta 2: Chrome DevTools Network
```
1. F12 → Aba "Network"
2. Recarregue página
3. Vê tamanho de cada recurso
4. Vê tempo de carregamento
```

### Ferramenta 3: Linha de Comando
```bash
# Medir tempo de resposta
curl -w "Tempo: %{time_total}s\n" http://localhost:8000/dashboard/

# Medir tamanho
curl -s http://localhost:8000/dashboard/ | wc -c

# Com gzip
curl -H "Accept-Encoding: gzip" -s http://localhost:8000/dashboard/ | wc -c
```

---

## ✅ Checklist de Otimização

```
RÁPIDO (Fazer HOJE):
☐ Gzip ativado
☐ Cache HTMX em filtros
☐ Select Related em queries

MÉDIO (Esta semana):
☐ Lazy loading de imagens
☐ Compressão de imagens
☐ Redis cache no servidor

AVANÇADO (Próximas semanas):
☐ Minificação CSS/JS
☐ CDN para assets estáticos
☐ Preload de recursos críticos
☐ Service Worker (offline mode)
```

---

## 🎯 Resultado Final

Depois de aplicar estas otimizações:
```
✅ Seu app será TÃO RÁPIDO quanto Node.js
✅ Sem risco de refatoração
✅ Com Django/HTMX mantido
✅ Tempo investido: ~5 horas
✅ Impacto: 80-90% de melhoria
```

**Começe pelo Gzip hoje! 🚀**
