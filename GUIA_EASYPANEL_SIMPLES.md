# 🎯 GUIA SIMPLES - EXECUTE NA EASYPANEL

## ⚠️ IMPORTANTE

O banco de dados está na **EasyPanel**, não na sua máquina.

Por isso precisamos executar os comandos **dentro da EasyPanel**, não localmente.

---

## 🚀 PASSO 1: Acessar Terminal da EasyPanel

1. Entre em: **https://seu-painel.easypanel.io**
2. Selecione seu projeto: **robo-de-agendamento-igor**
3. Clique em **Terminal** (à direita)
4. Abre um terminal **dentro do container Docker**

---

## 🔧 PASSO 2: Executar o Setup

Dentro do terminal da EasyPanel:

```bash
# Ir para o diretório do Django
cd /app/src

# Executar o script all-in-one
bash ../../easypanel_setup_completo.sh
```

**Isso vai fazer automaticamente:**
```
✅ 1. Aplicar migração (scheduling.0010)
✅ 2. Registrar 1 Evolution API
✅ 3. Criar 50 WhatsApps
✅ 4. Mostrar resumo final
```

**Tempo:** ~30-60 segundos

---

## ✅ RESULTADO ESPERADO

```
╔════════════════════════════════════════════════════════════════╗
║                    🎉 SETUP CONCLUÍDO!                        ║
╚════════════════════════════════════════════════════════════════╝

📊 RESUMO FINAL:

Evolution APIs:
   ✅ evolution-1: 50/50 (100%)

Total de WhatsApps: 50
   📋 pending: 50

✅ Sistema pronto para enviar WhatsApps!
```

---

## 🔍 VERIFICAR FUNCIONAMENTO

Após o script:

1. **Django Admin:**
   ```
   https://robo-de-agendamento-igor.ivhjcm.easypanel.host/admin/
   → Scheduling → Evolution API Volume
   → Deve aparecer: evolution-1 (50/50)
   ```

2. **Testar:**
   - Crie um agendamento
   - WhatsApp será enviado automaticamente ✅

---

## 📝 ALTERNATIVA: Executar Passo a Passo

Se preferir fazer manualmente:

### Passo 1: Migração

```bash
cd /app/src
python manage.py migrate
```

Esperado: `Applying scheduling.0010_evolutionapi_whatsappinstance... OK`

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

### Passo 3: Criar WhatsApps

```bash
python create_whatsapp_instances_simple.py
```

---

## 🆘 SE DER ERRO

### "Arquivo não encontrado"

Se o script não estiver onde você esperava:

```bash
# Procurar o arquivo
find /app -name "easypanel_setup_completo.sh" -type f

# Se encontrou, executar com caminho completo
bash /app/easypanel_setup_completo.sh
```

### "Migração não pode ser aplicada"

```bash
# Verificar versão do Django
python manage.py --version

# Tentar migração explícita
python manage.py migrate scheduling 0010
```

### "Evolution API já existe"

Tudo bem! O script detecta e pula. Execute novamente e verá:

```
⚠️  Evolution API 'evolution-1' já existe
```

---

## 📱 PRÓXIMOS PASSOS

1. ✅ Execute o script (agora)
2. ✅ Verifique no Django Admin
3. ⏳ Conecte WhatsApps no Evolution (manual, 5 min)
4. ⏳ Teste com um agendamento

---

## 💡 RESUMO

| Ação | Onde | Como | Tempo |
|------|------|------|-------|
| Script all-in-one | EasyPanel Terminal | `bash ../../easypanel_setup_completo.sh` | 1 min |
| Verify | Django Admin | `/admin/scheduling/evolutionapivolume/` | 2 min |
| Teste | Criar agendamento | Manual | 5 min |

---

## 🎉 PRONTO!

Depois que o script terminar, seu Bora Agendar estará enviando WhatsApps automaticamente! 🚀

---

**Execute agora na EasyPanel:**

```bash
cd /app/src && bash ../../easypanel_setup_completo.sh
```
