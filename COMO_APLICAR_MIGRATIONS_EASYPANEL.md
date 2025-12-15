# 🚀 COMO APLICAR MIGRATIONS NA EASYPANEL

Seu código está **100% pronto**. Apenas precisa aplicar as migrations no banco de dados da EasyPanel.

---

## ✅ O que foi feito

```
✅ Modelos criados: EvolutionAPI e WhatsAppInstance
✅ Migração gerada: scheduling/migrations/0010_evolutionapi_whatsappinstance.py
✅ Scripts prontos:
   - setup_evolution_simple.sh      (registra 1 Evolution)
   - create_whatsapp_instances_simple.py   (cria 50 WhatsApps)
```

---

## 🔧 PASSO A PASSO - Aplicar Migrations

### Opção 1: Via EasyPanel Admin (RECOMENDADO)

1. Acesse: `https://your-domain.com/admin/`
2. Faça login

3. Abra o **terminal do container Django**:
   - Painel EasyPanel → seu projeto → Terminal
   
4. Execute dentro do terminal:
```bash
cd /app/src  # ou o caminho do seu Django
python manage.py migrate
```

5. Verá:
```
Operations to perform:
  Apply all migrations: ...
  Preparing migrations: Done
  Applying scheduling.0010_evolutionapi_whatsappinstance... OK
```

---

### Opção 2: Via Git Push (se tiver CI/CD)

Se seu repositório tem webhook configurado:

```bash
# Local
git add .
git commit -m "feat: add Evolution API models and migrations"
git push origin main
```

A EasyPanel aplicará as migrations automaticamente.

---

### Opção 3: SSH Direto (se tiver acesso)

```bash
ssh user@your-server.com
cd /caminho/do/projeto
python manage.py migrate
```

---

## 📋 Checklist Pós-Migração

Depois de rodar `migrate`, execute:

```bash
# 1. Verificar que tudo OK
python manage.py check

# 2. Registrar 1 Evolution API
bash ../setup_evolution_simple.sh

# 3. Criar 50 WhatsApps
python create_whatsapp_instances_simple.py

# 4. Ver no admin
# Acesse: /admin/scheduling/evolutionapivolume/
```

---

## 📱 Arquivos Criados

```
✅ scheduling/models.py
   └─ Adicionados:
      • EvolutionAPI (gerencia instâncias)
      • WhatsAppInstance (gerencia WhatsApps)

✅ scheduling/migrations/0010_evolutionapi_whatsappinstance.py
   └─ Cria tabelas no PostgreSQL

✅ scheduling/services/evolution_manager.py
   └─ Já existe, importa os modelos

✅ setup_evolution_simple.sh
   └─ Registra 1 Evolution API com seus dados

✅ src/create_whatsapp_instances_simple.py
   └─ Cria 50 WhatsApps automaticamente
```

---

## 🔐 Dados do seu Evolution API

Já preenchidos automaticamente:

```
Instance ID: evolution-1
URL: https://robo-de-agendamento-igor.ivhjcm.easypanel.host
API Key: 429683C4C977415CAAFCCE10F7D57E11
Capacity: 50 WhatsApps
Priority: 10
```

---

## 🆘 Se der erro

### "Tabela já existe"
→ Tudo OK! Script detecta e continua

### "API Key inválida"
→ Verifique em `.env` ou Evolution API settings

### "Sem conexão com banco"
→ Aguarde container estar pronto (2-3 min)

---

## 🎯 Próximos Passos

1. ✅ Aplique a migração (agora)
2. ✅ Registre 1 Evolution (2 min)
3. ✅ Crie 50 WhatsApps (2 min)
4. 📱 Conecte WhatsApps no Evolution (via interface)
5. 🧪 Teste envio de mensagem
6. 📈 Quando pronto, escale para 2º Evolution

---

## 📞 Checklist Final

```
[ ] Migration aplicada com sucesso
[ ] Evolution API registrado no admin
[ ] 50 WhatsApps criados no banco
[ ] Admin mostra: evolution-1 com 50/50 (100%)
[ ] Load balancing ativo
[ ] Próximo: Escalar a 100 WhatsApps (adicionar 2º Evolution)
```

---

**Bora aplicar! 🚀**

```bash
# Dentro do terminal da EasyPanel
python manage.py migrate
```
