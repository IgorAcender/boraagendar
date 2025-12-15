# 🚀 GUIA COMPLETO - ATIVAR WHATSAPP NO BORA AGENDAR

## 📋 Status Atual

✅ **O que já está pronto:**
- Integração com Evolution API implementada
- Banco de dados com campo `whatsapp_number` 
- Formulários e templates configurados
- Script de teste criado

⚙️ **O que falta:**
- Configurar a URL correta do Evolution API no `.env`
- Testar envio de mensagens
- Configurar número de WhatsApp por tenant

---

## 🔧 PASSO 1: Configurar o `.env` com Domínio Correto

Edite o arquivo `.env` na raiz do projeto:

```bash
nano .env
```

Procure por esta linha:

```
EVOLUTION_API_URL=https://seu-dominio-easypanel.com/message/sendText
```

E substitua `seu-dominio-easypanel.com` pelo **domínio real do seu EasyPanel**.

**Exemplo:**
```
EVOLUTION_API_URL=https://evolution.seudominio.com/message/sendText
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
```

---

## 🔑 PASSO 2: Configurar Número de WhatsApp no Admin

1. Vá para: `http://localhost:8000/admin/`
2. Clique em **Tenants** → Seu Tenant
3. Procure pelo campo **WhatsApp Number**
4. Preencha com seu número no formato internacional:
   - **Exemplo Brasil:** `5511987654321`
   - **Formato:** País (55) + Área (11) + Número (987654321)

5. Clique em **Salvar**

---

## 🧪 PASSO 3: Testar o Envio

Existem 3 formas de testar:

### Opção A: Script de Teste (Recomendado)

```bash
cd /Users/user/Desktop/Programação/boraagendar
python test_whatsapp.py
```

O script vai:
- ✅ Verificar se as credenciais estão configuradas
- ✅ Buscar um tenant no banco
- ✅ Pedir um número para teste
- ✅ Enviar uma mensagem

### Opção B: Django Shell

```bash
cd src
python manage.py shell
```

```python
from notifications.services import EvolutionApiClient, WhatsappMessage
from scheduling.models import Tenant

tenant = Tenant.objects.first()
client = EvolutionApiClient()

message = WhatsappMessage(
    tenant_slug=tenant.slug,
    to_number="5511987654321",  # Altere para seu número
    message="Teste de WhatsApp - Bora Agendar"
)

resultado = client.send_message(message)
print(f"Enviado: {resultado}")
```

### Opção C: Através de um Agendamento

1. Vá para `http://localhost:8000/admin/`
2. Crie um novo agendamento (Scheduling → Bookings)
3. Preencha:
   - Serviço
   - Profissional
   - Cliente e Telefone
   - Data/Hora
4. Salve
5. A confirmação será enviada via WhatsApp automaticamente

---

## 🔍 Verificar Logs

Se a mensagem não chegar:

### 1. Django Logs (Local)
```bash
cd src
python manage.py runserver
# Veja se há erros sobre Evolution API
```

### 2. EasyPanel Logs
No painel do EasyPanel → Evolution API → Logs
- Procure por erros de conexão
- Verifique se a instância está online

### 3. Verificar Credenciais
```bash
# Confirme que a API Key está correta
# Ela deve ser: 429683C4C977415CAAFCCE10F7D57E11
```

---

## 🐛 Troubleshooting

### ❌ "Evolution API credentials missing"
**Solução:** Verificar se `.env` tem:
```
EVOLUTION_API_URL=...
EVOLUTION_API_KEY=...
```

### ❌ "Failed to send WhatsApp message"
**Solução:** 
- Confirme que a URL está correta
- Verifique se a instância está conectada no Evolution API
- Teste a conexão: `curl https://seu-dominio/message/sendText`

### ❌ "Invalid phone number"
**Solução:**
- Use formato internacional completo (55 + área + número)
- Sem parênteses ou hífens
- Exemplo: `5511987654321` (não `(11) 98765-4321`)

### ❌ "Instance not found"
**Solução:**
- No EasyPanel, conecte uma instância de WhatsApp
- Vá em: Evolution API → Instances → Create New
- Escaneie o QR Code com seu WhatsApp

---

## 📊 Configurações Avançadas

### Personalizar Mensagem de Confirmação

Edite: `src/scheduling/services/notification_dispatcher.py`

```python
def send_booking_confirmation(booking) -> bool:
    # Customize a mensagem aqui
    message = (
        f"Olá {booking.customer_name},\n"
        f"Agendamento confirmado!\n"
        f"Serviço: {booking.service.name}\n"
        f"Data: {booking.scheduled_for:%d/%m/%Y %H:%M}\n"
        f"Profissional: {booking.professional.display_name}"
    )
    # ...
```

### Enviar Outras Mensagens

Use em qualquer lugar:

```python
from notifications.services import EvolutionApiClient, WhatsappMessage

client = EvolutionApiClient()
message = WhatsappMessage(
    tenant_slug="seu-tenant",
    to_number="5511987654321",
    message="Sua mensagem aqui"
)
client.send_message(message)
```

---

## ✅ Checklist Final

- [ ] `.env` configurado com URL correta
- [ ] API Key verificada: `429683C4C977415CAAFCCE10F7D57E11`
- [ ] Número de WhatsApp configurado no admin
- [ ] Instância conectada no EasyPanel
- [ ] Script de teste executado com sucesso
- [ ] Mensagem recebida no WhatsApp

---

## 📞 Suporte

Se continuar com problemas:
1. Verifique o console do Django
2. Verifique os logs do EasyPanel
3. Confirme a conectividade de rede
4. Teste manualmente a URL no navegador

**Bora Agendar** - Agendamentos inteligentes com WhatsApp! 🚀
