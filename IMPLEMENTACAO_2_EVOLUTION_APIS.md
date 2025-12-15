# 🚀 IMPLEMENTAÇÃO: 2 Evolution APIs + 100 WhatsApps

## 📋 Arquitetura Inicial

```
┌─────────────────────────────────────────────────────────┐
│          DJANGO (Bora Agendar)                          │
│                                                          │
│  - EvolutionAPI (2 instâncias)                          │
│  - WhatsAppInstance (100 WhatsApps)                     │
│  - Booking (agendamentos)                               │
│                                                          │
│  PostgreSQL + Redis                                     │
└──────────────┬──────────────────────────────────────────┘
               │
               ├─→ NGINX Load Balancer
               │
       ┌───────┴────────────┐
       ↓                    ↓
┌─────────────────┐   ┌─────────────────┐
│ Evolution API 1 │   │ Evolution API 2 │
│ 50 WhatsApps    │   │ 50 WhatsApps    │
│ Porto: 8080     │   │ Porto: 8081     │
│ URL: evo1:8080  │   │ URL: evo2:8081  │
└─────────────────┘   └─────────────────┘
       │                    │
       └───────┬────────────┘
               ↓
    PostgreSQL + Redis
    (compartilhado)
```

---

## ✅ Checklist de Implementação

### Fase 1: Setup Django (10 min)
- [ ] 1a. Fazer migration dos modelos
- [ ] 1b. Verificar se migrações passaram

### Fase 2: Registrar Evolution APIs (5 min)
- [ ] 2a. Registrar Evolution API 1 no admin
- [ ] 2b. Registrar Evolution API 2 no admin

### Fase 3: Criar WhatsApps (5 min)
- [ ] 3a. Script para criar 100 WhatsApps
- [ ] 3b. Verificar se foram criados

### Fase 4: Testar (10 min)
- [ ] 4a. Testar envio automático
- [ ] 4b. Verificar load balancing

---

## 🎯 Próximo Passo: Fazer Migration

Execute este comando:

```bash
cd /Users/user/Desktop/Programação/boraagendar/src
python manage.py makemigrations scheduling
python manage.py migrate
```

**O que será criado:**
- Tabela `scheduling_evolutionapi` (2 registros)
- Tabela `scheduling_whatsappinstance` (100 registros)

---

## 📝 Dados para Registrar no Admin

### Evolution API 1:
```
Nome: Evolution API 1
URL: https://[seu-dominio-evo1]/message/sendText
Instance ID: evolution-1
API Key: 429683C4C977415CAAFCCE10F7D57E11
Capacidade: 50
Prioridade: 10
Ativa: ✅
```

### Evolution API 2:
```
Nome: Evolution API 2
URL: https://[seu-dominio-evo2]/message/sendText
Instance ID: evolution-2
API Key: 429683C4C977415CAAFCCE10F7D57E11
Capacidade: 50
Prioridade: 5
Ativa: ✅
```

---

## 🔄 Próximos Passos Detalhados

1. **Fazer migration** ← Você está aqui
2. Registrar 2 Evolution APIs no admin
3. Executar script para criar 100 WhatsApps
4. Testar envio de agendamento
5. Monitorar carga entre os 2 containers

---

**Vamos começar? Execute:**

```bash
cd /Users/user/Desktop/Programação/boraagendar/src
python manage.py makemigrations scheduling
```

Me avisa quando passar! 🚀
