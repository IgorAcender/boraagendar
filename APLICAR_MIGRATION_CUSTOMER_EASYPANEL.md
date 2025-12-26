# 🚀 Aplicar Migration do Modelo Customer no EasyPanel

## ⚠️ PROBLEMA ATUAL
Server Error (500) porque o modelo `Customer` foi criado mas a migration não foi aplicada no servidor de produção.

## ✅ SOLUÇÃO

### 1. Acesse o Terminal do Container no EasyPanel

No painel do EasyPanel:
1. Vá até sua aplicação
2. Clique em **"Terminal"** ou **"Console"**
3. Execute os comandos abaixo:

```bash
# Navegue até o diretório
cd /app/src

# Verifique migrations pendentes
python3 manage.py showmigrations scheduling

# Aplique a migration do Customer
python3 manage.py migrate scheduling

# Confirme que foi aplicada
python3 manage.py showmigrations scheduling
```

### 2. Ou use SSH (se tiver acesso)

```bash
# Conecte ao servidor
ssh seu-usuario@seu-servidor

# Entre no container
docker exec -it <container-id> bash

# Execute
cd /app/src
python3 manage.py migrate scheduling
```

## 📝 Migration que será aplicada:
- **scheduling.0013_customer** - Cria tabela de clientes com todos os campos

## ✅ Após aplicar:

1. Recarregue a aplicação no EasyPanel (se necessário)
2. Acesse: `https://robo-de-agendamento-igor.lvh.cm.easypanel.host/dashboard/clientes/`
3. O erro 500 deve ter sumido!

## 🔍 Verificação de Sucesso:

Execute no terminal do EasyPanel:
```bash
cd /app/src
python3 manage.py dbshell
```

Depois execute no SQLite/PostgreSQL:
```sql
-- SQLite
SELECT name FROM sqlite_master WHERE type='table' AND name='scheduling_customer';

-- PostgreSQL
\dt scheduling_customer
```

Se retornar a tabela, está tudo OK! ✅
