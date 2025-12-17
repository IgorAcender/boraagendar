# 📚 Guia Prático: Como Usar HTMX no Seu Dashboard

## 🎯 Casos de Uso Imediatos

### 1. ✅ Filtrar Histórico (Já Implementado!)

Clique nos botões de filtro e a tabela atualiza sem reload:

```html
<button 
    hx-get="{% url 'dashboard:dashboard_history_fragment' %}"
    hx-vals='{"type": "agendamento"}'
    hx-target="#history-table-container"
    hx-swap="innerHTML">
    Agendamentos
</button>
```

**O que acontece:**
1. Clica no botão
2. HTMX faz GET para `/dashboard/fragmentos/historico/?type=agendamento`
3. Servidor retorna apenas `<table>...</table>`
4. HTMX insere na div `#history-table-container`
5. ✨ Pronto!

---

## 🔨 Como Adicionar HTMX a Novos Filtros

### Exemplo: Filtrar Agendamentos por Status

**1. Criar a view (em `scheduling/views/dashboard.py`):**

```python
@login_required
def booking_filter_fragment(request):
    tenant = request.user.tenant
    status = request.GET.get('status', 'all')
    
    # Filtrar
    bookings = Booking.objects.filter(tenant=tenant)
    if status != 'all':
        bookings = bookings.filter(status=status)
    
    return render(request, "scheduling/dashboard/fragments/booking_list.html", {
        "bookings": bookings
    })
```

**2. Adicionar a URL (em `scheduling/urls/dashboard.py`):**

```python
path("fragmentos/agendamentos/", booking_filter_fragment, name="booking_filter_fragment"),
```

**3. Adicionar os botões no template:**

```html
<button hx-get="{% url 'dashboard:booking_filter_fragment' %}"
        hx-vals='{"status": "pending"}'
        hx-target="#booking-list"
        hx-swap="innerHTML">
    Pendentes
</button>

<button hx-get="{% url 'dashboard:booking_filter_fragment' %}"
        hx-vals='{"status": "confirmed"}'
        hx-target="#booking-list"
        hx-swap="innerHTML">
    Confirmados
</button>

<!-- Container onde os resultados aparecem -->
<div id="booking-list"></div>
```

---

## 🌟 Padrões HTMX Úteis

### 1. **Indicador de Carregamento**

```html
<button hx-get="/api/data/"
        hx-indicator="#loading"
        hx-target="#content">
    Carregar
</button>

<!-- Mostra spinner enquanto carrega -->
<div id="loading" style="display:none;">
    <i class="fas fa-spinner fa-spin"></i> Carregando...
</div>
```

### 2. **Atualização Automática (Poll)**

```html
<!-- Atualiza a cada 5 segundos -->
<div hx-get="/api/notifications/"
     hx-trigger="every 5s"
     hx-swap="innerHTML">
    Notificações...
</div>
```

### 3. **Trigger em Mudança**

```html
<!-- Busca profissionais quando muda o serviço -->
<select name="service"
        hx-get="/api/professionals/"
        hx-trigger="change"
        hx-target="#professional-list">
    <option>Escolha um serviço</option>
    ...
</select>

<div id="professional-list"></div>
```

### 4. **Deletar com Confirmação**

```html
<button hx-delete="/agendamento/123/"
        hx-confirm="Tem certeza que deseja cancelar?"
        hx-target="closest tr"
        hx-swap="outerHTML swap:1s">
    ❌ Cancelar
</button>
```

### 5. **Formulário Dinâmico**

```html
<form hx-post="/agendamento/criar/"
      hx-target="#response"
      hx-swap="innerHTML">
    <input name="cliente" required>
    <input name="data" required>
    <button type="submit">Criar</button>
</form>

<div id="response"></div>
```

---

## 📡 Atributos HTMX Essenciais

| Atributo | O Que Faz | Exemplo |
|----------|-----------|---------|
| `hx-get` | Faz GET AJAX | `hx-get="/api/data/"` |
| `hx-post` | Faz POST AJAX | `hx-post="/criar/"` |
| `hx-delete` | Faz DELETE AJAX | `hx-delete="/remover/1/"` |
| `hx-target` | Onde colocar resposta | `hx-target="#container"` |
| `hx-swap` | Como inserir | `hx-swap="innerHTML"` |
| `hx-trigger` | Quando fazer | `hx-trigger="click"` / `hx-trigger="every 5s"` |
| `hx-vals` | Valores adicionais | `hx-vals='{"tipo":"agendamento"}'` |
| `hx-confirm` | Confirmação | `hx-confirm="Tem certeza?"` |
| `hx-indicator` | Elemento loading | `hx-indicator="#spinner"` |

---

## 🎨 Modos de Inserção (hx-swap)

