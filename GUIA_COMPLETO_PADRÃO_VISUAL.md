# 🎨 Aplicação Completa do Padrão Visual em Todas as Abas

## Status de Implementação

### ✅ Já Implementado (Padrão Novo)
- `base_dashboard.html` - Base com sidebar roxo, header com data/hora
- `service_list.html` - Listagem de serviços (tabela moderna)
- `professional_list.html` - Listagem de profissionais (tabela moderna)
- `client_list.html` - Listagem de clientes (tabela moderna)
- `team_list.html` - Listagem de equipes (tabela moderna)
- `index.html` - Dashboard (página inicial)

### 🔄 Em Progresso
- `calendar.html` - Calendário (remover hero-header antigo)
- Outros templates administrativos

---

## 📋 Checklist por Página

### Páginas de Listagem (Tabelas)
```
Estrutura padrão:

{% extends "base_dashboard.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title"><i class="fas fa-icon"></i> Título</h1>
</div>

<div class="data-card">
    <div class="data-card-header">
        <div class="search-box">...</div>
    </div>
    <table class="data-table">...</table>
    <div class="data-card-footer">...</div>
</div>
{% endblock %}
```

**Arquivos a atualizar:**
- [ ] `booking_form.html` - Formulário de agendamento
- [ ] `booking_detail.html` - Detalhes do agendamento

### Páginas de Calendário
```
Estrutura padrão:

{% extends "base_dashboard.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title"><i class="fas fa-calendar"></i> Calendário</h1>
</div>

<!-- Conteúdo do calendário -->
{% endblock %}
```

**Arquivos a atualizar:**
- [x] `calendar.html` - Calendário principal (iniciado)
- [ ] `calendar_day.html` - Calendário dia

### Páginas de Configuração/Formulário
```
Estrutura padrão:

{% extends "base_dashboard.html" %}
{% block content %}
<div class="page-header">
    <h1 class="page-title"><i class="fas fa-icon"></i> Título</h1>
    <p class="page-subtitle">Subtítulo descritivo</p>
</div>

<div class="data-card" style="max-width: 1000px;">
    <div style="padding: 1.5rem;">
        <form>
            <div class="form-group">
                <label>Campo</label>
                <input type="text">
            </div>
            <button class="btn-submit">Salvar</button>
        </form>
    </div>
</div>
{% endblock %}
```

**Arquivos a atualizar:**
- [ ] `tenant_settings.html` - Configurações da empresa
- [ ] `booking_policies.html` - Políticas de agendamento
- [ ] `branding_settings.html` - Cores e marca
- [ ] `default_availability.html` - Horário padrão
- [ ] `my_schedule.html` - Meus horários
- [ ] `my_services.html` - Meus serviços
- [ ] `professional_form.html` - Formulário profissional
- [ ] `professional_services.html` - Serviços do profissional
- [ ] `professional_schedule.html` - Horários do profissional

---

## 🎯 Componentes Padrão

### Page Header
```html
<div class="page-header">
    <h1 class="page-title">
        <i class="fas fa-icon"></i>
        Título da Página
    </h1>
    <p class="page-subtitle">Descrição opcional</p>
</div>
```

### Data Card (Container Principal)
```html
<div class="data-card">
    <!-- Conteúdo aqui -->
</div>
```

### Search Box
```html
<div class="search-box">
    <i class="fas fa-search"></i>
    <input type="text" placeholder="Buscar...">
</div>
```

### Data Table
```html
<table class="data-table">
    <thead>
        <tr>
            <th class="sortable">Coluna <i class="fas fa-sort"></i></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Dado</td>
        </tr>
    </tbody>
</table>
```

### Status Badge
```html
<span class="status-badge status-active">Ativo</span>
<span class="status-badge status-inactive">Inativo</span>
<span class="status-badge status-pending">Pendente</span>
```

### Botões
```html
<!-- Primário -->
<button class="btn-primary"><i class="fas fa-plus"></i> Novo</button>

<!-- Outline -->
<button class="btn-outline"><i class="fas fa-sync-alt"></i> Atualizar</button>

<!-- Ação na tabela -->
<button class="btn-action btn-edit"><i class="fas fa-pencil-alt"></i></button>
<button class="btn-action btn-delete"><i class="fas fa-trash"></i></button>
```

### Form Group
```html
<div class="form-group">
    <label>Rótulo do campo</label>
    <input type="text" placeholder="Digite...">
    <div class="help-text">Texto de ajuda</div>
</div>
```

---

## 🚀 Como Aplicar o Padrão

### 1. **Para Páginas de Listagem (Tabelas)**

Substitua:
```html
<div class="hero-header">
    <div class="hero-content">
        <h1>Título</h1>
    </div>
</div>
```

Por:
```html
<div class="page-header">
    <h1 class="page-title"><i class="fas fa-icon"></i> Título</h1>
</div>
```

### 2. **Para Páginas de Configuração/Formulário**

Remova estilos antigos de `.hero-header` e use:
```html
<div class="page-header">
    <h1 class="page-title"><i class="fas fa-icon"></i> Título</h1>
    <p class="page-subtitle">Descrição</p>
</div>

<div class="data-card" style="max-width: 1000px;">
    <div style="padding: 1.5rem;">
        <!-- Formulário -->
    </div>
</div>
```

### 3. **Para Páginas com Múltiplas Seções**

Use múltiplos `data-card`:
```html
<div class="page-header">
    <h1 class="page-title">Seção 1</h1>
</div>
<div class="data-card"><!-- Conteúdo 1 --></div>

<div class="page-header">
    <h1 class="page-title">Seção 2</h1>
</div>
<div class="data-card"><!-- Conteúdo 2 --></div>
```

---

## 🎨 Referência de Cores

```css
--brand-primary: #6366f1        /* Roxo/Indigo principal */
--brand-secondary: #4f46e5      /* Azul Indigo */

/* Backgrounds */
#f8fafc - Cinza claro (page bg)
#ffffff - Branco (cards)
#1e293b - Escuro (texto)
#64748b - Cinza médio (subtítulo)

/* Status */
#10b981 - Verde (ativo)
#ef4444 - Vermelho (inativo)
#f59e0b - Amarelo (pendente)
```

---

## ✨ Próximos Passos

1. **Aplicar em páginas críticas:**
   - [x] Listagens
   - [ ] Configurações
   - [ ] Calendário

2. **Revisar componentes:**
   - Modais
   - Alerts
   - Toast notifications

3. **Testes:**
   - Mobile responsividade
   - Contraste de cores
   - Acessibilidade

---

## 📞 Dúvidas?

Consulte `base_dashboard.html` para ver todos os estilos CSS disponíveis:
- `.page-header`
- `.page-title`
- `.data-card`
- `.data-card-header`
- `.data-table`
- `.btn-primary`, `.btn-outline`
- `.status-badge`
- `.form-group`
