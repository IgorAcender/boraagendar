# 🚀 QUICK START - DASHBOARD WHATSAPP (5 MINUTOS)

## O que você vai fazer em 5 minutos

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ PASSO 1 (1 min) │→  │ PASSO 2 (2 min) │→  │ PASSO 3 (2 min) │
│ Editar URLs     │   │ Aplicar DB      │   │ Testar Acesso   │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

---

## 🔧 PASSO 1: Editar config/urls.py (1 minuto)

**Arquivo:** `src/config/urls.py`

**Procure:**
```python
from django.contrib import admin
from django.urls import path
```

**Logo após admin import, ADICIONE:**
```python
from scheduling.urls import whatsapp as whatsapp_urls
```

**Procure em urlpatterns:**
```python
urlpatterns = [
    path('admin/', admin.site.urls),
```

**ANTES de admin, ADICIONE:**
```python
    path('whatsapp/', include(whatsapp_urls)),
```

**Resultado esperado:**
```python
from django.contrib import admin
from django.urls import path, include
from scheduling.urls import whatsapp as whatsapp_urls

urlpatterns = [
    path('whatsapp/', include(whatsapp_urls)),      # ← NOVO
    path('admin/', admin.site.urls),
    # ... resto das rotas
]
```

✅ **PRONTO! Salve o arquivo.**

---

## 💾 PASSO 2: Aplicar Migration (2 minutos)

**No seu computador/EasyPanel:**

### Se em EasyPanel:

```bash
# 1. Entrar no container
docker exec -it seu_container_django bash

# 2. Aplicar migration
python manage.py migrate

# 3. Verificar se funcionou
python manage.py showmigrations scheduling | grep 0011

# Resultado esperado:
# [x] 0011_whatsappinstance_connected_at
```

### Se local (desenvolvimento):

```bash
cd src/

# 1. Aplicar
python manage.py migrate

# 2. Verificar
python manage.py showmigrations scheduling | grep 0011
```

✅ **PRONTO! Database atualizado.**

---

## 🌐 PASSO 3: Testar Acesso (2 minutos)

### 1. Reiniciar servidor

**Em EasyPanel:**
```bash
docker restart seu_container_django
```

**Local:**
```bash
# Ctrl+C para parar (se tiver rodando)
python manage.py runserver
```

### 2. Abrir no navegador

```
https://seu-dominio.com/whatsapp/
```

**Você deve ver:**
```
┌─────────────────────────────────────────┐
│ 📱 Gerenciar WhatsApps                  │
├─────────────────────────────────────────┤
│ ┌────┐ ┌────────┐ ┌──────┐ ┌────────┐  │
│ │Tot │ │Conectd │ │Descon│ │Pending │  │
│ │ 0  │ │   0    │ │  0   │ │   0    │  │
│ └────┘ └────────┘ └──────┘ └────────┘  │
├─────────────────────────────────────────┤
│ Nenhum WhatsApp conectado ainda         │
│ [ + Conectar Novo WhatsApp ]            │
└─────────────────────────────────────────┘
```

✅ **PRONTO! Dashboard funcionando!**

---

## ✨ AGORA O QUE FAZER?

### Teste o QR Code:

1. No dashboard, clique **[ + Conectar Novo WhatsApp ]** (se houver botão)
   - Ou crie um WhatsApp de teste via admin
   - Ou via shell: `python manage.py shell`

```python
from scheduling.models import WhatsAppInstance
from tenants.models import Tenant

tenant = Tenant.objects.first()
wa = WhatsAppInstance.objects.create(
    tenant=tenant,
    phone_number="+5511999999999",
    status="pending"
)
print(wa.id)  # Anote esse ID
```

2. Acesse: `https://seu-dominio.com/whatsapp/{id}/gerar-qrcode/` (POST)
   - Via JavaScript no dashboard (botão)
   - Resultado: JSON com QR code em Base64

3. Veja a QR code na dashboard modal

4. Teste os outros botões (desconectar, set primary)

---

## 🎯 VERIFICAÇÕES RÁPIDAS

### Dashboard carrega? 
```
✅ Sim → Pronto! Siga para testes
❌ Não → Verifique:
  - URLs foram realmente adicionadas?
  - config/urls.py foi salvo?
  - Servidor foi reiniciado?
```

### Botões respondem?
```
✅ Sim → Pronto! QR code deve funcionar
❌ Não → Verifique:
  - Console do navegador (F12)
  - Há erro de CSRF? (improvável)
  - CSRF token está no template? (já está)
```

### QR Code gera?
```
✅ Sim → Pronto! Conecte um WhatsApp real
❌ Não → Verifique:
  - qrcode library instalada? (pip install qrcode[pil])
  - Logs do Django (erros?)
```

---

## 📊 ESTRUTURA DE PASTAS (Confirmação)