```html
<!-- Substitui conteúdo interno (padrão) -->
<div hx-swap="innerHTML">...</div>

<!-- Substitui elemento inteiro -->
<div hx-swap="outerHTML">...</div>

<!-- Coloca antes do elemento -->
<div hx-swap="beforebegin">...</div>

<!-- Coloca depois do elemento -->
<div hx-swap="afterend">...</div>

<!-- Anima enquanto swapa -->
<div hx-swap="innerHTML swap:1s">...</div>
```

---

## 🛠️ Fragmentos de Exemplo

### Fragment: Lista de Agendamentos

```django
{# scheduling/dashboard/fragments/booking_list.html #}
{% for booking in bookings %}
<div class="booking-card">
    <h3>{{ booking.customer_name }}</h3>
    <p>{{ booking.scheduled_for|date:"d/m/Y H:i" }}</p>
    <span class="badge badge-{{ booking.status }}">
        {{ booking.get_status_display }}
    </span>
</div>
{% endfor %}
```

### Fragment: Tabela de Profissionais

```django
{# scheduling/dashboard/fragments/professional_table.html #}
<table>
    <tbody>
        {% for prof in professionals %}
        <tr>
            <td>{{ prof.display_name }}</td>
            <td>{{ prof.service_count }} serviços</td>
            <td>
                <button hx-delete="/profissional/{{ prof.id }}/"
                        hx-confirm="Remover {{ prof.display_name }}?"
                        hx-target="closest tr"
                        hx-swap="outerHTML swap:1s">
                    ❌
                </button>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

---

## 🚨 Tratamento de Erros

### View:
```python
@login_required
def create_agendamento(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            return render(request, "success.html")
        else:
            # Retorna com status 400 para indicar erro
            return render(request, "form.html", {"form": form}, status=400)
```

### Template:
```html
<form hx-post="/agendamento/criar/"
      hx-target="#form-container">
    <!-- HTMX automaticamente rehighlights erros -->
</form>
```

---

## 📊 Comparação: Antes vs Depois

### ❌ ANTES (Sem HTMX)

```javascript
document.getElementById('filterBtn').addEventListener('click', function() {
    fetch('/api/data/?type=' + type)
        .then(response => response.json())
        .then(data => {
            let html = '';
            data.forEach(item => {
                html += `<tr><td>${item.name}</td></tr>`;
            });
            document.getElementById('table').innerHTML = html;
        });
});
```

### ✅ DEPOIS (Com HTMX)

```html
<button hx-get="/fragmentos/dados/"
        hx-vals='{"type": "seu-tipo"}'
        hx-target="#table"
        hx-swap="innerHTML">
    Filtrar
</button>
```

---

## 🎓 Workflow Típico com HTMX

1. **View retorna fragmento HTML** (não JSON!)
   ```python
   return render(request, "fragment.html", context)
   ```

2. **Template é um fragmento mínimo** (sem `<html>`, `<body>`)
   ```html
   {% for item in items %}
   <div>{{ item.name }}</div>
   {% endfor %}
   ```

3. **Button/Form dispara HTMX**
   ```html
   <button hx-get="/fragmento/" hx-target="#container">
       Carregar
   </button>
   ```

4. **HTML é inserido no DOM** (automático!)
   ```html
   <div id="container">
       <!-- HTML do fragmento aparece aqui -->
   </div>
   ```

---

## ⚡ Dicas de Performance

1. **Retorne apenas o necessário** (não a página inteira)
2. **Use fragmentos pequenos** (não megablobs de HTML)
3. **Cache GET requests** quando apropriado
4. **Batch múltiplas requisições** com `hx-sync`

```html
<!-- Espera 1s antes de fazer nova requisição -->
<button hx-get="/api/"
        hx-sync="closest button:2.5s">
    Buscar
</button>
```

---

## 🐛 Debugging

Abra o **Console do Navegador** (F12):

```javascript
// Ver eventos HTMX
document.addEventListener('htmx:xhr:loadstart', (e) => {
    console.log('Requisição iniciada:', e.detail.xhr.url);
});

document.addEventListener('htmx:xhr:loadend', (e) => {
    console.log('Requisição concluída:', e.detail.xhr.status);
});
```

---

## 📚 Mais Recursos

- **HTMX Docs:** https://htmx.org
- **Django + HTMX:** https://django-htmx.readthedocs.io
- **Exemplos Práticos:** https://htmx.org/examples/
- **Essays:** https://htmx.org/essays/

---

## ✨ Conclusão

HTMX simplifica drasticamente a interatividade sem necessidade de JS complexo. É a abordagem perfeita para Django!

**Próximo passo?** Aplique HTMX em:
- ✅ Seus filtros de dashboard
- ⏳ Deletar/Editar inline
- ⏳ Busca em tempo real
- ⏳ Auto-complete de campos

---

Happy coding! 🚀
