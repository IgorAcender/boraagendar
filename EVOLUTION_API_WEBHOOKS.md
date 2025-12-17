# Evolution API - Webhooks e Eventos

Documentação oficial: https://doc.evolution-api.com/v1/pt/env

## Variáveis de Ambiente Importantes

### Webhook Global
```
WEBHOOK_GLOBAL_URL          # URL que receberá as requisições de webhook
WEBHOOK_GLOBAL_ENABLED      # Se os webhooks estão habilitados (true ou false)
WEBHOOK_GLOBAL_WEBHOOK_BY_EVENTS  # Habilita webhooks por eventos específicos
```

### Eventos de Webhook Disponíveis

#### Conexão
- `WEBHOOK_EVENTS_CONNECTION_UPDATE` ⭐ **Envia eventos de Atualização de Conexão**
- `WEBHOOK_EVENTS_QRCODE_UPDATED` ⭐ **Envia eventos de Atualização do QR Code**

#### Mensagens
- `WEBHOOK_EVENTS_MESSAGES_SET` - Envia eventos de Criação de Mensagens (recuperação)
- `WEBHOOK_EVENTS_MESSAGES_UPSERT` - Envia eventos de Recebimento de Mensagens
- `WEBHOOK_EVENTS_MESSAGES_UPDATE` - Envia eventos de Atualização de Mensagens
- `WEBHOOK_EVENTS_MESSAGES_DELETE` - Envia eventos de Deleção de Mensagens
- `WEBHOOK_EVENTS_SEND_MESSAGE` - Envia eventos de Envio de Mensagens

#### Contatos
- `WEBHOOK_EVENTS_CONTACTS_SET` - Envia eventos de Criação de Contatos
- `WEBHOOK_EVENTS_CONTACTS_UPSERT` - Envia eventos de Atualização/Criação de Contatos
- `WEBHOOK_EVENTS_CONTACTS_UPDATE` - Envia eventos de Atualização de Contatos

#### Conversas
- `WEBHOOK_EVENTS_CHATS_SET` - Envia eventos de Criação de Conversas
- `WEBHOOK_EVENTS_CHATS_UPSERT` - Envia eventos de Criação/Atualização de Conversas
- `WEBHOOK_EVENTS_CHATS_UPDATE` - Envia eventos de Atualização de Conversas
- `WEBHOOK_EVENTS_CHATS_DELETE` - Envia eventos de Deleção de Conversas

#### Grupos
- `WEBHOOK_EVENTS_GROUPS_UPSERT` - Envia eventos de Criação de Grupos
- `WEBHOOK_EVENTS_GROUPS_UPDATE` - Envia eventos de Atualização de Grupos
- `WEBHOOK_EVENTS_GROUP_PARTICIPANTS_UPDATE` - Envia eventos de Atualização de Participantes

#### Outros
- `WEBHOOK_EVENTS_PRESENCE_UPDATE` - Envia eventos de Atualização de presença ("digitando…" ou "gravando…")
- `WEBHOOK_EVENTS_LABELS_EDIT` - Envia eventos de Edição de Etiquetas
- `WEBHOOK_EVENTS_LABELS_ASSOCIATION` - Envia eventos de Associação de Etiquetas
- `WEBHOOK_EVENTS_CALL` - Envia eventos de Chamadas
- `WEBHOOK_EVENTS_APPLICATION_STARTUP` - Envia evento na inicialização do app
- `WEBHOOK_EVENTS_NEW_JWT_TOKEN` - Envia eventos de novo token JWT
- `WEBHOOK_EVENTS_ERRORS` - Envia eventos de Erros
- `WEBHOOK_EVENTS_ERRORS_WEBHOOK` - Envia eventos de Erros em Webhooks
- `WEBHOOK_EVENTS_TYPEBOT_START` - Envia eventos de Início de fluxo do Typebot
- `WEBHOOK_EVENTS_TYPEBOT_CHANGE_STATUS` - Envia eventos de Atualização no status do Typebot
- `WEBHOOK_EVENTS_CHAMA_AI_ACTION` - Envia eventos de Ações de IA

