#!/bin/bash
# 🚀 EXECUTE ESTE COMANDO NO TERMINAL DO EASYPANEL
# 
# Passo a passo:
# 1. Abra o EasyPanel
# 2. Acesse seu projeto
# 3. Abra o Terminal/Console
# 4. Cole e execute o comando abaixo:

cd /app/src && python3 manage.py migrate && python3 manage.py showmigrations tenants

# OU execute o script completo:
# bash /app/apply_migrations.sh

# ✅ Isso irá:
# - Aplicar todas as migrações pendentes
# - Corrigir o erro 500 na aba "Cores e Marca"
# - Mostrar o status das migrações do app tenants

# 📝 Resultado esperado:
# Operations to perform:
#   Apply all migrations: ...
# Running migrations:
#   Applying tenants.0015_remove_old_branding_fields... OK
#   Applying tenants.0016_alter_brandingsettings_button_color_primary_and_more... OK
#   Applying raffles.0001_initial... OK
