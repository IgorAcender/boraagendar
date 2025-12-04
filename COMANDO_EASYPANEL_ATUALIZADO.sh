#!/bin/bash
# 🚀 COMANDO ATUALIZADO PARA EASYPANEL
# 
# Execute este comando no terminal do EasyPanel:

# Primeiro, veja onde você está:
pwd

# Liste os arquivos para encontrar o manage.py:
ls -la

# Se manage.py estiver na raiz /app, execute:
cd /app && python3 manage.py migrate

# Se manage.py estiver em outro lugar, ajuste o caminho
# Exemplo: cd /app/src && python3 manage.py migrate

# ✅ Depois de executar, verifique o status:
python3 manage.py showmigrations tenants
