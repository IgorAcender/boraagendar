#!/bin/bash
# Script para testar a API diretamente via curl

echo "🔍 Testando WhatsApp Create API"
echo "================================"

# Tentar fazer uma requisição POST simples
echo ""
echo "1️⃣ Testando acesso ao endpoint..."
curl -v -X POST http://localhost:8000/dashboard/whatsapp/criar/ \
  -H "Content-Type: application/json" \
  -d '{}' 2>&1 | head -30

echo ""
echo ""
echo "2️⃣ Testando com autenticação..."
# Você pode precisar extrair um token real
curl -v -X POST http://localhost:8000/dashboard/whatsapp/criar/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: test" \
  -d '{}' 2>&1 | head -30
