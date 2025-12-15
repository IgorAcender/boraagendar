# 🔧 INTEGRAÇÃO DO DASHBOARD DE WHATSAPP

## ✅ O que já foi criado

1. **Models** (`scheduling/models.py`)
   - Extended `WhatsAppInstance` com campos de gerenciamento
   - 8 campos novos + 3 métodos helper

2. **Migration** (`scheduling/migrations/0011_*.py`)
   - Pronta para aplicar (gerada com makemigrations)
   - Adiciona 8 colunas ao banco

3. **Views** (`scheduling/views/whatsapp_manager.py`)
   - 8 endpoints completos
   - QR code generation
   - Webhook para Evolution API
   - JSON APIs para real-time

4. **URLs** (`scheduling/urls/whatsapp.py`)
   - 8 rotas prontas
   - Namespace 'whatsapp' configurado

5. **Templates**
   - `scheduling/templates/whatsapp/dashboard.html` (dashboard principal)
   - `scheduling/templates/whatsapp/detail.html` (detalhes do WhatsApp)

---

## 🔌 PRÓXIMOS PASSOS (Integração)

### PASSO 1: Atualizar URLs Principais ✅ CRÍTICO

**Arquivo:** `src/config/urls.py` (ou main urls.py)

Adicionar a inclusão do whatsapp.urls:

```python
# Em cima, com outros imports
from scheduling.urls import whatsapp as whatsapp_urls

# Em urlpatterns, adicionar:
urlpatterns = [
    # ... outras rotas ...
    path('whatsapp/', include(whatsapp_urls)),  # ← NOVO
    # ... resto das rotas ...
]
```

### PASSO 2: Aplicar Migration ✅ CRÍTICO

**Em seu ambiente EasyPanel, no terminal:**

```bash
# Conectar ao container do Django
docker exec -it [seu_container_django] bash

# Aplicar migrations
python manage.py migrate

# Verificar que funcionou
python manage.py showmigrations scheduling
```

**Esperado:** Deve listar a migration 0011 como aplicada ✅

### PASSO 3: Coletar Estáticos (Opcional)

Se usar arquivos estáticos (CSS/JS separados):

```bash
docker exec -it [seu_container_django] bash
python manage.py collectstatic --noinput
```

### PASSO 4: Reiniciar Servidor

```bash
docker restart [seu_container_django]
```

### PASSO 5: Testar Acesso

```
Abra no navegador:
https://seu-dominio.com/whatsapp/

Você deve ver:
- Página de dashboard
- Cards de WhatsApps (vazio se nenhum criado)
- Botões para ações
```

---

## 🧪 TESTE RÁPIDO (Local Development)

Se quiser testar localmente antes de EasyPanel:

```bash
# Na sua máquina local
cd src/

# Aplicar migration localmente
python manage.py migrate

# Criar um WhatsApp de teste
python manage.py shell
```

```python
from scheduling.models import WhatsAppInstance
from tenants.models import Tenant

# Pegar um tenant existente
tenant = Tenant.objects.first()

# Criar WhatsApp de teste
whatsapp = WhatsAppInstance.objects.create(
    tenant=tenant,
    phone_number="+5511999999999",
    status="pending",
    is_primary=True
)

print(f"Created: {whatsapp.id} - {whatsapp.phone_number}")
```

```bash
# Sair do shell (exit())

# Rodar servidor
python manage.py runserver

# Abrir: http://localhost:8000/whatsapp/
```

---

## 📡 INTEGRAÇÃO COM EVOLUTION API

### Webhooks Já Configurados

Quando Evolution API manda atualizações:

```
POST https://seu-dominio.com/whatsapp/webhook/update/
```

Com payload:
```json
{
    "instance": "instance_name",
    "status": "connected",  // ou "disconnected", "error"
    "session_id": "SESSION123",
    "error_message": null
}
```

**O que o sistema faz:**
1. Recebe POST
2. Valida X-API-Key
3. Atualiza status do WhatsApp
4. Atualiza timestamps
5. Gera eventos (se implementado)

### Configurar Evolution API para enviar webhooks

Em suas configurações da Evolution API:

```
Webhook URL: https://seu-dominio.com/whatsapp/webhook/update/
Headers:
  X-API-Key: sua_api_key_secreta
```

---

## 🔑 CONFIGURAÇÕES IMPORTANTES

### settings.py

Adicionar a api_key para validação:

```python
# Em config/settings.py (ou .env)
WHATSAPP_WEBHOOK_API_KEY = "sua_chave_secreta_aqui"
```

No código (whatsapp_manager.py), a validação é:

```python
api_key = request.headers.get('X-API-Key')
if api_key != settings.WHATSAPP_WEBHOOK_API_KEY:
    return JsonResponse({'error': 'Unauthorized'}, status=401)
```

### Garantir que a chave está no .env

```bash
# .env na raiz do projeto
WHATSAPP_WEBHOOK_API_KEY=sua_chave_super_secreta_123456
```

---

## 🎨 PERSONALIZAÇÃO DE TEMPLATES

