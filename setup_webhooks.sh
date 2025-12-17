#!/bin/bash

# Script para configurar webhooks no Evolution API
# Execute este script para ativar webhooks automáticos

echo "🔧 Configurando Webhooks no Evolution API..."

# Carregar variáveis do .env
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Verificar se as variáveis estão configuradas
if [ -z "$EVOLUTION_API_URL" ] || [ -z "$EVOLUTION_API_KEY" ]; then
    echo "❌ ERRO: Configure EVOLUTION_API_URL e EVOLUTION_API_KEY no .env"
    exit 1
fi

echo "📍 URL: $EVOLUTION_API_URL"
echo "🔑 Key: ${EVOLUTION_API_KEY:0:10}..."

# URL do webhook (ajuste para produção)
WEBHOOK_URL="http://localhost:8000/dashboard/whatsapp/webhook/update/"

echo "🎯 Webhook URL: $WEBHOOK_URL"

# 1. Configurar webhook global
echo "📡 Configurando webhook global..."
curl -X POST "$EVOLUTION_API_URL/settings/set" \
  -H "Content-Type: application/json" \
  -H "apikey: $EVOLUTION_API_KEY" \
  -d "{
    \"webhook\": {
      \"global\": {
        \"url\": \"$WEBHOOK_URL\",
        \"enabled\": true,
        \"webhook_by_events\": true
      }
    }
  }" 2>/dev/null | jq . 2>/dev/null || echo "Resposta recebida"

# 2. Ativar eventos de conexão
echo "🔗 Ativando eventos de conexão..."
curl -X POST "$EVOLUTION_API_URL/settings/set" \
  -H "Content-Type: application/json" \
  -H "apikey: $EVOLUTION_API_KEY" \
  -d "{
    \"webhook\": {
      \"events\": {
        \"connection_update\": true,
        \"qrcode_updated\": true
      }
    }
  }" 2>/dev/null | jq . 2>/dev/null || echo "Resposta recebida"

# 3. Verificar configurações
echo "🔍 Verificando configurações..."
curl -X GET "$EVOLUTION_API_URL/settings" \
  -H "apikey: $EVOLUTION_API_KEY" 2>/dev/null | jq '.webhook' 2>/dev/null || echo "Verificação concluída"

echo "✅ Webhooks configurados!"
echo ""
echo "📋 Para testar:"
echo "1. Acesse o dashboard WhatsApp"
echo "2. Clique em 'Novo QR'"
echo "3. Escaneie o QR code"
echo "4. O modal deve fechar automaticamente quando conectar"
echo ""
echo "🔧 Se não funcionar, verifique os logs do Django:"
echo "tail -f logs/django.log | grep webhook"</content>
<parameter name="filePath">/Users/user/Desktop/Programação/boraagendar/setup_webhooks.sh