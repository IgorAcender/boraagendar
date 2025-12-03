# 🚀 Ação Necessária: Aplicar Migrations na Produção

## Problema Identificado

Os horários de funcionamento não aparecem no mini site porque a migration `0012` (que cria o model `BusinessHours`) **ainda não foi aplicada na produção**.

## Status Atual

✅ **Local**: Migration aplicada com sucesso  
❌ **Produção**: Migration pendente  

---

## Como Resolver

### Na Produção (EasyPanel):

Execute o comando:

```bash
python3 manage.py migrate tenants
```

Ou via SSH no container:

```bash
docker exec <container_id> python3 manage.py migrate tenants
```

---

## Passo a Passo

### 1. **Acesse o EasyPanel**
   - URL: https://easypanel.host/
   - Navegue até seu container

### 2. **Abra o Terminal do Container**
   - Clique em **Terminal** ou **SSH**

### 3. **Execute a Migration**
   ```bash
   cd /app/src
   python3 manage.py migrate tenants
   ```

### 4. **Verifique o Status**
   ```bash
   python3 manage.py showmigrations tenants
   ```
   
   Procure por:
   ```
   [X] 0012_tenant_about_us_...
   ```

### 5. **Teste no Navegador**
   - Acesse o mini site: `https://seu-dominio.com/{tenant-slug}/`
   - Verifique se os horários aparecem

---

## Alternativamente via Git

Se preferir via git:

```bash
# 1. Faça commit e push do código
git add src/
git commit -m "Add BusinessHours model and landing page"
git push origin main

# 2. Sincronize no servidor
cd /app
git pull origin main

# 3. Execute a migration
cd /app/src
python3 manage.py migrate tenants
```

---

## Verificação

Após executar a migration, os horários deverão aparecer no mini site:

**Antes:**
```
Horários não configurados
```

**Depois:**
```
Segunda: 09:00 - 18:00
Terça: 09:00 - 18:00
...
```

---

## Possíveis Erros

### Erro: "No such table: tenants_businesshours"
**Solução**: Execute `python3 manage.py migrate tenants`

### Erro: "Migration already applied"
**Solução**: Já foi aplicada com sucesso

### Erro: "Column already exists"
**Solução**: Use `--fake` se necessário (já resolvemos isso antes)

---

## Checklist

- [ ] Acessei o EasyPanel
- [ ] Executei `python3 manage.py migrate tenants`
- [ ] Verifiquei com `showmigrations` que 0012 está `[X]`
- [ ] Testei o mini site e os horários aparecem
- [ ] Confirmação recebida do usuário

---

**Data**: 3 de dezembro de 2025  
**Prioridade**: 🔴 ALTA - Necessário para funcionamento completo