```
/Users/user/Desktop/Programação/boraagendar/
├── src/
│   ├── config/
│   │   └── urls.py ← MODIFICAR (Passo 1)
│   ├── scheduling/
│   │   ├── models.py ✅
│   │   ├── views/
│   │   │   └── whatsapp_manager.py ✅
│   │   ├── urls/
│   │   │   └── whatsapp.py ✅
│   │   ├── templates/
│   │   │   └── whatsapp/
│   │   │       ├── dashboard.html ✅
│   │   │       └── detail.html ✅
│   │   └── migrations/
│   │       └── 0011_*.py ✅
│   └── manage.py
├── RESUMO_FINAL_WHATSAPP_DASHBOARD.md (você está aqui)
├── INTEGRACAO_WHATSAPP_DASHBOARD.md (documentação completa)
└── GUIA_GERENCIAR_WHATSAPP.md (guia do usuário)
```

---

## 🔗 PRÓXIMAS ETAPAS (Após 5 min)

### Conectar WhatsApp Real
1. Dashboard → Novo WhatsApp
2. Gerar QR Code
3. Apontar câmera no celular
4. Status muda para "Conectado"

### Integrar com Agendamentos
1. Cliente faz agendamento
2. Sistema envia confirmação no WhatsApp
3. Cliente recebe mensagem ✅

### Configurar Webhooks Evolution
1. Evolution API POST → `/whatsapp/webhook/update/`
2. Status atualiza em tempo real

---

## 🆘 SOS - RÁPIDO

| Problema | Solução |
|----------|---------|
| 404 ao acessar /whatsapp/ | Verificar config/urls.py, reiniciar servidor |
| Botões não funcionam | Ver console (F12), CSRF token OK? |
| QR code não gera | Instalar: `pip install qrcode[pil]` |
| Banco sem nova coluna | Rodar: `python manage.py migrate` |
| "Unauthorized" no webhook | Configurar X-API-Key na Evolution |

---

## ✅ CHECKLIST 5 MIN

- [ ] Editei config/urls.py (adicionei import + path)
- [ ] Apliquei migration (`python manage.py migrate`)
- [ ] Reiniciei servidor (`docker restart` ou Ctrl+C)
- [ ] Acessei `/whatsapp/` no navegador
- [ ] Dashboard carregou com sucesso
- [ ] Vejo stats (todos em 0 é normal)
- [ ] Vejo mensagem "Nenhum WhatsApp conectado"

**Todos checked? 🎉 PARABÉNS! Dashboard está funcionando!**

---

## 🎬 DEMO (O que esperar)

### Tela 1: Dashboard Principal
```
📱 Gerenciar WhatsApps
Conecte seus WhatsApps para receber confirmações...

┌──────────┬──────────┬──────────┬──────────┐
│ Total: 0 │ Conectad│ Descon.: │ Pending: │
│          │ os: 0   │ 0        │ 0        │
└──────────┴──────────┴──────────┴──────────┘

Nenhum WhatsApp conectado ainda
[+ Conectar Novo WhatsApp]
```

### Tela 2: Após criar um WhatsApp
```
📱 Gerenciar WhatsApps

┌──────────┬──────────┬──────────┬──────────┐
│ Total: 1 │ Conectad│ Descon.: │ Pending: │
│          │ os: 0   │ 0        │ 1        │
└──────────┴──────────┴──────────┴──────────┘

┌─ WhatsApp #1 ─────────────────────┐
│ +55 11 9999-9999                  │
│ 📋 Aguardando QR Code             │
│ [ 🔗 Gerar QR Code ]              │
│ [ 📋 Detalhes ]                   │
└───────────────────────────────────┘
```

### Tela 3: Após gerar QR
```
[Modal aparece com QR code em Base64]

Escanear com WhatsApp Web
┌─────────────────────┐
│ [QR CODE IMAGE]     │
│ (5 minutos válido)  │
└─────────────────────┘

Apontando câmera para conectar...
```

### Tela 4: Após conectar
```
┌──────────┬──────────┬──────────┬──────────┐
│ Total: 1 │ Conectad│ Descon.: │ Pending: │
│          │ os: 1   │ 0        │ 0        │
└──────────┴──────────┴──────────┴──────────┘

┌─ WhatsApp #1 ─────────────────────┐
│ +55 11 9999-9999                  │
│ ✅ Conectado e Pronto             │
│ Conectado em: 2024-01-15 10:30    │
│ ⭐ Principal                       │
│ [ 🔗 Gerar QR ]  [ ❌ Desconectar]│
│ [ 📋 Detalhes ]                   │
└───────────────────────────────────┘
```

---

## 🎉 SUCESSO!

Você agora tem um **dashboard funcional** para gerenciar WhatsApps! 

Próximo passo: **Integrar com agendamentos** (mensagens automáticas)

Dúvidas? Ver documentação completa em:
- `RESUMO_FINAL_WHATSAPP_DASHBOARD.md`
- `INTEGRACAO_WHATSAPP_DASHBOARD.md`
- `GUIA_GERENCIAR_WHATSAPP.md`

**Siga os 3 passos acima em 5 minutos!** ⏱️
