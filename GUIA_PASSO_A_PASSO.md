# 🚀 GUIA PASSO A PASSO: 2 Evolution APIs + 100 WhatsApps

## 📋 4 Passos Simples

### 🔷 PASSO 1: Fazer Migration (2 min)

```bash
cd /Users/user/Desktop/Programação/boraagendar/src
python manage.py makemigrations scheduling
python manage.py migrate
```

**Resultado esperado:**
```
Migrations for 'scheduling':
  scheduling/migrations/0XXX_initial.py
    - Create model EvolutionAPI
    - Create model WhatsAppInstance
Running migrations:
  Applying scheduling.0XXX... OK
```

---

### 🔷 PASSO 2: Registrar as 2 Evolution APIs (3 min)

**Opção A: Script automático (RECOMENDADO)**

```bash
cd /Users/user/Desktop/Programação/boraagendar
bash register_evolution_apis.sh
```

**O que faz:**
- ✅ Cria Evolution API 1 (prioridade 10)
- ✅ Cria Evolution API 2 (prioridade 5)
- ✅ Mostra resumo

**Resultado esperado:**
```
✅ Evolution API 1 criada com sucesso
   URL: https://evo1.seu-dominio/message/sendText
   Prioridade: 10

✅ Evolution API 2 criada com sucesso
   URL: https://evo2.seu-dominio/message/sendText
   Prioridade: 5
```

---

**Opção B: Admin Django (Manual)**

Se preferir fazer pelo admin:

1. Vá para: `http://seu-dominio/admin/`
2. Clique em: **Scheduling** → **Evolution APIs**
3. Clique em: **Add Evolution API**
4. Preencha:
   - Nome: `Evolution API 1`
   - URL: `https://evo1.seu-dominio/message/sendText`
   - API Key: `429683C4C977415CAAFCCE10F7D57E11`
   - Capacidade: `50`
   - Prioridade: `10`
   - Ativa: ✅
5. Salve
6. Repita para Evolution API 2 (prioridade 5)

---

### 🔷 PASSO 3: Criar 100 Instâncias de WhatsApp (2 min)

```bash
cd /Users/user/Desktop/Programação/boraagendar/src
python create_whatsapp_instances.py
```

**O que faz:**
- ✅ Cria 50 WhatsApps em Evolution API 1
- ✅ Cria 50 WhatsApps em Evolution API 2
- ✅ Marca 1 como "principal" em cada
- ✅ Mostra estatísticas

**Resultado esperado:**
```
✅ CRIANDO 100 INSTÂNCIAS DE WHATSAPP

📋 Buscando Evolution APIs...
✅ Encontradas 2 Evolution APIs

🔨 Criando instâncias...

   Evolution API 1: Evolution API 1
      ✅ 50/50 concluídos!
   
   Evolution API 2: Evolution API 2
      ✅ 50/50 concluídos!

📊 RESUMO
✅ Instâncias criadas: 100
```

---

### 🔷 PASSO 4: Testar Integração (5 min)

**Teste A: Verificar no Admin**

1. Vá para: `http://seu-dominio/admin/`
2. Clique em: **Scheduling** → **WhatsApp Instances**
3. Veja a lista de 100 WhatsApps

**Teste B: Verificar Load Balancing**

```bash
cd /Users/user/Desktop/Programação/boraagendar/src
python manage.py shell << 'EOF'
from scheduling.services.evolution_manager import EvolutionAPIManager

stats = EvolutionAPIManager.get_usage_stats()
print("\n📊 ESTATÍSTICAS DE USO\n")
print(f"Total de instâncias: {stats['total_instances']}")
print(f"Capacidade total: {stats['total_capacity']} WhatsApps")
print(f"Conectados: {stats['total_connected']}")
print()

for inst in stats['instances']:
    print(f"✅ {inst['name']}")
    print(f"   Conectados: {inst['connected']}/{inst['capacity']}")
    print(f"   Disponíveis: {inst['available']}")
    print(f"   Uso: {inst['usage_percentage']}%")
    print()
EOF
```

**Teste C: Testar Envio Automático**

1. Acesse o admin
2. Vá para: **Scheduling** → **Bookings**
3. Clique em: **Add Booking**
4. Preencha com um teste e salve
5. Sistema deve:
   - ✅ Selecionar uma das 2 Evolution APIs
   - ✅ Enviar confirmação via WhatsApp
   - ✅ Registrar no log

---

## 🎯 Resumo Visual

```
ANTES (sem WhatsApp):
└─ Agendamento → Email (apenas)

DEPOIS (com 2 Evolution APIs):
└─ Agendamento 
   ├─ Email ✅
   └─ WhatsApp (auto-distribuído entre 2 servidores) ✅
      ├─ Evolution API 1 (50 WhatsApps) → 60% de chance
      └─ Evolution API 2 (50 WhatsApps) → 40% de chance
```

---

## 📊 Arquitetura Final

```
Django App
    ↓
send_booking_confirmation()
    ↓
EvolutionAPIManager.send_message_auto()
    ├─ Seleciona Evolution API 1 (prioridade 10) se houver espaço
    └─ Senão, seleciona Evolution API 2 (prioridade 5)
    ↓
Evolution API 1 ou 2
    ↓
WhatsApp Message ✅ Sent!
```

---

## ✅ Checklist Completo

- [ ] Passo 1: Migration executada
- [ ] Passo 2: Evolution APIs registradas
- [ ] Passo 3: 100 WhatsApps criados
- [ ] Passo 4: Testes passaram
- [ ] Admin acessível: http://seu-dominio/admin/
- [ ] Estatísticas visíveis
- [ ] Agendamento envia via WhatsApp

---

## 🚨 Troubleshooting

### Erro: "Nenhuma Evolution API disponível"
**Solução:** Verificar se as 2 estão marcadas como "Ativa" no admin

### Erro: "Invalid API Key"
**Solução:** Confirmar se a chave está correta no .env

### Erro: "WhatsApp não conectado"
**Solução:** Conectar os WhatsApps no painel da Evolution API

### Falta dados no admin
**Solução:** 
```bash
# Verificar migração
python manage.py migrate scheduling --list

# Refazer se necessário
python manage.py migrate scheduling zero
python manage.py migrate scheduling
```

---

## 🎓 Próximas Fases

### Fase 2: Adicionar mais (quando precisar)
- Adicionar Evolution API 3, 4, 5...
- Script automático faz distribuição

### Fase 3: Monitoramento
- Dashboard com estatísticas em tempo real
- Alertas se alguma ficar fora

### Fase 4: Otimizações
- Webhooks para sincronizar status
- Mensagens customizadas por tenant
- Lembretes antes do agendamento

---

**Vamos começar? Rode o PASSO 1 agora!** 🚀

```bash
cd /Users/user/Desktop/Programação/boraagendar/src
python manage.py makemigrations scheduling
python manage.py migrate
```

Me avisa quando passar! ✅
