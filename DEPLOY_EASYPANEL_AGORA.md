# 🚨 ERRO 500 NO REAGENDAMENTO - SOLUÇÃO RÁPIDA

## ⚡ STATUS ATUAL
✅ Código corrigido localmente  
✅ Commit feito no Git  
✅ Push realizado para origin/main  
⏳ **FALTA: Deploy no EasyPanel**

## 🎯 O QUE FAZER AGORA

### OPÇÃO 1: Deploy Automático (RECOMENDADO)

1. Acesse: https://app.easypanel.io
2. Selecione seu projeto **boraagendar**
3. Clique em **"Deploy"** ou **"Rebuild"**
4. Aguarde 2-5 minutos
5. Teste: acesse um agendamento e clique em "Reagendar"

### OPÇÃO 2: Verificar Logs (se ainda der erro)

No terminal do EasyPanel:
```bash
# Ver últimos erros
tail -n 100 /var/log/gunicorn/error.log

# OU logs do Docker
docker logs --tail 100 $(docker ps -q --filter name=boraagendar)
```

### OPÇÃO 3: Executar Script de Teste

No terminal do EasyPanel:
```bash
# Copie o script test_reschedule_fix.sh para /app/
# Depois execute:
bash /app/test_reschedule_fix.sh
```

## 🔧 O QUE FOI CORRIGIDO

**Arquivo:** `src/scheduling/views/public.py`  
**Linha:** ~1016  
**Mudança:** Adicionada variável `today` ao contexto

```python
# ANTES (causava erro 500):
return render(request, 'scheduling/public/reschedule_booking.html', {
    'tenant': tenant,
    'booking': booking,
    'policy': policy,
    'branding': branding,
    'available_professionals': available_professionals,
    'has_auto_assign_professionals': has_auto_assign,
})

# DEPOIS (corrigido):
today = timezone.now().date()

return render(request, 'scheduling/public/reschedule_booking.html', {
    'tenant': tenant,
    'booking': booking,
    'policy': policy,
    'branding': branding,
    'available_professionals': available_professionals,
    'has_auto_assign_professionals': has_auto_assign,
    'today': today,  # <- ADICIONADO
})
```

## 🐛 SE AINDA DER ERRO 500

Cole este comando no terminal do EasyPanel e me envie a saída:

```bash
cd /app/src && python3 manage.py shell << 'EOF'
from scheduling.models import Booking
from tenants.models import Tenant

# Buscar um booking
booking = Booking.objects.first()
if booking:
    print(f"Booking ID: {booking.id}")
    print(f"Service: {booking.service}")
    print(f"Professional: {booking.professional}")
    print(f"Scheduled: {booking.scheduled_for}")
else:
    print("Nenhum booking encontrado")
EOF
```

## 📞 PRÓXIMO PASSO
**FAÇA O DEPLOY NO EASYPANEL AGORA!**

Depois de fazer o deploy, teste acessando:
- Login como cliente
- Meus Agendamentos
- Clicar em "Reagendar"

Se ainda der erro, me envie:
1. Screenshot do erro
2. Logs do EasyPanel (comando acima)
