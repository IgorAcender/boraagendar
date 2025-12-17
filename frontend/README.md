# BoraAgendar Frontend

Frontend React + Ant Design estilo Balasis para o BoraAgendar.

## 🚀 Começar

### Pré-requisitos
- Node.js 16+ 
- npm ou yarn

### Instalação

```bash
cd frontend
npm install
```

### Desenvolvimento

```bash
npm run dev
```

Acesse `http://localhost:3000`

### Build Produção

```bash
npm run build
```

## 📁 Estrutura

```
src/
├── components/
│   ├── AppLayout.jsx      (Layout principal)
│   └── Sidebar.css
├── pages/
│   ├── Dashboard.jsx      (Dashboard com gráficos)
│   └── Transactions.jsx   (Gerenciador de transações)
├── services/
│   └── api.js            (Cliente HTTP com axios)
├── App.jsx               (Roteamento)
├── main.jsx              (Entry point)
├── App.css
└── index.css
```

## 🎨 Design

- **UI Framework**: Ant Design 5.x
- **Idioma**: Português Brasileiro
- **Responsivo**: Mobile, tablet, desktop
- **Ícones**: Ant Design Icons

## 📡 API

O frontend consome a API Django em `http://localhost:8000/api/`

### Endpoints suportados:
- `/financial/accounts/` - Contas
- `/financial/transactions/` - Transações
- `/financial/commissions/` - Comissões
- `/bookings/` - Agendamentos
- `/services/` - Serviços
- `/professionals/` - Profissionais

## 🔐 Autenticação

Token JWT é armazenado em `localStorage` e enviado em cada requisição.

```js
Authorization: Bearer <token>
```

## 🚢 Deploy

### Vercel

```bash
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "preview"]
```

## 📝 Próximos passos

- [ ] Páginas de agendamentos
- [ ] Página de relatórios
- [ ] Autenticação JWT
- [ ] Testes E2E
- [ ] PWA support
- [ ] Dark mode

## 📄 Licença

MIT
