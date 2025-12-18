# 🎨 Tailwind CSS Setup para BoraAgendar

## Instalação Rápida

### 1. Instalar Node.js (se não tiver)
```bash
# macOS com Homebrew
brew install node

# Ou baixe de: https://nodejs.org/
```

### 2. Instalar dependências Tailwind
```bash
cd /Users/user/Desktop/Programação/boraagendar
npm install
```

### 3. Compilar CSS (primeira vez)
```bash
npm run build
```

Isso vai gerar: `src/static/css/tailwind.css`

### 4. Desenvolvimento (watch mode)
```bash
npm run watch
```

Deixe rodando enquanto desenvolve. O CSS atualiza automaticamente!

## 📁 Estrutura

```
boraagendar/
├── package.json              ← Configuração npm
├── tailwind.config.js        ← Configuração Tailwind
├── postcss.config.js         ← Configuração PostCSS
└── src/
    ├── static/css/
    │   ├── tailwind-input.css    ← Arquivo fonte (não editar muito)
    │   └── tailwind.css          ← ⭐ Arquivo gerado (use no HTML!)
    └── templates/
        ├── base_dashboard.html   ← Usar classes Tailwind aqui
        ├── scheduling/
        └── ...
```

## 🎯 Uso Básico

### Antes (Bootstrap 5 + CSS inline):
```html
<style>
  .sidebar { position: fixed; width: 280px; ... }
  .card { background: white; padding: 24px; ... }
</style>

<div class="sidebar">
  <div class="card">...</div>
</div>
```

### Depois (Tailwind):
```html
<link href="{% static 'css/tailwind.css' %}" rel="stylesheet">

<div class="fixed inset-y-0 left-0 w-64 bg-slate-900">
  <div class="bg-white rounded-lg shadow-md p-6">...</div>
</div>
```

## 📚 Classes Tailwind Comuns

### Spacing
- `p-4` = padding 16px
- `m-2` = margin 8px
- `px-6` = padding horizontal
- `mb-4` = margin-bottom

### Colors
- `bg-blue-600` = background color
- `text-slate-900` = text color
- `border-slate-200` = border color

### Flexbox
- `flex` = display flex
- `flex-col` = flex-direction column
- `items-center` = align-items center
- `justify-between` = justify-content space-between

### Responsive
- `md:w-1/2` = width 50% on medium screens
- `lg:p-8` = padding 32px on large screens

## 🚀 Comandos

```bash
# Build uma vez
npm run build

# Watch (recompila ao salvar)
npm run watch

# O mesmo que watch
npm run dev
```

## 🔗 Links Úteis

- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Tailwind UI Components](https://tailwindui.com/)
- [Ant Design Inspired](https://ant.design/)

## 💡 Dicas

1. **Inspecione o CSS gerado**: `src/static/css/tailwind.css` (é grande, mas otimizado)
2. **Deixe npm watch rodando**: Facilita desenvolvimento
3. **Use o Tailwind docs**: Tem tudo que precisa
4. **Copie padrões de Balasis**: A maioria dos estilos pode virar Tailwind

## 🐛 Troubleshooting

### "tailwindcss: command not found"
```bash
npm install  # Reinstale as dependências
```

### CSS não está aparecendo
```bash
npm run build  # Compile novamente
npx tailwindcss -i src/static/css/tailwind-input.css -o src/static/css/tailwind.css
```

### Classes não reconhecidas
Certifique-se que o arquivo está em `src/static/css/tailwind.css` (não `-input`)

---

**Próximos passos**: Veja `TAILWIND_REFACTOR.md` para começar a refatorar templates!
