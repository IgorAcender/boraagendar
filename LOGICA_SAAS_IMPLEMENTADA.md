# ✅ LÓGICA SAAS MULTI-TENANT IMPLEMENTADA

## 🎯 Como Funciona Agora

### Regra de Negócio:
- **1 Salão = 1 Instância Evolution API**
- **Instância criada apenas na PRIMEIRA vez**
- **Reconexões usam a MESMA instância**

---

## 🔄 Fluxo de Uso

### 📱 PRIMEIRA VEZ (Botão "Conectar WhatsApp"):

```
1. User clica "Conectar WhatsApp"
   ↓
2. Sistema verifica: Existe WhatsAppInstance para este tenant?
   └─ NÃO EXISTE
   ↓
3. Cria instância na Evolution API
   POST /instance/create
   {
     "instanceName": "salao_barbearia_whatsapp",  # baseado no slug do tenant
     "qrcode": true,
     "integration": "WHATSAPP-BAILEYS"
   }
   ↓
4. Obtém QR code
   GET /instance/connect/salao_barbearia_whatsapp
   ↓
5. Salva no banco:
   - instance_name: "salao_barbearia_whatsapp"
   - tenant: salão atual
   - qr_code: base64
   - connection_status: 'connecting'
   ↓
6. Exibe QR code para o usuário
   ↓
7. User escaneia com WhatsApp
   ↓
8. ✅ Conectado! (webhook atualiza status)
```

### 🔄 RECONEXÃO (Mesma instância, novo QR):

```
1. User clica "Reconectar WhatsApp" (ou "Conectar" novamente)
   ↓
2. Sistema verifica: Existe WhatsAppInstance para este tenant?
   └─ JÁ EXISTE! (instance_name já salvo)
   ↓
3. Não cria nova instância!
   ↓
4. Obtém NOVO QR code da instância EXISTENTE
   GET /instance/connect/salao_barbearia_whatsapp
   ↓
5. Atualiza QR code no banco (mesma instância)
   ↓
6. Exibe novo QR code
   ↓
7. User escaneia
   ↓
8. ✅ Reconectado!
```

---

## 💻 Código Implementado

### View `whatsapp_create`:

```python
# Verifica se já existe instância
existing_whatsapp = WhatsAppInstance.objects.filter(tenant=tenant).first()

if existing_whatsapp:
    # ♻️ RECONEXÃO - usa instância existente
    instance_name = existing_whatsapp.instance_name
    # Obtém novo QR da mesma instância
    # ...
    
else:
    # 🆕 PRIMEIRA VEZ - cria nova instância
    instance_name = f"{tenant.slug}_whatsapp"
    # POST /instance/create
    # GET /instance/connect
    # Cria WhatsAppInstance no banco
    # ...
```

---

## 🗂️ Modelo de Dados

### WhatsAppInstance:

```python
{
    "id": 1,
    "tenant": <Tenant: Barbearia do João>,
    "instance_name": "barbearia_do_joao_whatsapp",  # Nome único na Evolution API
    "phone_number": "+5511987654321",  # Preenchido após conectar
    "connection_status": "connected",  # pending, connecting, connected, disconnected
    "is_primary": true,
    "qr_code": "iVBORw0KGgo...",  # Base64 do último QR
    "qr_code_expires_at": "2025-12-16T15:30:00Z",
    "created_at": "2025-12-16T10:00:00Z"
}
```

---

## 🎨 Interface (Dashboard)

### Estado 1: Nenhum WhatsApp Conectado
```
╔══════════════════════════════════════╗
║  📱 Gerenciar WhatsApp               ║
╠══════════════════════════════════════╣
║                                      ║
║  Nenhum WhatsApp conectado           ║
║                                      ║
║  [➕ Conectar WhatsApp]              ║
║                                      ║
╚══════════════════════════════════════╝
```

