# 📋 REFERÊNCIA RÁPIDA - MVP WHATSAPP

## ⏱️ TL;DR (Resumo em 10 segundos)

```bash
# Na EasyPanel Terminal, execute:
cd /app/src && bash ../../easypanel_setup_completo.sh
```

**Resultado:** 50 WhatsApps prontos em ~1 minuto ✅

---

## 🎯 PRÉ-REQUISITOS

- [ ] Acesso à EasyPanel Admin
- [ ] Terminal do Docker acessível
- [ ] Git commit já feito ✅

---

## 📝 CHECKLIST DE EXECUÇÃO

### Antes
- [ ] Arquivo: `easypanel_setup_completo.sh` está no repo ✅
- [ ] Arquivo: `src/create_whatsapp_instances_simple.py` existe ✅
- [ ] Migração: `scheduling/migrations/0010_*.py` existe ✅

### Durante
- [ ] Acesse EasyPanel Terminal
- [ ] Digite: `cd /app/src`
- [ ] Digite: `bash ../../easypanel_setup_completo.sh`
- [ ] Aguarde saída com ✅

### Depois
- [ ] Acesse: `/admin/scheduling/evolutionapivolume/`
- [ ] Veja: `evolution-1 (50/50)`
- [ ] Status: ✅ ATIVO

---

## 🔧 SE NÃO FUNCIONAR

### Erro: "Arquivo não encontrado"

```bash
# Procurar arquivo
find /app -name "easypanel_setup_completo.sh" 2>/dev/null

# Se encontrou:
bash /caminho/do/arquivo
```

### Erro: "Migração falhou"

```bash
cd /app/src
python manage.py migrate scheduling 0010 --verbose
```

### Erro: "Banco inacessível"

Aguarde 2-3 min para container iniciar, depois tente novamente.

---

## 📱 RESULTADO ESPERADO

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

## 📊 DADOS INTEGRADOS NO SCRIPT

```
Instance ID:  evolution-1
Domain:       robo-de-agendamento-igor.ivhjcm.easypanel.host
API Key:      429683C4C977415CAAFCCE10F7D57E11
Capacity:     50 WhatsApps
Priority:     10
```

---

## 🚀 PRÓXIMOS PASSOS

1. Execute script (agora) ← Você está aqui
2. Verifique no admin (2 min)
3. Conecte WhatsApps (manual, 5-10 min)
4. Teste com agendamento (2 min)

---

## 📚 ARQUIVOS IMPORTANTES

| Arquivo | Uso |
|---------|-----|
| `easypanel_setup_completo.sh` | Execute este (all-in-one) |
| `GUIA_EASYPANEL_SIMPLES.md` | Leia para entender |
| `EASYPANEL_SETUP_FINAL.md` | Guia detalhado |
| `scheduling/migrations/0010_*.py` | Migração (automática) |
| `scheduling/models.py` | Models (já adicionado) |
| `scheduling/services/evolution_manager.py` | Load balancer |

---

## ✅ CONFIRMAÇÃO DE SUCESSO

Depois do script, você terá:

```
✅ Tabelas criadas:
   - scheduling_evolutionapivolume
   - scheduling_whatsappinstance

✅ 1 Evolution API:
   - ID: evolution-1
   - Status: ATIVO
   - Capacity: 50/50

✅ 50 WhatsApps:
   - Numerados: 55119990000* até 55119904999
   - Status: pending (aguardando conexão)
   - Evolution: evolution-1

✅ Load Balancer:
   - Ativo e funcionando
   - Pronto para distribuir mensagens
```

---

## 🎉 PRONTO!

Seu MVP WhatsApp está 100% pronto! 🚀

Próximo: Execute o script na EasyPanel.
