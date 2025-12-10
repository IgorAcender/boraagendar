# 🔍 DEBUG NO EASYPANEL - Comandos Diretos

Você está dentro do container! Agora execute estes comandos:

## 1️⃣ Verificar se o código está atualizado

```bash
cd /app/src/scheduling/views
grep -A 5 "today = timezone.now().date()" public.py
```

**Resultado esperado:** Deve mostrar a linha com `today = timezone.now().date()`  
**Se NÃO aparecer:** O deploy não foi feito ou o código não está atualizado

## 2️⃣ Ver logs do Django/Gunicorn

```bash
# Tentar diferentes locais de log
ls -la /var/log/
ls -la /app/logs/
ls -la /tmp/

# Ver processos rodando
ps aux | grep gunicorn
ps aux | grep django

# Ver últimas linhas do stdout/stderr
tail -100 /proc/1/fd/1
tail -100 /proc/1/fd/2
```

## 3️⃣ Testar a view manualmente no shell

```bash
cd /app/src
python3 manage.py shell << 'EOF'
from django.utils import timezone
from scheduling.models import Booking
from tenants.models import Tenant

# Pegar um booking qualquer
booking = Booking.objects.first()

if not booking:
    print("❌ NENHUM BOOKING ENCONTRADO")
else:
    print(f"✅ Booking ID: {booking.id}")
    print(f"✅ Service: {booking.service.name if booking.service else 'None'}")
    print(f"✅ Professional: {booking.professional.display_name if booking.professional else 'None'}")
    
    # Testar se hoje funciona (o que estava faltando)
    today = timezone.now().date()
    print(f"✅ Today: {today}")
    
    # Simular o contexto da view
    tenant = booking.tenant
    available_professionals = tenant.professionals.filter(is_active=True)
    print(f"✅ Professionals disponíveis: {available_professionals.count()}")
    
    print("\n🎉 TESTE PASSOU - Código está funcionando!")
EOF
```

## 4️⃣ Verificar arquivo de configuração do Gunicorn

```bash
cat /app/gunicorn.conf.py
# OU
cat /etc/gunicorn/gunicorn.conf
```

## 5️⃣ Reiniciar o serviço (após verificar)

```bash
# Se tiver supervisorctl
supervisorctl restart all

# OU se for systemd
systemctl restart gunicorn

# OU mate o processo e deixe reiniciar
pkill -HUP gunicorn
```

## 6️⃣ Verificar se DEBUG está ativado (temporariamente)

```bash
cd /app/src
grep -n "DEBUG" config/settings.py | head -20
```

## 🎯 DIAGNÓSTICO RÁPIDO

Execute tudo de uma vez:

```bash
echo "=== VERIFICANDO CÓDIGO ==="
cd /app/src/scheduling/views
grep -c "today = timezone.now().date()" public.py

echo ""
echo "=== VERIFICANDO TEMPLATE ==="
ls -lh /app/src/templates/scheduling/public/reschedule_booking.html

echo ""
echo "=== TESTANDO IMPORTS ==="
cd /app/src
python3 << 'EOF'
try:
    from scheduling.views.public import reschedule_booking
    print("✅ Import OK")
except Exception as e:
    print(f"❌ Erro: {e}")
EOF

echo ""
echo "=== PROCESSOS RODANDO ==="
ps aux | grep -E "gunicorn|django" | grep -v grep

echo ""
echo "=== ÚLTIMO RESTART ==="
ls -lt /app/ | head -5
```

## 🚨 SE AINDA DER ERRO 500

Cole a saída completa dos comandos acima e me envie!

Também tente acessar o reagendamento e depois execute:

```bash
# Ver últimas 50 linhas de qualquer log
find /app -name "*.log" -type f -exec tail -50 {} \;
find /var/log -name "*.log" -type f -exec tail -50 {} \;
```

## 📝 NOTAS

- Você está em: `/app` (container root)
- Código Django em: `/app/src`
- Se precisar editar: `nano /app/src/scheduling/views/public.py`
