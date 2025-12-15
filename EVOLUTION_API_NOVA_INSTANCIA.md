# 🔄 EVOLUTION API - NOVA INSTÂNCIA NO EASYPANEL

## 📋 O que Mudou?

Você excluiu a instância antiga e criou uma **nova** no EasyPanel.

### Credenciais Extraídas:

```
✅ API Key (MANTÉM A MESMA):
   AUTHENTICATION_API_KEY=429683C4C977415CAAFCCE10F7D57E11

⚠️ Novo Banco de Dados:
   DATABASE_CONNECTION_URI=postgres://postgres:58d6a08d5d74539feb24@$(PROJECT_NAME)_evolution-api-db:5432/$(PROJECT_NAME)
   - Usuário: postgres
   - Senha: 58d6a08d5d74539feb24

✅ Cache Redis (NOVO):
   CACHE_REDIS_URI=redis://default:9906d9c3495977ee5fc2@$(PROJECT_NAME)_evolution-api-redis:6379
```

---

## 🔗 Qual é o Novo Domínio?

**Você precisa dizer qual é o domínio do novo Evolution API.**

Deve estar no painel do EasyPanel em:
- **Evolution API** → **Configurações** → **URL**
- Ou em: **Aplicações** → **Evolution API** → **URL de Acesso**

Pode ser algo como:
- `https://evolution-api-novo.seu-dominio.com`
- `https://evo2.seu-dominio.com`
- `https://seu-dominio.com/evolution-api`

---

## 📝 Quando Você Tiver o Domínio

Me envie e vou atualizar o `.env` para:

```bash
EVOLUTION_API_URL=https://<novo-dominio>/message/sendText
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
```

---

## ✅ Checklist Imediato

- [ ] Acessar EasyPanel
- [ ] Encontrar URL do novo Evolution API
- [ ] Enviar para mim
- [ ] Eu atualizo `.env`
- [ ] Testar integração

**Manda o novo domínio!** 🚀
