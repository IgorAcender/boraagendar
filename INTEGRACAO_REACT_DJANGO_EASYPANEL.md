# 🚀 Guia: Integração React com Django para EasyPanel

## O que foi feito

Criamos uma integração onde o **React roda como SPA servido pelo Django**, permitindo:
- ✅ Um único aplicativo no EasyPanel
- ✅ Build automático do React
- ✅ API do Django em `/api`
- ✅ Rotas do React em `/app/*`

---

## 📋 Estrutura Resultante

```
boraagendar/
├── src/
│   ├── config/
│   │   ├── urls.py              (← atualizado com rotas SPA)
│   │   ├── spa.py               (← novo: serve React)
│   │   └── management/
│   │       └── commands/
│   │           └── build_frontend.py  (← novo: build command)
│   │
│   ├── staticfiles/
│   │   └── dist/                (← build do React vai aqui)
│   │
│   └── templates/
│       └── spa.html             (← novo: index HTML para React)
│
├── frontend/
│   ├── dist/                    (← gerado por npm run build)
│   ├── src/
│   ├── package.json
│   ├── vite.config.js           (← atualizado com build config)
│   └── .gitignore
│
└── build_frontend.sh            (← novo: script de build)
```

---

## 🛠️ Como Usar

### Opção 1: Build Automático (Recomendado para EasyPanel)

```bash
# Compilar React e copiar para Django
python src/manage.py build_frontend

# Iniciar servidor
python src/manage.py runserver
```

**O que faz:**
1. ✅ Instala dependências npm
2. ✅ Compila React com Vite
3. ✅ Copia build para `src/staticfiles/dist/`
4. ✅ Django serve automaticamente

---

### Opção 2: Build Manual

```bash
# Compilar React
./build_frontend.sh

# Iniciar servidor
python src/manage.py runserver
```

---

### Opção 3: Desenvolvimento

```bash
# Terminal 1: Django (sem React)
python src/manage.py runserver

# Terminal 2: Vite dev server
cd frontend
npm install
npm run dev  # Roda em http://localhost:3000
```

---

## 🔗 URLs do Aplicativo

| URL | O que faz |
|-----|-----------|
| `http://localhost:8000/` | Dashboard Django antigo |
| `http://localhost:8000/app` | React SPA (novo) |
| `http://localhost:8000/app/financeiro/transacoes` | Transações React |
| `http://localhost:8000/api/*` | Endpoints da API REST |
| `http://localhost:8000/admin` | Django admin |

---

## 📦 EasyPanel: Próximos Passos

Quando você fizer **push para GitHub**:

```bash
git add .
git commit -m "🚀 Integração React + Django com SPA"
git push origin main
```

**EasyPanel vai:**
1. Detectar mudanças
2. Rodando o Dockerfile
3. Executar:
   ```bash
   python src/manage.py build_frontend
   python src/manage.py runserver
   ```
4. Servir em: `http://robo-agendamento-igor.hjcm.easypanel.host/app`

---

## ⚙️ Configuração do Docker (Dockerfile)

Seu Dockerfile precisa ter:

```dockerfile
# Build stage
FROM node:18 AS frontend-builder
WORKDIR /app
COPY frontend /app/frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Django stage
FROM python:3.13
WORKDIR /app
COPY . /app

# Copiar build do React
COPY --from=frontend-builder /app/frontend/dist /app/src/staticfiles/dist

RUN pip install -r requirements.txt
RUN python src/manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]
```

---

## 🚨 Troubleshooting

### "npm: command not found"
- EasyPanel com Node.js - ✅ Deve funcionar
- Localmente sem Node - ❌ Instale: https://nodejs.org

### "StaticFilesNotFound"
- Rode: `python src/manage.py collectstatic --noinput`

### React não carrega em `/app`
1. Verifique se `frontend/dist` foi criado
2. Rode: `python src/manage.py build_frontend`
3. Reinicie o servidor

### API retorna 404
- URLs estão em `/api/*`
- Frontend chama `http://localhost:8000/api/...`
- Em produção: `https://seu-dominio.com/api/...`

---

## 📝 Próximas Etapas

1. **Teste localmente primeiro**
   ```bash
   python src/manage.py build_frontend
   python src/manage.py runserver
   # Acesse: http://localhost:8000/app
   ```

2. **Faça push para GitHub**
   ```bash
   git add .
   git commit -m "Integração React + Django"
   git push origin main
   ```

3. **Espere EasyPanel fazer deploy**
   - Deve aparecer em alguns minutos

4. **Acesse**
   ```
   http://robo-agendamento-igor.hjcm.easypanel.host/app
   ```

---

## 📊 Arquitetura Final

```
┌─────────────────────────────────────────┐
│      Frontend React (SPA)               │
│  /app, /app/financeiro, /app/config     │
└──────────────┬──────────────────────────┘
               │
               ├─→ API Calls: /api/*
               │
┌──────────────▼──────────────────────────┐
│      Django Backend (REST API)          │
│  /api/financial/*, /api/accounts/, etc  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      PostgreSQL Database                │
│      (Multi-tenant com TenantMembership)│
└─────────────────────────────────────────┘
```

---

**Status**: ✅ Pronto para Deploy no EasyPanel!

Qualquer dúvida, me avisa! 🚀
