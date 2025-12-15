# 🚀 SETUP EASYPANEL - BORA AGENDAR COM WHATSAPP

## Status: ✅ 100% Pronto para Deploy

Você tem um script que faz TUDO automaticamente. Execute dentro do terminal da EasyPanel.

---

## 🎯 EM 1 MINUTO

Na EasyPanel Admin:

1. Abra: **Terminal do Container Django**
2. Execute:
```bash
cd /app/src
bash ../../easypanel_setup_completo.sh
```

3. Pronto! ✅

---

## 📋 O QUE O SCRIPT FAZ (automaticamente)

```
✅ 1. Verifica Django (python manage.py check)
✅ 2. Aplica migrações (makemigrations + migrate)
✅ 3. Registra 1 Evolution API com seus dados
✅ 4. Cria 50 WhatsApps no banco
✅ 5. Mostra resumo final
```

---

## 🔐 DADOS DO SEU APP (já preenchidos no script)

```
Domínio:    robo-de-agendamento-igor.ivhjcm.easypanel.host
Banco:      agendamento @ robo_de_agendamento_igor-postgres
Redis:      robo_de_agendamento_igor-redis
API Key:    429683C4C977415CAAFCCE10F7D57E11
```

---

## 🔧 SETUP PASSO A PASSO (se preferir manual)

### Passo 1: Aplicar Migrações

```bash
cd /app/src
python manage.py migrate
```

Esperado:
```
Applying scheduling.0010_evolutionapi_whatsappinstance... OK
```

### Passo 2: Registrar Evolution

```bash
python manage.py shell << 'EOF'
from scheduling.models import EvolutionAPI

EvolutionAPI.objects.create(
    instance_id='evolution-1',
    url='https://robo-de-agendamento-igor.ivhjcm.easypanel.host',
    api_key='429683C4C977415CAAFCCE10F7D57E11',
    capacity=50,
    priority=10,
    is_active=True
)
print("✅ Evolution criado!")
EOF
```

### Passo 3: Criar 50 WhatsApps

```bash
python create_whatsapp_instances_simple.py
```

Esperado:
```
✅ 50 instâncias criadas
📊 evolution-1: 50/50 (100%)
```

---

## 📱 VERIFICAR TUDO FUNCIONOU

### Via Django Shell

```bash
python manage.py shell
```

```python
from scheduling.models import EvolutionAPI, WhatsAppInstance

# Ver Evolution APIs
EvolutionAPI.objects.all()
# <QuerySet [<EvolutionAPI: ✅ evolution-1 (50/50)>]>

# Contar WhatsApps
WhatsAppInstance.objects.count()
# 50

# Ver status
from django.db.models import Count
WhatsAppInstance.objects.values('connection_status').annotate(total=Count('id'))
# <QuerySet [{'connection_status': 'pending', 'total': 50}]>
```

### Via Django Admin

Acesse: `https://seu-dominio.com/admin/`

Navegue para: **Scheduling → Evolution API**

Esperado:
- [ ] `evolution-1` aparece
- [ ] Status: ✅ ATIVO
- [ ] Capacity: 50/50 (100%)

---

## 🎯 DADOS DA EASYPANEL

Se precisar conectar diretamente ao banco:

```
HOST:     robo_de_agendamento_igor-postgres
PORT:     5432
USER:     postgres
PASSWORD: Acender@123!
DATABASE: agendamento
```

Redis:
```
HOST:     robo_de_agendamento_igor-redis
PORT:     6379
PASSWORD: Acender@123!
DB:       0
```

---

## 🚀 ARQUIVOS CRIADOS

```
✅ easypanel_setup_completo.sh
   └─ Script all-in-one para EasyPanel
   
✅ setup_evolution_simple.sh
   └─ Versão separada (se preferir executar partes)
   
✅ setup_evolution_add.sh
   └─ Para adicionar 2º Evolution depois
   
✅ src/create_whatsapp_instances_simple.py
   └─ Criar WhatsApps (chamado pelo script principal)
```

---

## 📊 INTEGRAÇÃO COM AGENDAMENTOS

Depois de pronto, qualquer agendamento enviará WhatsApp:

```python
# scheduling/services/notification_dispatcher.py
def send_booking_confirmation(booking):
    # Load balancer seleciona Evolution automaticamente
    manager = EvolutionAPIManager()
    manager.send_message_auto(
        phone=booking.customer_phone,
        message=f"Sua consulta está agendada para {booking.scheduled_for}"
    )
    # ✅ Mensagem enviada via WhatsApp!
```

---

## 🔄 ESCALAR DEPOIS

Quando atingir 100% de utilização:

```bash
# Adicionar 2º Evolution
bash setup_evolution_add.sh

# Criar mais 50 WhatsApps
python create_whatsapp_instances_simple.py
```

Resultado: 100 WhatsApps (50 em cada Evolution)

---

## 🐛 TROUBLESHOOTING

### Erro: "Migração não pode ser aplicada"

```bash
# Verificar status
python manage.py showmigrations scheduling

# Se ver 0010 marcada como NOT applied:
python manage.py migrate scheduling 0010

# Se houver erro de schema:
python manage.py makemigrations scheduling
python manage.py migrate
```

### Erro: "Evolution API já existe"

Tudo bem! O script detecta automaticamente. Execute novamente e verá:

```
⚠️  Evolution API 'evolution-1' já existe
```

### Erro: "Sem conexão com banco"

Aguarde 2-3 minutos para container iniciar completamente.

### Erro: "API Key inválida"

Verifique em `.env`:
```bash
# Deve ser:
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
```

---

## 📞 CHECKLIST FINAL

```
[ ] Acessou terminal EasyPanel
[ ] Executou: bash easypanel_setup_completo.sh
[ ] Viu "✅ Setup concluído!"
[ ] Evolution API aparece no admin
[ ] 50 WhatsApps aparecem no admin
[ ] Status de todos: "pending" (esperando conexão)
[ ] Próximo: Conectar WhatsApps no Evolution
```

---

## 🎉 RESUMO

**Você tem:**
- ✅ 1 Evolution API gerenciado
- ✅ 50 WhatsApps registrados
- ✅ Load balancer automático
- ✅ Admin interface visual
- ✅ Script all-in-one

**Falta:**
1. ⏱️ Executar o script (1 min)
2. ⏱️ Conectar WhatsApps no Evolution (manual, 5 min)
3. ⏱️ Testar com um agendamento

---

## 🚀 EXECUTE AGORA

Na EasyPanel Terminal:

```bash
cd /app/src
bash ../../easypanel_setup_completo.sh
```

Pronto! 🎉

---

**Bora agendar com WhatsApp! 📱✅**
