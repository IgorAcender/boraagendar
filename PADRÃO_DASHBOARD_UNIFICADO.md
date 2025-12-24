# 📋 Padrão de Design Unificado para o Dashboard

Este documento explica como manter uma **base única, simples e bonita** para todas as abas do dashboard.

---

## 🎨 Estrutura Visual Padrão

Todas as páginas do dashboard seguem este padrão:

```
┌─────────────────────────────────────────────────────────────┐
│  🔵 SIDEBAR ROXO                │  HEADER COM DATA/HORA      │
│  • Painel                       │  Notificação  👤 João      │
│  • Agenda                       │                             │
│  • Serviços                     │  Serviços         + Novo    │
│                                 │  Buscar por...    Atualizar │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 TABELA DE DADOS                                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Serviço      │ Categoria │ Duração │ Preço │ Status   │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ Barba...     │ -         │ 30min   │ R$0,35│ Ativo  ✏ │ │
│  │ Corte...     │ -         │ 40min   │ R$0,45│ Inativo✏ │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Total: 4 serviços    [◀] 1 [▶]                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Como Aplicar em Cada Página

### 1. **Clientes**
```django
{% extends "base_dashboard.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title"><i class="fas fa-users"></i> Clientes</h1>
    <button class="btn-primary" onclick="openNewClientModal();">
        <i class="fas fa-plus"></i> Novo Cliente
    </button>
</div>

<div class="data-card">
    <div class="data-card-header">
        <div class="search-box">
            <i class="fas fa-search"></i>
            <input type="text" placeholder="Buscar por nome...">
        </div>
    </div>
    
    <table class="data-table">
        <thead>
            <tr>
                <th>Cliente</th>
                <th>Telefone</th>
                <th>Status</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
            {% for client in clients %}
            <tr>
                <td><div class="client-info">
                    <span class="client-name">{{ client.name }}</span>
                    <span class="client-email">{{ client.email }}</span>
                </div></td>
                <td>{{ client.phone }}</td>
                <td><span class="status-badge status-active">Ativo</span></td>
                <td><div class="action-buttons">
                    <button class="btn-action btn-edit"><i class="fas fa-pencil-alt"></i></button>
                    <button class="btn-action btn-delete"><i class="fas fa-trash"></i></button>
                </div></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

---

### 2. **Serviços** ✅ Exemplo pronto em `service_list_new.html`

```django
{% extends "base_dashboard.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title"><i class="fas fa-concierge-bell"></i> Serviços</h1>
    <button class="btn-primary">+ Novo Serviço</button>
</div>

<div class="data-card">
    <!-- Tabela com dados do serviço -->
</div>
{% endblock %}
```

---

### 3. **Profissionais**
```django
{% extends "base_dashboard.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title"><i class="fas fa-user-tie"></i> Profissionais</h1>
    <button class="btn-primary">+ Novo Profissional</button>
</div>

<!-- Mesma estrutura -->
{% endblock %}
```

---

## 🎯 Componentes Reutilizáveis

### Tabelas
```html
<div class="data-card">
    <table class="data-table">
        <thead>
            <tr>
                <th class="sortable">Coluna <i class="fas fa-sort"></i></th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Dados</td>
            </tr>
        </tbody>
    </table>
</div>
```

### Badges de Status
```html
<!-- Ativo -->
<span class="status-badge status-active">Ativo</span>

<!-- Inativo -->
<span class="status-badge status-inactive">Inativo</span>

<!-- Pendente -->
<span class="status-badge status-pending">Pendente</span>
```

### Botões
```html
<!-- Primário (Novo Item) -->
<button class="btn-primary">
    <i class="fas fa-plus"></i> Novo
</button>

<!-- Outline (Ação secundária) -->
<button class="btn-outline">
    <i class="fas fa-sync-alt"></i> Atualizar
</button>

<!-- Ações na tabela -->
<button class="btn-action btn-edit"><i class="fas fa-pencil-alt"></i></button>
<button class="btn-action btn-delete"><i class="fas fa-trash"></i></button>
```

### Busca
```html
<div class="search-box">
    <i class="fas fa-search"></i>
    <input type="text" placeholder="Buscar...">
</div>
```

### Info com Duas Linhas
```html
<div class="client-info">
    <span class="client-name">Nome Principal</span>
    <span class="client-email">Subtítulo/Email</span>
</div>
```

---

## 🎨 Cores e Estilos

### Paleta de Cores (já definida no `base_dashboard.html`)

```css
--brand-primary: #6366f1        /* Roxo/Indigo */
--brand-secondary: #4f46e5      /* Azul Indigo */
--sidebar-bg: #312e81 → #1e1b4b /* Roxo Escuro */
```

### Backgrounds
- **Sidebar:** Roxo escuro com gradiente
- **Page:** #f8fafc (cinza claro)
- **Cards:** white (#ffffff)
- **Hover:** #fafbfc

---

## ✅ Checklist para Nova Página

- [ ] Usa `{% extends "base_dashboard.html" %}`
- [ ] Tem `.page-header` com ícone + título
- [ ] Tem botão `.btn-primary` para nova ação
- [ ] Usa `.data-card` para conteúdo
- [ ] Tem `.search-box` para busca
- [ ] Tabela usa `.data-table`
- [ ] Status usa `.status-badge status-{active|inactive|pending}`
- [ ] Ações usam `.btn-action btn-{edit|delete}`
- [ ] Paginação com `.pagination`

---

## 📂 Arquivos de Referência

- `src/templates/base_dashboard.html` - Base principal com todos os estilos
- `src/templates/scheduling/dashboard/service_list_new.html` - Exemplo completo
- `src/templates/layouts/list_base.html` - Template reutilizável (opcional)

---

## 🚀 Próximos Passos

1. **Aplicar em outras páginas:**
   - `professional_list.html`
   - `client_list.html` 
   - `team_list.html`

2. **Criar templates de detalhe:**
   - Formulário para criar/editar item
   - Card única com mais informações

3. **Adicionar funcionalidades:**
   - Modal para novo item
   - Confirmar exclusão
   - Filtros avançados

---

**Resumo:** Use sempre a mesma estrutura (`page-header` → `data-card` → `data-table`) e o dashboard fica bonito, institucional e moderno! 🎉
