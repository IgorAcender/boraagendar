# 🚀 ARQUITETURA MULTI-EVOLUTION API

## 📊 Visão Geral

Seu sistema **Bora Agendar** pode gerenciar **múltiplas instâncias de Evolution API** com até **20 WhatsApps cada**.

### Exemplo:
```
Evolution API 1 → 20 WhatsApps
Evolution API 2 → 20 WhatsApps
Evolution API 3 → 20 WhatsApps
Evolution API 4 → 20 WhatsApps
─────────────────────────
Total: 80 WhatsApps = 80 Negócios Gerenciados
```

---

## 💾 Banco de Dados

### ✅ **1 BANCO PostgreSQL para TODOS**

```sql
Tabelas:
├─ scheduling_evolutionapi         -- Instâncias da API
├─ scheduling_whatsappinstance      -- WhatsApps individuais
└─ scheduling_booking               -- Agendamentos (já existe)
```

**Vantagens:**
- ✅ Simples
- ✅ Barato
- ✅ Fácil de consultar (1 banco)
- ✅ Backups unificados

---

## 🗺️ Fluxo de Dados

```
┌─────────────────────────────────┐
│   Cliente faz Agendamento       │
│   (formulário no mini-site)     │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│   Django Salva Booking          │
│   (scheduling_booking)          │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│   send_booking_confirmation()   │
│   (notification_dispatcher.py)  │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│   EvolutionAPIManager           │
│   .send_message_auto()          │
│   - Seleciona melhor instância  │
│   - Load balancing automático   │
└──────────────┬──────────────────┘
               ↓
    ┌──────────┴──────────┬──────────────┬──────────────┐
    ↓                     ↓              ↓              ↓
┌─────────────┐   ┌────────────┐  ┌────────────┐  ┌────────────┐
│ Evolution 1 │   │ Evolution2 │  │ Evolution3 │  │ Evolution4 │
│ (20 WA)     │   │ (20 WA)    │  │ (20 WA)    │  │ (20 WA)    │
└──────┬──────┘   └──────┬─────┘  └──────┬─────┘  └──────┬─────┘
       │ POST            │                │              │
       └────────────┬────┴────────────────┴──────────────┘
                    ↓
         🟢 WhatsApp Message
         ✉️ Cliente Recebe Confirmação
```

---

## 🔧 Como Configurar

### Passo 1: Fazer Migration

```bash
cd src
python manage.py makemigrations scheduling
python manage.py migrate
```

### Passo 2: Acessar Admin

```
http://seu-dominio.com/admin/
```

### Passo 3: Criar Evolution APIs

1. Vá em: **Scheduling** → **Evolution APIs**
2. Clique em **Add Evolution API**
3. Preencha:
   - **Nome:** "Evolution API 1"
   - **URL:** `https://evo1.seu-dominio.com/message/sendText`
   - **API Key:** (copie do EasyPanel)
   - **Capacidade:** 20
   - **Prioridade:** 10 (maior = mais usada)
   - **Ativa:** ✅

Repita para Evolution 2, 3, 4...

### Passo 4: Adicionar WhatsApps

1. Vá em: **Scheduling** → **WhatsApp Instances**
2. Clique em **Add WhatsApp Instance**
3. Preencha:
   - **Instância Evolution API:** "Evolution API 1"
   - **Número de WhatsApp:** 5511987654321
   - **Nome de Exibição:** "WhatsApp Principal"
   - **Status:** "Conectado"
   - **Principal:** ✅ (primeira vez)
4. **Salvar**

Repita para os outros 19 WhatsApps...

---

## 📊 Monitoramento

No Admin, você vê em tempo real:

### Evolution APIs
```
✅ Evolution API 1 (15/20)
   - Uso: 75%
   - Prioridade: 10

✅ Evolution API 2 (8/20)
   - Uso: 40%
   - Prioridade: 5

❌ Evolution API 3 (0/20)
   - Uso: 0%
   - Prioridade: 1
```

### WhatsApp Instances
```
✅ 5511987654321 (Evolution API 1) - Principal
⏳ 5511987654322 (Evolution API 1) - Conectando
❌ 5511987654323 (Evolution API 2) - Desconectado
✅ 5511987654324 (Evolution API 2) - Conectado
```

---

## 🧠 Load Balancing Automático

O sistema **seleciona automaticamente** qual Evolution API usar:

```python
# Critérios (em ordem):
1. ✅ Ativa?
2. ✅ Tem espaço (< 20 WhatsApps)?
3. 📊 Maior prioridade?
4. 🔄 Menos usada?
```

**Exemplo:**

```
Cenário: Enviar mensagem de agendamento

Evolution API 1: 18/20 WhatsApps (Prioridade: 10)
Evolution API 2: 8/20 WhatsApps  (Prioridade: 5)

✅ Sistema escolhe: Evolution API 1
   Motivo: Maior prioridade, ainda tem espaço
```

---

## 💻 Usando na Prática

### Envio Automático
```python
# Usa a melhor instância automaticamente
send_booking_confirmation(booking)
```

### Envio para Instância Específica
```python
from scheduling.services.evolution_manager import EvolutionAPIManager
from scheduling.models import EvolutionAPI

evo1 = EvolutionAPI.objects.get(name="Evolution API 1")
EvolutionAPIManager.send_message_auto(
    tenant_slug="meu-negocio",
    to_number="5511987654321",
    message="Olá!",
    evolution_api=evo1  # Força essa instância
)
```

### Consultar Estatísticas
```python
stats = EvolutionAPIManager.get_usage_stats()

# Retorna:
{
    "total_instances": 4,
    "total_capacity": 80,
    "total_connected": 51,
    "instances": [
        {
            "name": "Evolution API 1",
            "connected": 18,
            "capacity": 20,
            "available": 2,
            "usage_percentage": 90,
            "status": "✅ Online"
        },
        ...
    ]
}
```

---

## 🔍 Verificações

### Ver Instâncias Ativas
```bash
python manage.py shell
>>> from scheduling.models import EvolutionAPI
>>> EvolutionAPI.objects.filter(is_active=True)
```

### Ver WhatsApps Conectados
```bash
>>> from scheduling.services.evolution_manager import EvolutionAPIManager
>>> EvolutionAPIManager.get_connected_whatsapps()
```

---

## ⚠️ Troubleshooting

### Problema: "Nenhuma Evolution API disponível"
**Solução:**
1. Verificar se pelo menos uma está marcada como "Ativa"
2. Verificar se não atingiu capacidade máxima

### Problema: Mensagem não envia
**Solução:**
1. Confirmar API Key correta
2. Confirmar WhatsApp conectado (status: connected)
3. Verificar logs do Evolution API

### Problema: Muita latência
**Solução:**
1. Distribuir WhatsApps entre Evolution APIs
2. Aumentar prioridade das que têm menos uso

---

## 📈 Escalando para 80+ WhatsApps

Se precisar mais de 80 WhatsApps:

```
Adicionar Evolution API 5 → +20 WhatsApps
Adicionar Evolution API 6 → +20 WhatsApps
...
```

Sistema escala **linearmente** com novos servidores!

---

## ✅ Checklist de Implementação

- [ ] Fazer migration dos novos modelos
- [ ] Criar Evolution APIs no admin
- [ ] Adicionar WhatsApps individuais
- [ ] Testar envio automático
- [ ] Verificar balanceamento de carga
- [ ] Monitorar uso em tempo real

---

**Bora Agendar** - Escala infinita com WhatsApp! 🚀
