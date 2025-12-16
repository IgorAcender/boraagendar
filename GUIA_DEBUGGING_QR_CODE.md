# 🔍 GUIA DE DEBUGGING - QR Code Não Aparece

## ✅ O que já está correto:

1. ✅ Lógica SaaS implementada (1 salão = 1 instância)
2. ✅ Evolution API respondendo (testado)
3. ✅ URL correta (sem /manager)
4. ✅ JavaScript com logs no console

---

## 🔍 Como Debugar (Passo a Passo):

### 1. Abrir DevTools
```
Pressione F12 no navegador
Ou: Botão direito → Inspecionar
```

### 2. Ir na aba Console
```
DevTools → Console
```

### 3. Clicar "Conectar WhatsApp"
```
Clicar no botão azul "➕ Conectar WhatsApp"
```

### 4. Verificar os logs que aparecem:

#### ✅ Logs esperados (SUCESSO):
```javascript
Iniciando createNewWhatsApp...
URL de criação: /api/whatsapp/connect/
Response status: 200
Response headers: {content-type: "application/json"}
Response data: {
  success: true,
  qr_code: "data:image/png;base64,iVBORw0...",
  whatsapp_id: 1,
  message: "Escaneie o QR code...",
  instance_name: "vintge_whatsapp"
}
```
→ **QR code deve aparecer!**

#### ❌ Possíveis erros:

**Erro 1: Status 500**
```javascript
Response status: 500
HTTP 500: Internal Server Error
```
**Causa:** Erro no servidor (Python)
**Solução:** Ver logs do Django/Easypanel

**Erro 2: Status 404**
```javascript
Response status: 404
HTTP 404: Not Found
```
**Causa:** URL do endpoint errada
**Solução:** Verificar URLs (whatsapp.py)

**Erro 3: Response sem qr_code**
```javascript
Response data: {
  success: false,
  error: "Evolution API não retornou QR code"
}
```
**Causa:** Evolution API não retornou base64
**Solução:** Ver logs do Django, verificar Evolution API

**Erro 4: CSRF Token**
```javascript
Forbidden (CSRF token missing or incorrect)
```
**Causa:** Token CSRF inválido
**Solução:** Recarregar página (Ctrl+F5)

**Erro 5: Não é JSON**
```javascript
Response não é JSON: <!DOCTYPE html>...
```
**Causa:** Django retornou HTML em vez de JSON
**Solução:** Ver logs do Django

---

## 🖥️ Logs do Servidor (Django/Easypanel)

### O que procurar nos logs:

#### ✅ Logs esperados (PRIMEIRA VEZ):
```
🆕 Criando PRIMEIRA instância para Vintge: vintge_whatsapp
🔗 [1/2] POST http://robo-de-agendamento-evolution-api.ivhjcm.easypanel.host/instance/create
📊 Status criação: 201
✅ Instância criada/encontrada: vintge_whatsapp
🔗 [2/2] GET http://robo-de-agendamento-evolution-api.ivhjcm.easypanel.host/instance/connect/vintge_whatsapp
✅ Registro criado no banco para Vintge
```

#### ✅ Logs esperados (RECONEXÃO):
```
♻️  Reconectando instância existente: vintge_whatsapp
🔗 GET http://robo-de-agendamento-evolution-api.ivhjcm.easypanel.host/instance/connect/vintge_whatsapp
✅ QR code atualizado para instância vintge_whatsapp
```

#### ❌ Possíveis erros:

**Erro 1: Evolution API não configurada**
```
❌ Erro geral em whatsapp_create: ...
Evolution API não configurada
```
**Solução:** Verificar variáveis EVOLUTION_API_URL e EVOLUTION_API_KEY

**Erro 2: Timeout Evolution API**
```
❌ Erro ao obter QR code: HTTPConnectionPool...
```
**Solução:** Evolution API não acessível

**Erro 3: Sem base64**
```
⚠️  Resposta sem base64. Keys: ['pairingCode', 'code']
```
**Solução:** Evolution API não retornou campo 'base64'

---

## 🧪 Testes Manuais

### Teste 1: Verificar Evolution API está UP
```bash
curl http://robo-de-agendamento-evolution-api.ivhjcm.easypanel.host/health
```

### Teste 2: Criar instância de teste
```bash
curl -X POST \
  http://robo-de-agendamento-evolution-api.ivhjcm.easypanel.host/instance/create \
  -H "apikey: 429683C4C977415CAAFCCE10F7D57E11" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "teste_manual_debug",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

### Teste 3: Obter QR code
```bash
curl -X GET \
  http://robo-de-agendamento-evolution-api.ivhjcm.easypanel.host/instance/connect/teste_manual_debug \
  -H "apikey: 429683C4C977415CAAFCCE10F7D57E11"
```

Deve retornar:
```json
{
  "base64": "data:image/png;base64,iVBORw0KGgo...",
  "code": "AB12-CD34",
  "pairingCode": "AB12-CD34"
}
```

---

## 📋 Checklist de Debugging

### No Navegador (DevTools):
- [ ] F12 aberto
- [ ] Aba Console selecionada
- [ ] Clicar "Conectar WhatsApp"
- [ ] Ver log "Iniciando createNewWhatsApp..."
- [ ] Ver "Response status: 200"
- [ ] Ver "Response data:" com qr_code

### No Servidor:
- [ ] Ver logs do Django/Easypanel
- [ ] Procurar por "🆕 Criando" ou "♻️  Reconectando"
- [ ] Ver "✅ QR code atualizado" ou "✅ Registro criado"
- [ ] Nenhum erro "❌"

### Variáveis de Ambiente:
- [ ] EVOLUTION_API_URL está correta (sem /manager)
- [ ] EVOLUTION_API_KEY está correta
- [ ] Reiniciou o app após mudar variáveis

### Evolution API:
- [ ] Evolution API está rodando
- [ ] Acessível na URL configurada
- [ ] API Key válida

---

## 🚨 Problema Comum: QR Code não aparece no modal

### Sintoma:
Modal abre, mas QR code não aparece (espaço em branco)

### Causas possíveis:

1. **JavaScript não recebe qr_code**
   - Verificar console: `data.qr_code` está undefined?
   - Ver resposta da API no console

2. **QR code sem prefixo**
   - QR deve ser: `data:image/png;base64,iVBORw0...`
   - Verificar no console se tem o prefixo

3. **Erro no backend silencioso**
   - Ver logs do Django
   - Procurar por exceptions

4. **CSRF Token**
   - Recarregar página (Ctrl+F5)
   - Testar novamente

---

## 📞 Próximo Passo

**Me envie os logs que aparecem no Console (F12) quando você clicar em "Conectar WhatsApp"!**

Exemplo do que preciso ver:
```
Iniciando createNewWhatsApp...
URL de criação: /api/whatsapp/connect/
Response status: ???
Response data: ???
```

Com essas informações, posso identificar exatamente onde está o problema! 🔍
