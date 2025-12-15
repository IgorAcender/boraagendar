# 🚀 INSTRUÇÕES PARA DEPLOY NO EASYPANEL

## ⚡ QUICK START (5 MINUTOS)

Se você está lendo isto, o código já foi integrado na sua máquina local. Agora você precisa:

### PASSO 1: Entrar no EasyPanel Terminal

```bash
# Abra seu terminal EasyPanel (você deve estar na pasta do projeto)
docker exec -it seu_container_django bash
```

Você deve ver o prompt mudar para algo como: `root@container:/app#`

### PASSO 2: Aplicar a Migration

```bash
# Dentro do container
python manage.py migrate
```

**Esperado:**
```
Running migrations:
  Applying scheduling.0011_whatsappinstance_connected_at
  Applying scheduling.0011_whatsappinstance_connection_code
  ... (8 migrations)
  
  Success!
```

### PASSO 3: Reiniciar o Servidor

```bash
# Sair do container
exit

# Reiniciar o Django
docker restart seu_container_django

# Aguarde 10 segundos
sleep 10

# Verificar logs (opcional)
docker logs seu_container_django | tail -20
```

### PASSO 4: Testar Dashboard

Abra no navegador:
```
https://seu-dominio.com/dashboard/whatsapp/
```

**Você deve ver:**
- Página com título "📱 Gerenciar WhatsApps"
- Stats grid com números (0/0/0/0 é normal no início)
- Mensagem "Nenhum WhatsApp conectado ainda"
- Botão para gerenciar

---

## 🔧 TROUBLESHOOTING

### ❌ Erro: "404 Not Found"

**Solução:**
```bash
# Verificar se migration foi aplicada
docker exec -it seu_container bash
python manage.py showmigrations scheduling | grep 0011
```

Esperado: `[x] 0011_whatsappinstance_*` (com x, não espaço)

### ❌ Erro de permissão

**Solução:**
```bash
# Aplicar novamente com verbosidade
python manage.py migrate --verbosity=2

# Se der erro, verificar banco de dados
python manage.py dbshell
```

### ❌ "Dados errados" ou "Campo não existe"

**Solução:**
```bash
# Seu banco provavelmente já tem migration 0011 aplicada
# Verifique:
python manage.py migrate --list | grep scheduling
```

Se 0011 aparecer com `[x]`, está tudo bem!

---

## 📱 PARA USAR O DASHBOARD

### Como Dono de Barbearia:

1. **Acessar:**
   - Ir para: `https://seu-dominio.com/dashboard/whatsapp/`
   - Ou clicar no menu lateral

2. **Ver estatísticas:**
   - Total de WhatsApps
   - Quantos estão conectados
   - Quantos estão pendentes

3. **Conectar novo WhatsApp:**
   - Clicar em "Gerar QR Code"
   - Apontar câmera do WhatsApp
   - Confirmar

4. **Gerenciar:**
   - Ver detalhes de cada um
   - Desconectar se necessário
   - Definir WhatsApp principal

---

## 🔐 CONFIGURAÇÕES OPCIONAIS

### Configurar Webhook da Evolution API

Se você tiver Evolution API, configure:

**Em suas configurações Evolution:**
```
URL: https://seu-dominio.com/dashboard/whatsapp/webhook/update/
Método: POST
Headers:
  X-API-Key: sua_chave_secreta
```

**Em seu .env:**
```
WHATSAPP_WEBHOOK_API_KEY=sua_chave_secreta
```

Depois recarregue o servidor.

---

## ✅ CHECKLIST FINAL

- [ ] Entrei no container Docker: `docker exec -it seu_container bash`
- [ ] Apliquei migration: `python manage.py migrate`
- [ ] Saí do container: `exit`
- [ ] Reiniciei: `docker restart seu_container_django`
- [ ] Abri no navegador: `/dashboard/whatsapp/`
- [ ] Vi a página carregar
- [ ] ✅ Tudo funcionando!

---

## 📞 PRECISA DE AJUDA?

### Verificar Status do Servidor

```bash
# Ver se o container está rodando
docker ps | grep django

# Ver logs recentes
docker logs seu_container_django -f

# Ctrl+C para sair dos logs
```

### Testar Migration Manualmente

```bash
docker exec -it seu_container bash
python manage.py showmigrations scheduling
```

Procure por `0011` - deve estar marcado com `[x]`

### Rollback (Se algo der errado)

```bash
docker exec -it seu_container bash
python manage.py migrate scheduling 0010
# Volta para migration anterior
```

---

## 🎊 PARABÉNS!

Seu dashboard de WhatsApp agora está **LIVE** no ar!

Os donos de barbearia podem:
- ✅ Acessar `/dashboard/whatsapp/`
- ✅ Ver seus WhatsApps
- ✅ Gerar QR codes
- ✅ Gerenciar conexões

---

**Próximo passo:** Criar um WhatsApp de teste para validar!

```bash
docker exec -it seu_container bash
python manage.py shell

from scheduling.models import WhatsAppInstance
from tenants.models import Tenant

tenant = Tenant.objects.first()
wa = WhatsAppInstance.objects.create(
    tenant=tenant,
    phone_number="+5511999999999",
    status="pending"
)
print(f"Criado: {wa.id}")
```

Depois acesse `/dashboard/whatsapp/` e veja o WhatsApp na lista! 🎉
