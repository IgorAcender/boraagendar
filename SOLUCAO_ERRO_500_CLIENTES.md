# 🚨 SOLUÇÃO IMEDIATA - Erro 500 no EasyPanel

## O PROBLEMA
O sistema de clientes foi criado, mas a **migration não foi aplicada no servidor**.

## ✅ SOLUÇÃO RÁPIDA (2 minutos)

### 1️⃣ Entre no Terminal do EasyPanel

No painel da sua aplicação, clique em **"Terminal"** ou **"Console"**

### 2️⃣ Execute estes 3 comandos:

```bash
cd /app/src
python3 manage.py migrate scheduling
python3 manage.py collectstatic --noinput
```

### 3️⃣ Pronto! ✅

Acesse: **https://robo-de-agendamento-igor.lvh.cm.easypanel.host/dashboard/clientes/**

---

## 🎨 O que você vai ver:

✅ Lista de clientes (vazia no começo)  
✅ Botão "Novo Cliente"  
✅ Formulário moderno com 3 abas:
   - **Cadastro** (nome, email, telefone, CPF, etc)
   - **Endereço** (CEP com busca automática)
   - **Configurações** (WhatsApp, SMS, Email)
✅ Upload de avatar  
✅ Máscaras automáticas (CPF, telefone, CEP)

---

## 🆘 Se ainda der erro:

Execute no terminal do EasyPanel:
```bash
cd /app/src
python3 manage.py showmigrations scheduling
```

Procure por:
```
[X] 0013_customer
```

Se aparecer `[ ]` (sem X), execute novamente:
```bash
python3 manage.py migrate scheduling 0013
```

---

## 📱 Criar clientes de teste (opcional):

```bash
cd /app/src
python3 manage.py shell
```

Depois cole e execute:
```python
from scheduling.models import Customer
from tenants.models import Tenant

tenant = Tenant.objects.first()
Customer.objects.create(
    tenant=tenant,
    name='Maria Silva',
    email='maria@teste.com',
    phone='(11) 98765-4321',
    city='São Paulo',
    state='SP'
)
print("✅ Cliente criado!")
exit()
```

---

**Pronto! O sistema de clientes está funcionando! 🎉**