### Se precisar customizar o dashboard:

**Arquivo:** `scheduling/templates/whatsapp/dashboard.html`

Pontos principais:

```html
<!-- Stats Grid (linhas 20-50) -->
<!-- Customizar cores em .stats-card -->

<!-- WhatsApp Cards (linhas 60-150) -->
<!-- Customizar layout da grid em .whatsapp-grid -->

<!-- Modal de QR Code (linhas 200-230) -->
<!-- Customizar tamanho/estilo em .qr-modal -->

<!-- JavaScript (linhas 250+) -->
<!-- Atualizar endpoints se mudarem as URLs -->
```

---

## ⚙️ TROUBLESHOOTING DE INTEGRAÇÃO

### Erro: "whatsapp URLs not found"

```
❌ Significa: URLs não estão incluídas em config/urls.py
✅ Solução: Adicionar path() conforme PASSO 1
```

### Erro: "Model has no attribute 'tenant'"

```
❌ Significa: Migration 0011 não foi aplicada
✅ Solução: Rodar migrate conforme PASSO 2
```

### Erro: "No module named 'qrcode'"

```
❌ Significa: Biblioteca qrcode não está instalada
✅ Solução: pip install qrcode[pil]
```

### Dashboard vazio (sem WhatsApps)

```
✅ Normal! Significa que:
   1. Nenhum WhatsApp foi criado ainda
   2. Você verá cards vazios
   3. Clique em "+ Conectar" para adicionar
```

### Botões não funcionam

```
Verificar:
1. Console do navegador (F12 → Console)
2. Se houver erro de CSRF:
   - Garantir {% csrf_token %} no formulário ✅ (já está)
3. Se houver erro de URL:
   - Garantir que URLs estão incluídas ✅ (PASSO 1)
4. Se houver erro de permissão:
   - Garantir que usuário está logado
```

---

## 📊 DIAGRAMA DE FLUXO

```
┌─────────────────────────────────────────────────────┐
│ Dono acessa: /whatsapp/                             │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ whatsapp_dashboard() view                           │
│ - Pega WhatsApps do tenant (multi-tenant)          │
│ - Calcula estatísticas                             │
│ - Renderiza dashboard.html                         │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ dashboard.html renderizado com cards               │
│ - Mostra status de cada WhatsApp                   │
│ - JavaScript pronto para ações                     │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ Dono clica em "Gerar QR Code"                       │
│ JavaScript faz POST em /whatsapp/{id}/gerar-qrcode/│
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ whatsapp_generate_qrcode() view                     │
│ - Gera QR usando qrcode library                    │
│ - Salva em Base64 no database                      │
│ - Retorna JSON com imagem                          │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ JavaScript recebe QR, mostra em modal               │
│ Dono aponta câmera para conectar                   │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ WhatsApp se conecta via Evolution API              │
│ Evolution API POST em /whatsapp/webhook/update/    │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ whatsapp_webhook_update() recebe status            │
│ - Atualiza WhatsAppInstance.status                 │
│ - Atualiza connected_at timestamp                  │
│ - Salva session_id                                 │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ Frontend polling detecta mudança                    │
│ Dashboard atualiza status para "✅ Conectado"      │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 FLUXO DE AGENDAMENTO (Integrado)

```
1. Cliente faz agendamento no site
   ↓
2. Sistema procura WhatsAppInstance.is_primary = True
   ↓
3. Se found:
   - Gera mensagem de confirmação
   - Envia via Evolution API para phone_number
   - Cliente recebe confirmação no WhatsApp ✅
   ↓
4. Se not found:
   - Log de erro
   - Email de fallback (se configurado)
```

---

## 📝 CHECKLIST DE VERIFICAÇÃO

- [ ] Passo 1: URLs incluídas em config/urls.py
- [ ] Passo 2: Migration 0011 aplicada (migrate)
- [ ] Passo 3: Servidor reiniciado
- [ ] Passo 4: Dashboard acessível em /whatsapp/
- [ ] Passo 5: QR code gerado com sucesso
- [ ] Passo 6: Evolution API webhooks configurados
- [ ] Passo 7: WhatsApp se conecta após QR
- [ ] Passo 8: Status atualiza automaticamente
- [ ] Passo 9: Agendamento envia mensagem no WhatsApp
- [ ] Passo 10: Teste com cliente real ✅

---

## 🎉 PRONTO!

Sua integração está completa! 

O dono da barbearia pode agora:
- ✅ Acessar /whatsapp/ do seu login
- ✅ Gerar QR codes
- ✅ Conectar WhatsApps
- ✅ Gerenciar múltiplos WhatsApps
- ✅ Ver status em tempo real
- ✅ Receber confirmações de agendamentos automaticamente

---

## 📞 SUPORTE

Se algo não funcionar:

1. Verifique o checklist acima
2. Veja logs em EasyPanel
3. Verifique console do navegador (F12)
4. Teste manualmente as APIs em `/whatsapp/list/api/`

Sucesso! 🚀
