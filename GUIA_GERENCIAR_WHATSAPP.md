# 📱 GERENCIAMENTO DE WHATSAPP - GUIA DO DONO

## 🎯 O que é?

Interface web para o dono da barbearia gerenciar seus WhatsApps conectados:

- ✅ Ver status de cada WhatsApp (conectado/desconectado)
- ✅ Gerar QR code para conectar novo WhatsApp
- ✅ Desconectar WhatsApps
- ✅ Definir WhatsApp principal (para agendamentos)
- ✅ Ver histórico de conexões
- ✅ Ver erros de conexão

---

## 🚀 COMO USAR

### 1. Acessar o Dashboard

```
URL: https://seu-dominio.com/whatsapp/
```

Você verá uma página com:
- **Estatísticas** (total, conectados, desconectados)
- **Cards dos WhatsApps** com status e ações

---

### 2. Conectar um Novo WhatsApp

#### Passo A: Gerar QR Code

```
1. Na página de gerenciamento, clique em "🔗 Gerar QR Code"
2. Uma modal abrirá com o QR code
3. O QR code expira em 5 minutos
```

#### Passo B: Apontar Câmera

```
1. Abra WhatsApp no seu celular
2. Vá para: Configurações → Aparelhos Conectados → Conectar Dispositivo
3. Aponte a câmera para o QR code
4. Confirme no celular
```

#### Passo C: Validação

```
✅ Status muda para "⏳ Conectando..."
✅ Depois para "✅ Conectado e Pronto"
✅ Pronto para receber agendamentos!
```

---

### 3. Definir WhatsApp Principal

Se você tem mais de 1 WhatsApp conectado:

```
1. No card do WhatsApp, clique em "⭐ Definir como Principal"
2. Este WhatsApp receberá as mensagens de agendamentos
3. Apenas 1 pode ser principal por vez
```

---

### 4. Desconectar um WhatsApp

Se precisar desconectar (ex: resetar o celular):

```
1. No card, clique em "❌ Desconectar"
2. Confirme a ação
3. Status muda para "❌ Desconectado"
4. Você pode reconectar depois gerando um novo QR code
```

---

### 5. Ver Detalhes

Para informações mais detalhadas:

```
1. Clique em "📋 Detalhes" no card
2. Veja:
   - Status da conexão
   - Session ID
   - Data de conexão
   - Erros (se houver)
```

---

## 📊 Entender os Status

| Status | Significado | O que fazer |
|--------|-------------|------------|
| 📋 Aguardando QR Code | Nunca foi conectado | Gerar QR code |
| ⏳ Conectando... | Esperando confirmação | Apontar câmera para QR code |
| ✅ Conectado e Pronto | Pronto para usar! | Nada, está funcionando |
| ❌ Desconectado | Foi desconectado | Gerar novo QR code se quiser reconectar |
| ⚠️ Erro na Conexão | Algo deu errado | Ver mensagem de erro e tentar novamente |

---

## 🔐 Segurança

**O QR code:**
- Expira em 5 minutos
- É exclusivo para aquele WhatsApp
- Não pode ser reutilizado
- Gerar um novo automaticamente invalida o anterior

---

## 🆘 TROUBLESHOOTING

### "QR code não funciona"

1. Verifique se a câmera do celular está funcionando
2. Verifique luz (pode estar muito escuro)
3. Tente gerar um novo QR code (o antigo pode ter expirado)

### "Conectou mas continua como pending"

1. Aguarde 10 segundos para atualizar
2. Recarregue a página (F5)
3. Se continuar, desconecte e tente novamente

### "Mensagens não estão sendo enviadas"

1. Verifique se o WhatsApp está como principal (⭐)
2. Verifique se está conectado (✅)
3. Verifique se o WhatsApp está ativo no celular
4. Verifique conexão de internet

### "Erro: Evolution API indisponível"

1. Aguarde alguns segundos
2. Tente novamente
3. Se persistir, contate suporte

---

## 📱 Ter Múltiplos WhatsApps

Você pode ter vários WhatsApps conectados:

```
Exemplo:
- WhatsApp 1: +55 11 9 9999-0001 (Principal ⭐)
- WhatsApp 2: +55 11 9 9999-0002 (Backup)
- WhatsApp 3: +55 11 9 9999-0003 (Suporte)

Apenas o Principal (⭐) recebe as mensagens de agendamento
```

---

## 🔗 Integração com Agendamentos

Uma vez conectado:

```
1. Cliente cria agendamento no site
2. Sistema automaticamente:
   - Seleciona o WhatsApp Principal ⭐
   - Envia mensagem de confirmação
   - Cliente recebe no telefone ✅
```

Não precisa fazer nada! É automático!

---

## 📞 Menu Rápido

| Ação | URL | Método |
|------|-----|--------|
| Dashboard | `/whatsapp/` | GET |
| Detalhes | `/whatsapp/{id}/` | GET |
| Gerar QR | `/whatsapp/{id}/gerar-qrcode/` | POST |
| Desconectar | `/whatsapp/{id}/desconectar/` | POST |
| Principal | `/whatsapp/{id}/set-primary/` | POST |
| Status API | `/whatsapp/{id}/status/` | GET |
| Lista API | `/whatsapp/list/api/` | GET |

---

## ✨ DICAS PRO

1. **Mantenha sempre um conectado** - Se um cair, tenha um backup
2. **Defina uma senha forte** - Use PIN no WhatsApp Web
3. **Monitore a conexão** - Verifique o dashboard regularmente
4. **Teste antes de usar** - Gere um agendamento de teste

---

## 🎉 Pronto!

Seu WhatsApp está gerenciado e pronto para enviar mensagens de confirmação automaticamente! 🚀

Qualquer dúvida, consulte este guia ou contate suporte.