### Estado 2: WhatsApp Conectado
```
╔══════════════════════════════════════╗
║  📱 Gerenciar WhatsApp               ║
╠══════════════════════════════════════╣
║                                      ║
║  ✅ WhatsApp Conectado               ║
║  📱 +55 11 98765-4321                ║
║  🟢 Online                           ║
║                                      ║
║  [📋 Ver Status]  [🔄 Reconectar]   ║
║                                      ║
╚══════════════════════════════════════╝
```

### Estado 3: WhatsApp Desconectado
```
╔══════════════════════════════════════╗
║  📱 Gerenciar WhatsApp               ║
╠══════════════════════════════════════╣
║                                      ║
║  ⚠️  WhatsApp Desconectado           ║
║  📱 +55 11 98765-4321                ║
║  🔴 Offline                          ║
║                                      ║
║  [🔄 Reconectar]                     ║
║                                      ║
╚══════════════════════════════════════╝
```

---

## 🔐 Segurança Multi-Tenant

### Isolamento:
- Cada tenant só vê/acessa suas próprias instâncias
- `instance_name` usa `tenant.slug` (único)
- Queries filtradas por `tenant=request.user.tenant`

### Nome da Instância:
```python
instance_name = f"{tenant.slug}_whatsapp"

# Exemplos:
# Tenant: "Barbearia do João" (slug: barbearia-do-joao)
# → instance_name: "barbearia-do-joao_whatsapp"

# Tenant: "Salão Beleza Pura" (slug: salao-beleza-pura)
# → instance_name: "salao-beleza-pura_whatsapp"
```

---

## ✅ Vantagens desta Abordagem

1. **Simples**: 1 salão = 1 instância
2. **Eficiente**: Não cria instâncias desnecessárias
3. **Escalável**: Suporta milhares de salões
4. **Claro**: Instance name identifica o salão
5. **Reconexão fácil**: Mesmo instance_name, novo QR

---

## 🧪 Testando

### Teste 1: Primeira Conexão
```bash
curl -X POST http://localhost:8000/api/whatsapp/connect/ \
  -H "Cookie: sessionid=..." \
  -H "Content-Type: application/json"

# Esperado:
# ✅ Cria instância "tenant_slug_whatsapp"
# ✅ Retorna QR code
# ✅ Cria WhatsAppInstance no banco
```

### Teste 2: Reconexão
```bash
# Mesmo endpoint!
curl -X POST http://localhost:8000/api/whatsapp/connect/ \
  -H "Cookie: sessionid=..." \
  -H "Content-Type: application/json"

# Esperado:
# ✅ NÃO cria nova instância
# ✅ Usa instance_name existente
# ✅ Retorna novo QR code
# ✅ Atualiza QR no banco
```

---

## 📊 Monitoramento

### Logs no Console:

**Primeira vez:**
```
🆕 Criando PRIMEIRA instância para Barbearia do João: barbearia-do-joao_whatsapp
🔗 [1/2] POST http://.../instance/create
📊 Status criação: 201
✅ Instância criada/encontrada: barbearia-do-joao_whatsapp
🔗 [2/2] GET http://.../instance/connect/barbearia-do-joao_whatsapp
✅ Registro criado no banco para Barbearia do João
```

**Reconexão:**
```
♻️  Reconectando instância existente: barbearia-do-joao_whatsapp
🔗 GET http://.../instance/connect/barbearia-do-joao_whatsapp
✅ QR code atualizado para instância barbearia-do-joao_whatsapp
```

---

## 🚀 Deploy

1. **Fazer commit:**
```bash
git add .
git commit -m "Implementa lógica SaaS: 1 salão = 1 instância Evolution API"
git push origin main
```

2. **Atualizar .env no Easypanel:**
```
EVOLUTION_API_URL=http://robo-de-agendamento-evolution-api.ivhjcm.easypanel.host
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
```
⚠️ **SEM** `/manager` no final!

3. **Aplicar migration:**
```bash
python src/manage.py migrate scheduling
```

4. **Testar:**
- Acesse dashboard
- Clique "Conectar WhatsApp"
- QR code deve aparecer
- Escaneie e conecte
- Teste reconexão

---

**Status:** ✅ Lógica SaaS implementada!
**Pronto para:** Deploy e testes em produção