### RabbitMQ (Alternativa)
Se usar RabbitMQ, também tem os mesmos eventos com prefixo `RABBITMQ_EVENTS_`:
```
RABBITMQ_ENABLED            # Habilita RabbitMQ (true ou false)
RABBITMQ_GLOBAL_ENABLED     # Habilita RabbitMQ de forma global (true ou false)
RABBITMQ_URI                # URI: amqp://guest:guest@rabbitmq:5672
RABBITMQ_EXCHANGE_NAME      # Nome do exchange (padrão: evolution_exchange)
```

### WebSocket
```
WEBSOCKET_ENABLED           # Habilitar ou não o WebSocket (true)
WEBSOCKET_GLOBAL_EVENTS     # Habilita os WebSocket de forma global (true)
```

## Fluxo de Conexão WhatsApp

### Estados Possíveis
1. **"qr"** - QR code foi gerado, aguardando scan
2. **"connecting"** - QR foi escaneado, tentando conectar
3. **"connected"** - Conectado com sucesso ✅
4. **"disconnected"** - Desconectado
5. **"error"** - Erro na conexão

## Como Implementar no Bora Agendar

### Webhook Handler (Django)
Local: `/src/scheduling/views/whatsapp_manager.py` (função `whatsapp_webhook_update`)

URL: `/dashboard/whatsapp/webhook/update/`

O webhook recebe POST com:
```json
{
  "instance_id": "seu_id",
  "phone_number": "seu_numero",
  "status": "connected|disconnected|connecting|error",
  "session_id": "xxx",
  "error_message": "..."
}
```

### Para Ativar os Webhooks

Na Evolution API, configurar as variáveis de ambiente:

```bash
# Ativar webhooks
WEBHOOK_GLOBAL_ENABLED=true
WEBHOOK_GLOBAL_URL=https://seu-dominio.com/dashboard/whatsapp/webhook/update/

# Ativar eventos específicos
WEBHOOK_EVENTS_CONNECTION_UPDATE=true
WEBHOOK_EVENTS_QRCODE_UPDATED=true
```

### Fluxo de Auto-Close do Modal

1. Usuário clica "Novo QR"
2. JavaScript abre modal e chama `/dashboard/whatsapp/criar/`
3. Evolution API gera QR e começa a monitorar
4. Usuário escaneia QR com WhatsApp
5. **Evolution API envia webhook** para `/dashboard/whatsapp/webhook/update/`
6. Django atualiza status no banco
7. **JavaScript monitora mudanças** e fecha modal automaticamente

### Opções de Monitoramento em Tempo Real

#### Opção 1: Polling (Atual)
- JavaScript faz requisições a cada 1 segundo
- Simples, sem necessidade de configuração extra
- Menos eficiente

#### Opção 2: Webhook + localStorage
- Evolution API envia webhook
- Django atualiza localStorage via resposta
- JavaScript monitora localStorage
- Mais eficiente, mais rápido

#### Opção 3: WebSocket
- Conexão bidirecional em tempo real
- Evolution API suporta via `WEBSOCKET_ENABLED=true`
- Ideal para aplicações em tempo real

#### Opção 4: RabbitMQ
- Broker de mensagens
- Ideal para arquiteturas distribuídas
- Mais complexo de configurar

## Próximos Passos

1. ✅ Verificar se Evolution API tem `WEBHOOK_GLOBAL_ENABLED=true`
2. ✅ Verificar URL do webhook em `WEBHOOK_GLOBAL_URL`
3. ✅ Ativar `WEBHOOK_EVENTS_CONNECTION_UPDATE=true`
4. ✅ Testar enviando QR code e monitorando logs do Django
5. ⏳ Melhorar frontend para detectar webhook em tempo real

## Referências

- Documentação completa: https://doc.evolution-api.com/v1/pt/env
- Repositório oficial: https://github.com/EvolutionAPI/evolution-api
- Arquivo .env exemplo: https://github.com/EvolutionAPI/evolution-api/blob/main/Docker/.env.example
