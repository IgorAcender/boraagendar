# 🔧 Correção do Erro 500 no Reagendamento - EasyPanel

## Problema Identificado
O erro 500 ocorre porque o template `reschedule_booking.html` precisa da variável `today` no contexto, mas ela não está sendo passada pela view.

## Solução Aplicada Localmente
Adicionamos a variável `today` ao contexto da view `reschedule_booking`.

## 📋 Passos para Aplicar no EasyPanel

### Opção 1: Deploy via Git (RECOMENDADO)

1. **Commit e Push das alterações:**
   ```bash
   cd /Users/user/Desktop/Programação/boraagendar
   git add src/scheduling/views/public.py
   git commit -m "fix: adiciona variável today ao contexto de reagendamento"
   git push origin main
   ```

2. **No EasyPanel:**
   - Vá para seu projeto
   - Clique em "Deploy"
   - Aguarde o deploy terminar
   - Teste o reagendamento novamente

### Opção 2: Edição Manual no Terminal do EasyPanel

Se você não usa Git ou precisa de uma correção imediata:

1. **Abra o Terminal no EasyPanel**
2. **Execute:**
   ```bash
   # Navegue para o diretório correto
   cd /app/src/scheduling/views
   
   # Faça backup do arquivo
   cp public.py public.py.backup
   
   # Edite o arquivo
   nano public.py
   ```

3. **Procure pela linha (aproximadamente linha 1016):**
   ```python
   branding = tenant.branding if hasattr(tenant, 'branding') else None
   
   return render(request, 'scheduling/public/reschedule_booking.html', {
   ```

4. **Adicione ANTES do `return render`:**
   ```python
   # Data atual para o calendário
   today = timezone.now().date()
   ```

5. **Adicione ao dicionário do contexto:**
   ```python
   return render(request, 'scheduling/public/reschedule_booking.html', {
       'tenant': tenant,
       'booking': booking,
       'policy': policy,
       'branding': branding,
       'available_professionals': available_professionals,
       'has_auto_assign_professionals': has_auto_assign,
       'today': today,  # <- ADICIONE ESTA LINHA
   })
   ```

6. **Salve e reinicie o serviço:**
   ```bash
   # Ctrl+X para sair do nano
   # Y para confirmar
   # Enter para salvar
   
   # Reinicie o Gunicorn/uWSGI
   supervisorctl restart all
   # OU
   systemctl restart gunicorn
   # OU use o botão "Restart" no EasyPanel
   ```

### Opção 3: Ver os Logs para Confirmar

```bash
# Ver os últimos erros
tail -n 100 /var/log/gunicorn/error.log

# OU logs do Django
tail -n 100 /app/logs/django.log

# Ver logs em tempo real
tail -f /var/log/gunicorn/error.log
```

## ✅ Como Testar

1. Faça login como cliente
2. Vá para "Meus Agendamentos"
3. Clique em "Reagendar" em um agendamento
4. A página deve carregar sem erro 500
5. O calendário deve aparecer funcionando

## 🐛 Se Ainda der Erro 500

Execute no terminal do EasyPanel:

```bash
cd /app/src
python3 manage.py shell << 'EOF'
from scheduling.models import Booking
from tenants.models import Tenant

# Teste se há bookings com problemas
problematic = []
for booking in Booking.objects.all()[:10]:
    try:
        _ = booking.service.name
        if booking.professional:
            _ = booking.professional.display_name
    except Exception as e:
        problematic.append((booking.id, str(e)))
        
print(f"Bookings problemáticos: {problematic}")
EOF
```

Isso vai ajudar a identificar se há algum booking com dados corrompidos.

## 📝 Alteração Feita

**Arquivo:** `src/scheduling/views/public.py`
**Função:** `reschedule_booking` (linha ~1016)
**Mudança:** Adicionou `today = timezone.now().date()` e incluiu no contexto do template

```python
# ANTES:
branding = tenant.branding if hasattr(tenant, 'branding') else None

return render(request, 'scheduling/public/reschedule_booking.html', {
    'tenant': tenant,
    'booking': booking,
    'policy': policy,
    'branding': branding,
    'available_professionals': available_professionals,
    'has_auto_assign_professionals': has_auto_assign,
})

# DEPOIS:
branding = tenant.branding if hasattr(tenant, 'branding') else None

# Data atual para o calendário
today = timezone.now().date()

return render(request, 'scheduling/public/reschedule_booking.html', {
    'tenant': tenant,
    'booking': booking,
    'policy': policy,
    'branding': branding,
    'available_professionals': available_professionals,
    'has_auto_assign_professionals': has_auto_assign,
    'today': today,
})
```
