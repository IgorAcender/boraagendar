# 🚀 QUICK START - Começar com 1 Evolution API

## ⏱️ Tempo total: ~5 minutos

---

## PASSO 1: Migração (1 min)

```bash
cd /Users/user/Desktop/Programação/boraagendar/src

# Criar e aplicar migrações
python manage.py makemigrations scheduling
python manage.py migrate
```

✅ Quando funcionar: Verá "OK" ou "No changes detected"

---

## PASSO 2: Registrar Evolution API (1 min)

Volta uma pasta e executa o script:

```bash
cd ..
bash setup_evolution_simple.sh
```

Isso registra seu Evolution API existente no banco com:
- ✅ Instance ID: `evolution-1`
- ✅ URL: `https://robo-de-agendamento-igor.ivhjcm.easypanel.host`
- ✅ API Key: `429683C4C977415CAAFCCE10F7D57E11`
- ✅ Capacity: 50 WhatsApps

---

## PASSO 3: Criar 50 WhatsApps (2 min)

```bash
cd src
python create_whatsapp_instances_simple.py
```

Verá:
```
✅ 50 instâncias criadas
📊 evolution-1: 50/50 (100%)
```

---

## 🎉 Pronto!

Seu sistema está funcionando com:
- ✅ 1 Evolution API registrado
- ✅ 50 WhatsApps no banco de dados
- ✅ Load balancing ativo

---

## 📊 Verificar Status

Acesse o Django Admin:

```
http://seu-dominio/admin/scheduling/evolutionapivolume/
```

Verá:
- `evolution-1` com 50 WhatsApps conectados
- Utilização: 100%

---

## 🔄 Escalar Depois (Adicionar 2º Evolution)

Quando estiver pronto para expandir:

```bash
bash setup_evolution_add.sh
```

Isso:
1. Adiciona um 2º Evolution API
2. Rebalanceia os 50 WhatsApps (25 cada)
3. Permite criar 50 novos

---

## 🐛 Troubleshooting

### Erro: "No module named 'scheduling'"

```bash
cd /Users/user/Desktop/Programação/boraagendar/src
python manage.py check
```

### Evolution API já existe

Tudo bem! O script verifica automaticamente.

### Ver Evolution APIs criados

```bash
python manage.py shell
>>> from scheduling.models import EvolutionAPI
>>> EvolutionAPI.objects.all()
```

---

## 📚 Documentação Completa

Para entender a arquitetura completa:
- `WHATSAPP_README.md` - Overview
- `ARQUITETURA_MULTI_EVOLUTION.md` - Detalhes técnicos
- `GUIA_PASSO_A_PASSO.md` - Guia completo

---

**Bora começar! Execute o PASSO 1 agora:** 👇

```bash
cd /Users/user/Desktop/Programação/boraagendar/src
python manage.py makemigrations scheduling
python manage.py migrate
```
