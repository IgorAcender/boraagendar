# 🚀 INTEGRAÇÃO WHATSAPP - PRODUÇÃO

## 📊 Configuração Atual

### Django App (Seu Sistema)
- **Domínio:** `robo-de-agendamento-igor.ivhjcm.easypanel.host`
- **Banco:** PostgreSQL (agendamento)
- **Status:** ✅ Configurado

### Evolution API (WhatsApp)
- **Domínio:** `robo-de-agendamento-igor.ivhjcm.easypanel.host`
- **Banco:** PostgreSQL (separado, conforme recomendado)
- **Status:** ⚠️ Aguardando API Key

---

## 🔧 Próximas Etapas

### 1️⃣ Obter API Key da Evolution API

No **EasyPanel Dashboard**, vá para:
1. Evolution API
2. Configurações/Settings
3. Procure por: **API Key** ou **Authentication Token**
4. Copie o valor (algo como: `abc123def456...`)

**Ou**, se você tiver acesso ao container Evolution API:
```bash
# Dentro do container
echo $AUTHENTICATION_API_KEY
# Deve retornar algo como: 429683C4C977415CAAFCCE10F7D57E11
```

### 2️⃣ Atualizar .env

Após obter a chave, edite `.env`:

```
EVOLUTION_API_URL=https://robo-de-agendamento-igor.ivhjcm.easypanel.host/message/sendText
EVOLUTION_API_KEY=<sua-chave-aqui>
```

### 3️⃣ Criar Instância de WhatsApp

No painel da Evolution API:
1. Vá em: **Instances** → **Create Instance**
2. Escaneie o QR Code com seu WhatsApp
3. Aguarde conectar (pode levar 30 segundos)
4. Agora está pronta para enviar mensagens!

### 4️⃣ Testar

```bash
# Local (para desenvolvimento)
python test_whatsapp.py

# Ou criar um agendamento no admin
# http://robo-de-agendamento-igor.ivhjcm.easypanel.host/admin/
# → Scheduling → Bookings → Add Booking
# → A mensagem será enviada automaticamente!
```

---

## 📝 Checklist

- [ ] API Key obtida do EasyPanel
- [ ] `.env` atualizado com EVOLUTION_API_KEY
- [ ] Instância de WhatsApp criada e conectada
- [ ] Número de WhatsApp configurado no tenant (admin → Tenants)
- [ ] Teste de agendamento realizado
- [ ] Mensagem recebida no WhatsApp ✅

---

## 🎯 URLs de Referência

| Item | URL |
|------|-----|
| Django Admin | https://robo-de-agendamento-igor.ivhjcm.easypanel.host/admin/ |
| Mini-site | https://robo-de-agendamento-igor.ivhjcm.easypanel.host/ |
| Evolution API Panel | https://robo-de-agendamento-igor.ivhjcm.easypanel.host/api/docs |
| API para Enviar MSG | https://robo-de-agendamento-igor.ivhjcm.easypanel.host/message/sendText |

---

## 🔍 Se Não Funcionar

### Erro: "Evolution API credentials missing"
- Verifique se `.env` tem `EVOLUTION_API_KEY` preenchida

### Erro: "Invalid API Key"
- Confirme a chave no EasyPanel
- Tente copiar novamente (pode ter caracteres invisíveis)

### Erro: "Instance not found"
- Você criou uma instância no Evolution API?
- A instância está conectada (status: online)?

### Erro: "Invalid phone number"
- Use formato: `55` + `11` + `987654321` (sem parênteses)
- Não use `(11) 98765-4321`

---

## 📞 Próximas Otimizações

Depois que WhatsApp estiver funcionando, podemos:
- ✅ Enviar lembretes antes do agendamento
- ✅ Permitir cancelamento via WhatsApp
- ✅ Enviar comprovante de pagamento
- ✅ Notificações customizadas por tenant

**Bora Agendar** - Agendamentos inteligentes! 🚀
