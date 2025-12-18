# 🎨 Refatoração de Templates com Tailwind

## Fase 1: Remover Bootstrap, Adicionar Tailwind

### Base Dashboard (`base_dashboard.html`)

Vamos transformar seu template atual de ~1200 linhas em algo muito mais limpo!

## 📋 O que Fazer

### 1. Remover imports antigos
```html
<!-- REMOVER ISSO -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">

<!-- ADICIONAR ISSO -->
<link href="{% static 'css/tailwind.css' %}" rel="stylesheet">
```

### 2. Remover <style> inline
```html
<!-- REMOVER: Toda essa seção (linhas ~12-150) -->
<style>
  :root { ... }
  body { ... }
  .sidebar-container { ... }
  /* ... 150 linhas ... */
</style>

<!-- SUBSTITUIR POR: Classes Tailwind diretas no HTML -->
```

### 3. Substituir classes Bootstrap por Tailwind

#### Exemplo 1: Sidebar

**ANTES (Bootstrap)**:
```html
<div class="sidebar-container">
  <div class="sidebar-header">
    <div class="logo-section">
      <div class="logo-container">
        <i class="fas fa-calendar-alt"></i>
      </div>
    </div>
  </div>
</div>

<style>
  .sidebar-container {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 280px;
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    color: #e2e8f0;
  }
  
  .logo-container {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, var(--brand-primary), var(--brand-secondary));
    border-radius: 10px;
  }
</style>
```

**DEPOIS (Tailwind)**:
```html
<div class="fixed inset-y-0 left-0 w-64 bg-gradient-to-b from-slate-800 to-slate-950 text-slate-100 overflow-y-auto z-50 shadow-lg">
  <div class="px-4 py-6 border-b border-slate-700 flex items-center gap-3">
    <div class="w-10 h-10 bg-gradient-to-br from-brand-primary to-brand-secondary rounded-lg flex items-center justify-center text-white">
      <i class="fas fa-calendar-alt text-lg"></i>
    </div>
  </div>
</div>
```

**Mapping**:
- `position: fixed; left: 0; top: 0; bottom: 0;` → `fixed inset-y-0 left-0`
- `width: 280px;` → `w-64`
- `background: linear-gradient(...)` → `bg-gradient-to-b from-slate-800 to-slate-950`
- `color: #e2e8f0;` → `text-slate-100`
- `z-index: 1000;` → `z-50`
- `padding: 1.5rem 1rem;` → `px-4 py-6`
- `border-bottom: 1px solid rgba(...)` → `border-b border-slate-700`
- `display: flex; align-items: center;` → `flex items-center`
- `gap: 0.75rem;` → `gap-3`

#### Exemplo 2: Botões

**ANTES**:
```html
<button class="btn btn-primary">Salvar</button>

<style>
  .btn {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s ease;
  }
  
  .btn-primary {
    background-color: #3b82f6;
    color: white;
  }
  
  .btn-primary:hover {
    background-color: #2563eb;
  }
</style>
```

**DEPOIS**:
```html
<button class="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors duration-200">
  Salvar
</button>

<!-- Ou use a classe reutilizável -->
<button class="btn-primary">Salvar</button>
```

(A classe `btn-primary` já está definida em `tailwind-input.css`)

#### Exemplo 3: Cards

**ANTES**:
```html
<div class="card">
  <h3 class="card-title">Título</h3>
  <p class="card-text">Descrição</p>
</div>

<style>
  .card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border: 1px solid #e2e8f0;
  }
  
  .card-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
  }
</style>
```

**DEPOIS**:
```html
<div class="card">
  <h3 class="text-lg font-semibold mb-2">Título</h3>
  <p class="text-slate-600">Descrição</p>
</div>

<!-- A classe .card já está em tailwind-input.css -->
```

## 🎯 Checklist de Refatoração

### Phase 1: Base Dashboard (1-2 horas)
- [ ] Adicionar link do Tailwind CSS
- [ ] Remover Bootstrap link
- [ ] Remover `<style>` inline completo
- [ ] Refatorar sidebar com Tailwind
- [ ] Refatorar header com Tailwind
- [ ] Refatorar footer com Tailwind
- [ ] Testar no browser

### Phase 2: Componentes (2-3 horas)
- [ ] Refatorar todos os cards
- [ ] Refatorar todos os botões
- [ ] Refatorar formulários
- [ ] Refatorar tabelas
- [ ] Refatorar modais

### Phase 3: Páginas (3-4 horas)
- [ ] Dashboard
- [ ] Transações
- [ ] Agendamentos
- [ ] Relatórios
- [ ] Configurações

## 📊 Resumo de Classes

| Tailwind | CSS | Uso |
|----------|-----|-----|
| `p-4` | `padding: 1rem` | Espaçamento interno |
| `m-2` | `margin: 0.5rem` | Espaçamento externo |
| `flex` | `display: flex` | Flexbox |
| `grid` | `display: grid` | Grid |
| `fixed` | `position: fixed` | Posicionamento |
| `bg-blue-600` | `background-color: #2563eb` | Cores |
| `text-slate-900` | `color: #0f172a` | Cor de texto |
| `rounded-lg` | `border-radius: 0.5rem` | BorderRadius |
| `shadow-md` | `box-shadow: ...` | Sombra |
| `hover:bg-blue-700` | `&:hover { bg... }` | Estados |
| `transition-colors` | `transition: color 0.3s` | Transições |

## 💡 Dicas Importantes

1. **Use o DevTools**: Inspecione elementos para ver classes aplicadas
2. **Copie padrões**: Se uma coisa funciona, reutilize a classe
3. **Deixe npm watch rodando**: Vê mudanças em tempo real
4. **Testa responsive**: `md:`, `lg:`, `xl:` breakpoints
5. **Reutilize classes compostas**: Crie mixins no CSS customizado

## 🚀 Como Começar AGORA

1. Instale Node.js se não tiver
2. `npm install` na raiz do projeto
3. `npm run watch` em um terminal (deixe rodando)
4. Abra `src/templates/base_dashboard.html`
5. Comece a refatorar!

## 📞 Precisa de Ajuda?

- Tailwind docs: https://tailwindcss.com/docs
- Playground: https://play.tailwindcss.com/
- Componentes prontos: https://headlessui.dev/

---

**Quando terminar**: Faça commit e push no GitHub! 🎉
