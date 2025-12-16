# 🚀 SOLUÇÃO: QR Code do WhatsApp não aparecia

## 📋 O Problema
O modal abria, mas ficava com o spinner de carregamento infinito e nunca mostrava o QR code.

## 🔍 Causa Raiz
**Não havia nenhuma `EvolutionAPI` cadastrada no banco de dados!**

Quando você clicava em "Conectar WhatsApp", a view tentava buscar:
```python
evolution_api = EvolutionAPI.objects.filter(
    is_active=True
).first()

if not evolution_api:
    return JsonResponse({
        'success': False,
        'error': 'Nenhum Evolution API disponível. Entre em contato com o suporte.'
    }, status=400)
```

Como não havia nenhuma, retornava erro 400 e o modal ficava com mensagem de erro (que você talvez não tenha visto).

## ✅ SOLUÇÃO

### Opção 1: Pelo Django Shell (Rápido)

```bash
cd /Users/user/Desktop/Programação/boraagendar

python3 << 'EOF'
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
django.setup()

from scheduling.models import EvolutionAPI

evo = EvolutionAPI.objects.create(
    instance_id='default',
    api_url='http://localhost:8080/api',
    api_key='sua-chave-aqui',
    is_active=True,
    capacity=10,
    priority=1
)
print(f'✅ Evolution API criada: {evo.id}')
EOF
```

### Opção 2: Pelo Script (Mais Fácil)

```bash
chmod +x setup_evolution_api_simple.sh
./setup_evolution_api_simple.sh
```

### Opção 3: Verificar Primeiro

```bash
python3 check_evolution_api.py
```

Isso mostra todas as Evolution APIs e cria uma se não existir.

## 🔧 Configuração da Evolution API

Você precisa ter:

1. **Instance ID** - Nome único da sua instância Evolution
   - Exemplo: `default`, `rifas-whatsapp`, `bora-agendar-1`

2. **API URL** - URL do servidor Evolution API
   - Exemplo: `http://localhost:8080/api`
   - Ou: `https://seu-dominio.com/api`

3. **API Key** - Chave de autenticação
   - Você obtém isso do painel da Evolution API

## 🧪 Testando

Após criar a Evolution API:

1. Volte ao dashboard
2. Clique em "Conectar WhatsApp"
3. Agora o QR code deve aparecer! 🎉

## 📝 Notas

- A `capacity` é quantos WhatsApps podem conectar nessa instância
- A `priority` é usada quando há várias Evolution APIs - a com menor número é usada primeiro
- Se não tiver uma Evolution API rodando, você pode usar `http://localhost:8080/api` (local) ou configurar com uma real

## 🔗 Próximos Passos

1. Após conectar um WhatsApp, configure-o para receber mensagens
2. Defina qual é o WhatsApp principal (⭐ Principal)
3. Configure os agendamentos para enviar confirmações por WhatsApp

---

**Criado em:** 15 de dezembro de 2025
**Problema:** QR code não aparecia no modal
**Solução:** Criar Evolution API no banco de dados
