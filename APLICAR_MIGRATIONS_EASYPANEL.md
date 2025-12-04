# 🚀 Aplicar Migrações no EasyPanel - Correção Erro 500 "Cores e Marca"

## 📋 Problema

A aba "Cores e Marca" está dando **erro 500** porque há migrações pendentes no banco de dados de produção.

## ✅ Migrações que Precisam Ser Aplicadas

1. **tenants.0015_remove_old_branding_fields** - Remove campos antigos do BrandingSettings
2. **tenants.0016_alter_brandingsettings_button_color_primary_and_more** - Atualiza campos de cor
3. **raffles.0001_initial** - Cria tabela de sorteios (se aplicável)

---

## 🔧 Como Aplicar (Passo a Passo)

### Opção 1: Via Terminal do EasyPanel (Recomendado)

1. **Acesse o EasyPanel**
   - Faça login no painel
   - Navegue até seu projeto/aplicação

2. **Abra o Terminal/Console do Container**
   - Procure por "Terminal", "Console" ou "Shell"
   - Isso abrirá um terminal dentro do container Docker

3. **Execute os comandos:**

```bash
# Navegue até o diretório do projeto
cd /app/src

# Verifique as migrações pendentes
python3 manage.py showmigrations

# Aplique todas as migrações
python3 manage.py migrate

# Verifique se foi aplicado
python3 manage.py showmigrations tenants
```

---

### Opção 2: Via Deploy Automático (Se configurado)

1. **Faça commit das migrações:**

```bash
# No seu computador local
cd /Users/user/Desktop/Programação/boraagendar

# Adicione as novas migrações ao git
git add src/tenants/migrations/0015_remove_old_branding_fields.py
git add src/tenants/migrations/0016_alter_brandingsettings_button_color_primary_and_more.py
git add src/raffles/migrations/0001_initial.py

# Commit
git commit -m "fix: Apply pending migrations for BrandingSettings (fixes 500 error on Cores e Marca)"

# Push para o repositório
git push origin main
```

2. **No EasyPanel:**
   - Se o deploy automático está configurado, aguarde o build
   - Caso contrário, faça o deploy manual
   - **IMPORTANTE**: Depois do deploy, ainda precisa executar as migrações via terminal

3. **Execute as migrações no terminal do EasyPanel:**

```bash
cd /app/src
python3 manage.py migrate
```

---

### Opção 3: Via SSH Direto (Se tiver acesso SSH)

```bash
# Conecte via SSH ao servidor
ssh seu-usuario@seu-servidor.com

# Acesse o container
docker ps  # Encontre o ID do container
docker exec -it <container-id> bash

# Execute as migrações
cd /app/src
python3 manage.py migrate
```

---

## 🧪 Verificação

Após aplicar as migrações, teste:

1. **Faça login como dono do salão**
2. **Acesse**: Menu → Configurações → Cores e Marca
3. **Verifique**: A página deve carregar sem erro 500
4. **Teste**: Altere as cores e salve

---

## 📊 Comandos Úteis para Diagnóstico

```bash
# Ver todas as migrações e seu status
python3 manage.py showmigrations

# Ver apenas migrações pendentes
python3 manage.py showmigrations | grep "[ ]"

# Ver detalhes de uma app específica
python3 manage.py showmigrations tenants

# Fazer backup do banco antes de aplicar (PostgreSQL)
pg_dump -U postgres -d seu_banco > backup_$(date +%Y%m%d).sql
```

---

## ⚠️ Notas Importantes

1. **Backup**: Sempre faça backup do banco antes de aplicar migrações em produção
2. **Downtime**: As migrações devem ser rápidas, mas considere um aviso de manutenção
3. **Reversão**: Se algo der errado, você pode reverter usando o backup
4. **Verificação**: Sempre teste a funcionalidade após aplicar as migrações

---

## 🆘 Troubleshooting

### Se o erro persistir:

```bash
# Verifique os logs do Django
python3 manage.py runserver  # Veja os logs no terminal

# Ou check logs do container
docker logs <container-id>
```

### Se a migração falhar:

```bash
# Ver detalhes do erro
python3 manage.py migrate --verbosity 3

# Forçar aplicação (use com cuidado)
python3 manage.py migrate --fake-initial
```

### Se aparecer "migration conflict":

```bash
# Merge migrations
python3 manage.py makemigrations --merge
```

---

## ✨ Resultado Esperado

Após aplicar as migrações, o modelo `BrandingSettings` terá apenas os campos:
- ✅ `background_color` (Cor de Fundo)
- ✅ `text_color` (Cor de Texto)
- ✅ `button_color_primary` (Cor do Botão)
- ✅ `button_text_color` (Cor de Texto do Botão)

Os campos antigos foram removidos:
- ❌ `button_color_secondary` (removido)
- ❌ `use_gradient_buttons` (removido)
- ❌ `highlight_color` (removido)

---

## 📞 Precisa de Ajuda?

Se encontrar problemas:
1. Verifique os logs do container
2. Confirme que está no diretório correto (`/app/src`)
3. Verifique se o Python está usando o ambiente virtual correto
4. Confirme as credenciais do banco de dados

---

**Data de Criação**: 04/12/2025  
**Última Atualização**: 04/12/2025
