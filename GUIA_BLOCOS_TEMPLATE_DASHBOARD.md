# 🎯 Guia de Blocos de Template do Dashboard

## ⚠️ INFORMAÇÃO CRÍTICA

**Data:** 17 de dezembro de 2025  
**Status:** Implementado e testado ✅

---

## O Problema

Quando foi criado o layout redesenhado do WhatsApp Dashboard (2 colunas), o CSS não estava sendo aplicado mesmo após múltiplas tentativas. A causa raiz foi descoberta ao comparar com outras abas que funcionavam perfeitamente.

### Root Cause
O template estava usando o bloco **ERRADO**: `{% block extra_css %}`

Mas a base template (`base_dashboard.html`) define o bloco como: `{% block extra_head %}`

---

## ✅ SOLUÇÃO

### ❌ ERRADO (Não funciona)
```django
{% extends "base_dashboard.html" %}
{% block extra_css %}
<style>
    /* seus estilos aqui */
</style>
{% endblock %}
```

### ✅ CORRETO (Funciona!)
```django
{% extends "base_dashboard.html" %}
{% block extra_head %}
<style>
    /* seus estilos aqui */
</style>
{% endblock %}
```

---

## 📋 Blocos Disponíveis em `base_dashboard.html`

| Bloco | Localização | Uso | Exemplo |
|-------|-------------|-----|---------|
| `{% block extra_head %}` | `<head>` (linha 582) | Adicionar CSS/JS no head | ✅ **USE ESTE** |
| `{% block content %}` | `<body>` (linha 824) | Conteúdo principal da página | ✅ Para HTML |

### ⚠️ NÃO EXISTE
- `{% block extra_css %}` ❌
- `{% block extra_styles %}` ❌
- `{% block css %}` ❌

---

## 📁 Arquivos Relevantes

### Template Principal
- **Local:** `/src/scheduling/templates/whatsapp/dashboard.html`
- **Bloco usado:** `{% block extra_head %}`
- **Conteúdo:** CSS inline + link para CSS externo

### CSS Externo (Sobrescreve Bootstrap)
- **Local:** `/src/static/css/whatsapp-dashboard.css`
- **Propósito:** Estilos que precisam vencer Bootstrap 5.3.2
- **Técnica:** Seletores com `.content-wrapper` + `!important`

### Base Template
- **Local:** `/src/templates/base_dashboard.html`
- **Linhas importantes:** 
  - 582: `{% block extra_head %}`
  - 824: `{% block content %}`

---

## 🔍 Como as Outras Abas Fazem

As abas que funcionam corretamente também usam `{% block extra_head %}`:

```django
<!-- Exemplo: /src/templates/scheduling/dashboard/index.html -->
{% extends "base_dashboard.html" %}
{% load static %}

{% block title %}Dashboard{% endblock %}

{% block extra_head %}
<style>
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        /* ... */
    }
</style>
{% endblock %}
```

---

## 🎨 Ordem de Carregamento de CSS (Importante!)

```
1. Bootstrap CDN (base_dashboard.html) - 5.3.2
   ↓
2. base_dashboard.html estilos inline
   ↓
3. {% block extra_head %} - seu CSS vai AQUI
   ↓
4. /static/css/whatsapp-dashboard.css (CSS externo)
   ↓
5. {% block content %} - HTML da página
```

**Resultado:** CSS externo tem a MAIOR prioridade e sobrescreve Bootstrap ✅

---

## 🛠️ Quando Modificar o Layout Futuramente

### Checklist:
- [ ] Usar `{% block extra_head %}` (não `extra_css`)
- [ ] Colocar `{% load static %}` no topo
- [ ] Adicionar `<link rel="stylesheet" href="{% static 'css/whatsapp-dashboard.css' %}">` dentro do bloco
- [ ] Usar seletores com `.content-wrapper` para especificidade
- [ ] Adicionar `!important` para vencer Bootstrap quando necessário
- [ ] Fazer `Cmd + Shift + R` no navegador (hard refresh)

### Teste Rápido:
```bash
# Verificar se template está correto
grep "block extra_head" /Users/user/Desktop/Programação/boraagendar/src/scheduling/templates/whatsapp/dashboard.html

# Verificar se CSS externo está vinculado
grep "whatsapp-dashboard.css" /Users/user/Desktop/Programação/boraagendar/src/scheduling/templates/whatsapp/dashboard.html
```

---

## 📊 Exemplo de Estrutura Completa

```django
{% extends "base_dashboard.html" %}
{% load static %}

{% block title %}Gerenciador WhatsApp{% endblock %}

{% block extra_head %}
<!-- CSS INLINE -->
<style>
    .content-wrapper .seu-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
    }
</style>

<!-- CSS EXTERNO (sobrescreve Bootstrap) -->
<link rel="stylesheet" href="{% static 'css/whatsapp-dashboard.css' %}">
{% endblock %}

{% block content %}
<!-- SEU HTML AQUI -->
<div class="content-wrapper">
    <div class="seu-container">
        <!-- conteúdo -->
    </div>
</div>
{% endblock %}
```

---

## 🚀 Resumo

| Aspecto | Detalhes |
|--------|----------|
| **Bloco correto** | `{% block extra_head %}` |
| **Arquivo CSS externo** | `/src/static/css/whatsapp-dashboard.css` |
| **Técnica de especificidade** | `.content-wrapper .seu-seletor` + `!important` |
| **Hard refresh** | `Cmd + Shift + R` no Mac |
| **Bootstrap versão** | 5.3.2 (carrega antes do seu CSS) |

**Status:** ✅ Implementado e funcionando no WhatsApp Dashboard (layout 2 colunas)

---

**Última atualização:** 17 de dezembro de 2025
