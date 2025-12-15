# 🔍 REFERÊNCIA TÉCNICA - ARQUIVOS DE CÓDIGO

## 📂 LOCALIZAÇÃO DOS ARQUIVOS

```
/Users/user/Desktop/Programação/boraagendar/
├── src/
│   ├── scheduling/
│   │   ├── models.py ........................ MODIFICADO
│   │   ├── views/
│   │   │   └── whatsapp_manager.py ......... NOVO (320+ linhas)
│   │   ├── urls/
│   │   │   └── whatsapp.py ................. NOVO (8 padrões)
│   │   ├── templates/
│   │   │   └── whatsapp/
│   │   │       ├── dashboard.html .......... NOVO (350+ linhas)
│   │   │       └── detail.html ............ NOVO (150+ linhas)
│   │   └── migrations/
│   │       └── 0011_whatsappinstance_*.py .. NOVO (8 campos)
│   └── config/
│       └── urls.py ......................... PENDENTE (editar)
└── documentação/
    ├── GUIA_GERENCIAR_WHATSAPP.md
    ├── INTEGRACAO_WHATSAPP_DASHBOARD.md
    ├── RESUMO_FINAL_WHATSAPP_DASHBOARD.md
    ├── QUICK_START_WHATSAPP_DASHBOARD.md
    ├── CHECKLIST_DEPLOY_WHATSAPP_DASHBOARD.md
    ├── PASSO_A_PASSO_PRATICO.md
    ├── INDICE_WHATSAPP_DASHBOARD.md
    └── SUMARIO_VISUAL_WHATSAPP_DASHBOARD.md
```

---

## 📝 ARQUIVO 1: models.py (MODIFICADO)

### Localização
```
src/scheduling/models.py
```

### O que foi adicionado

**8 Novos campos na classe WhatsAppInstance:**

```python
# QR Code Management
qr_code = models.TextField(null=True, blank=True)
qr_code_expires_at = models.DateTimeField(null=True, blank=True)

# Session & Connection Tracking
session_id = models.CharField(max_length=255, null=True, blank=True)
connection_code = models.CharField(max_length=50, null=True, blank=True)

# Connection Lifecycle
connected_at = models.DateTimeField(null=True, blank=True)
disconnected_at = models.DateTimeField(null=True, blank=True)

# Error Tracking
error_message = models.TextField(null=True, blank=True)

# Multi-tenancy
tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, null=True)
```

**3 Novos métodos/properties:**

```python
@property
def is_connected(self):
    """Retorna True se WhatsApp está conectado"""
    return self.status == 'connected'

@property
def qr_code_is_valid(self):
    """Verifica se QR code não expirou"""
    if not self.qr_code_expires_at:
        return False
    return timezone.now() < self.qr_code_expires_at

def get_status_display_verbose(self):
    """Retorna status em português com emoji"""
    # Exemplo: "✅ Conectado e Pronto"
```

### Como usar no shell
```python
from scheduling.models import WhatsAppInstance

wa = WhatsAppInstance.objects.first()
print(wa.is_connected)  # True/False
print(wa.qr_code_is_valid)  # True/False
print(wa.get_status_display_verbose())  # "✅ Conectado"
```

---

## 📝 ARQUIVO 2: whatsapp_manager.py (NOVO - 320+ linhas)

### Localização
```
src/scheduling/views/whatsapp_manager.py
```

### 8 Views/Endpoints

#### 1. whatsapp_dashboard()
```python
@login_required
def whatsapp_dashboard(request):
    # GET /whatsapp/
    # Retorna: Template com dashboard
    # Features:
    #   - Pega tenant do usuário
    #   - Calcula stats (total, conectados, etc)
    #   - Lista todos WhatsApps
    #   - Renderiza dashboard.html
```

**Contexto retornado:**
```python
{
    'whatsapps': <QuerySet>,
    'total': 5,
    'connected': 3,
    'disconnected': 1,
    'pending': 1,
    'errors': 0
}
```

#### 2. whatsapp_detail()
```python
@login_required
def whatsapp_detail(request, id):
    # GET /whatsapp/{id}/
    # Retorna: Template com detalhes
    # Features:
    #   - Valida permissão (tenant filtering)
    #   - Mostra todas as informações
    #   - Exibe QR se pendente
    #   - Sidebar de ações
```

#### 3. whatsapp_generate_qrcode()
```python
@login_required
def whatsapp_generate_qrcode(request, id):
    # POST /whatsapp/{id}/gerar-qrcode/
    # Retorna: JSON com QR code
    # Features:
    #   - Gera QR usando `qrcode` library
    #   - Encoda em Base64
    #   - Define expiry em 5 minutos
    #   - Salva no database
    #   - Retorna JSON
```

**Response:**
```json
{
    "success": true,
    "qr_code": "data:image/png;base64,...",
    "expires_in": "5 minutes"
}
```

#### 4. whatsapp_disconnect()
```python
@login_required
def whatsapp_disconnect(request, id):
    # POST /whatsapp/{id}/desconectar/
    # Retorna: JSON resultado
    # Features:
    #   - Muda status para 'disconnected'
    #   - Limpa session_id
    #   - Registra timestamp
    #   - Retorna JSON
```

#### 5. whatsapp_set_primary()
```python
@login_required
def whatsapp_set_primary(request, id):
    # POST /whatsapp/{id}/set-primary/
    # Retorna: JSON resultado
    # Features:
    #   - Valida se conectado
    #   - Remove primary de outros
    #   - Define este como principal
    #   - Transação atômica
```

#### 6. whatsapp_status_api()
```python
@login_required
def whatsapp_status_api(request, id):
    # GET /whatsapp/{id}/status/
    # Retorna: JSON com status
    # Features:
    #   - Para polling em tempo real
    #   - Retorna status atual
    #   - Timestamps
    #   - Mensagens de erro
```

**Response:**
```json
{
    "id": 1,
    "phone_number": "+55119999999",
    "status": "connected",
    "is_primary": true,
    "connected_at": "2024-01-15 10:30:45",
    "error_message": null
}
```

#### 7. whatsapp_list_api()
```python
@login_required
def whatsapp_list_api(request):
    # GET /whatsapp/list/api/
    # Retorna: JSON com lista completa
    # Features:
    #   - Para JavaScript bulk operations
    #   - Lista leve
    #   - Todos os status
```

#### 8. whatsapp_webhook_update()
```python
def whatsapp_webhook_update(request):
    # POST /whatsapp/webhook/update/
    # Recebe: Webhook da Evolution API
    # Features:
    #   - Valida X-API-Key header
    #   - Atualiza status do WhatsApp
    #   - Registra timestamps
    #   - Salva session_id
    #   - Registra erros
```

**Payload esperado:**
```json
{
    "instance": "instance_name",
    "status": "connected",
    "session_id": "SESSION123",
    "error_message": null
}
```

### Imports Necessários
```python
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, F
from django.utils import timezone
import qrcode
import base64
from io import BytesIO
```

### Segurança Implementada
- ✅ @login_required em todas as views
- ✅ Tenant filtering em todas as queries
- ✅ CSRF protection em POSTs
- ✅ API key validation no webhook
- ✅ Try/catch com error handling

---

## 📝 ARQUIVO 3: whatsapp.py URLs (NOVO - 8 padrões)

### Localização
```
src/scheduling/urls/whatsapp.py
```

### 8 URL Patterns

```python
from django.urls import path
from . import views

app_name = 'whatsapp'

urlpatterns = [
    # Dashboard & Detail
    path('', views.whatsapp_dashboard, name='dashboard'),
    path('<int:id>/', views.whatsapp_detail, name='detail'),
    
    # Actions
    path('<int:id>/gerar-qrcode/', views.whatsapp_generate_qrcode, name='generate_qr'),
    path('<int:id>/desconectar/', views.whatsapp_disconnect, name='disconnect'),
    path('<int:id>/set-primary/', views.whatsapp_set_primary, name='set_primary'),
    
    # APIs
    path('<int:id>/status/', views.whatsapp_status_api, name='status_api'),
    path('list/api/', views.whatsapp_list_api, name='list_api'),
    
    # Webhook
    path('webhook/update/', views.whatsapp_webhook_update, name='webhook'),
]
```

### Como usar em templates
```html
<!-- Link direto -->
<a href="{% url 'whatsapp:dashboard' %}">Dashboard</a>

<!-- Com parâmetro -->
<a href="{% url 'whatsapp:detail' wa.id %}">Ver Detalhes</a>

<!-- Em JavaScript -->
const url = "{% url 'whatsapp:status_api' wa.id %}";
```

### Inclusão em config/urls.py
```python
# Em config/urls.py
from scheduling.urls import whatsapp as whatsapp_urls

urlpatterns = [
    path('whatsapp/', include(whatsapp_urls)),
    # ... rest
]
```

---

## 📝 ARQUIVO 4: dashboard.html (NOVO - 350+ linhas)

### Localização
```
src/scheduling/templates/whatsapp/dashboard.html
```

### Estrutura HTML

**Header:**
```html
<h1>📱 Gerenciar WhatsApps</h1>
<p>Conecte seus WhatsApps para receber confirmações...</p>
```

**Stats Grid:**
```html
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value">{{ total }}</div>
        <div class="stat-label">Total</div>
    </div>
    <!-- Conectados, Desconectados, Pendentes -->
</div>
```

**WhatsApp Cards:**
```html
<div class="whatsapp-grid">
    {% for wa in whatsapps %}
    <div class="whatsapp-card">
        <div class="wa-header">
            <h3>{{ wa.phone_number }}</h3>
            {% if wa.is_primary %}<span class="primary-badge">⭐ Principal</span>{% endif %}
        </div>
        <div class="wa-status">
            <span class="status-badge {{ wa.status }}">{{ wa.get_status_display_verbose }}</span>
        </div>
        <div class="wa-info">
            {% if wa.connected_at %}
            <p>Conectado em: {{ wa.connected_at|date:"d/m/Y H:i" }}</p>
            {% endif %}
            {% if wa.error_message %}
            <p class="error">{{ wa.error_message }}</p>
            {% endif %}
        </div>
        <div class="wa-actions">
            <button onclick="generateQrCode({{ wa.id }})">🔗 Gerar QR Code</button>
            <button onclick="disconnect({{ wa.id }})">❌ Desconectar</button>
            {% if wa.is_connected %}
            <button onclick="setPrimary({{ wa.id }})">⭐ Definir como Principal</button>
            {% endif %}
            <a href="{% url 'whatsapp:detail' wa.id %}" class="btn-secondary">📋 Detalhes</a>
        </div>
    </div>
    {% endfor %}
</div>
```

**QR Code Modal:**
```html
<div id="qr-modal" class="modal">
    <div class="modal-content">
        <h2>Escanear com WhatsApp Web</h2>
        <img id="qr-image" src="" alt="QR Code">
        <p id="qr-expiry"></p>
        <button onclick="closeQrModal()">X Fechar</button>
    </div>
</div>
```

### CSS Styles
```css
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
}

.whatsapp-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

.whatsapp-card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.status-badge {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 500;
}

.status-badge.connected {
    background: #d4edda;
    color: #155724;
}

.status-badge.pending {
    background: #fff3cd;
    color: #856404;
}

.status-badge.disconnected {
    background: #f8d7da;
    color: #721c24;
}
```

### JavaScript Functions

```javascript
function generateQrCode(id) {
    fetch(`/whatsapp/${id}/gerar-qrcode/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(r => r.json())
    .then(data => {
        document.getElementById('qr-image').src = data.qr_code;
        document.getElementById('qr-modal').style.display = 'block';
    });
}

function disconnect(id) {
    if (confirm('Desconectar este WhatsApp?')) {
        fetch(`/whatsapp/${id}/desconectar/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(() => location.reload());
    }
}

function setPrimary(id) {
    fetch(`/whatsapp/${id}/set-primary/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(() => location.reload());
}

// Auto-refresh a cada 5 segundos
setInterval(() => {
    location.reload();
}, 5000);
```

---

## 📝 ARQUIVO 5: detail.html (NOVO - 150+ linhas)

### Localização
```
src/scheduling/templates/whatsapp/detail.html
```

### Estrutura

**Breadcrumb:**
```html
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li><a href="{% url 'whatsapp:dashboard' %}">WhatsApps</a></li>
        <li class="active">{{ whatsapp.phone_number }}</li>
    </ol>
</nav>
```

**Status Card:**
```html
<div class="status-card">
    <div class="status-display">
        <span class="status-badge {{ whatsapp.status }}">{{ whatsapp.get_status_display_verbose }}</span>
    </div>
    <div class="status-info">
        <p><strong>Session ID:</strong> {{ whatsapp.session_id }}</p>
        <p><strong>Conectado em:</strong> {{ whatsapp.connected_at|date:"d/m/Y H:i:s" }}</p>
        <p><strong>Desconectado em:</strong> {{ whatsapp.disconnected_at|date:"d/m/Y H:i:s" }}</p>
    </div>
</div>
```

**QR Code Section:**
```html
{% if whatsapp.qr_code and whatsapp.qr_code_is_valid %}
<div class="qr-section">
    <h3>QR Code</h3>
    <img src="{{ whatsapp.qr_code }}" alt="QR Code" class="qr-image">
    <p>Válido até: {{ whatsapp.qr_code_expires_at|date:"H:i:s" }}</p>
</div>
{% endif %}
```

**Actions Sidebar:**
```html
<aside class="actions-sidebar">
    <h3>Ações</h3>
    <button onclick="generateQrCode({{ whatsapp.id }})">🔗 Gerar QR Code</button>
    {% if whatsapp.is_connected %}
    <button onclick="setPrimary({{ whatsapp.id }})">⭐ Definir como Principal</button>
    {% endif %}
    <button onclick="disconnect({{ whatsapp.id }})">❌ Desconectar</button>
</aside>
```

---

## 📝 ARQUIVO 6: Migration 0011_whatsappinstance_*.py (NOVO)

### Localização
```
src/scheduling/migrations/0011_whatsappinstance_*.py
```

### O que faz

Adiciona 8 colunas ao banco de dados:

```python
migrations.AddField(
    model_name='whatsappinstance',
    name='qr_code',
    field=models.TextField(blank=True, null=True),
),
migrations.AddField(
    model_name='whatsappinstance',
    name='qr_code_expires_at',
    field=models.DateTimeField(blank=True, null=True),
),
# ... (mais 6 campos)
migrations.AddField(
    model_name='whatsappinstance',
    name='tenant',
    field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.tenant'),
),
```

### Como aplicar

```bash
# Local
cd src
python manage.py migrate

# EasyPanel
docker exec -it seu_container bash
python manage.py migrate
```

### Verificar aplicação

```bash
python manage.py showmigrations scheduling | grep 0011
# Esperado: [x] 0011_whatsappinstance_...
```

---

## 🔧 CONFIG/URLS.PY (PENDENTE)

### Localização
```
src/config/urls.py
```

### O que adicionar

**Import (no topo):**
```python
from scheduling.urls import whatsapp as whatsapp_urls
```

**URL Pattern (em urlpatterns):**
```python
path('whatsapp/', include(whatsapp_urls)),
```

### Exemplo completo após edição

```python
from django.contrib import admin
from django.urls import path, include
from scheduling.urls import whatsapp as whatsapp_urls

urlpatterns = [
    path('whatsapp/', include(whatsapp_urls)),
    path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls')),
    # ... rest das rotas
]
```

---

## 📊 RESUMO DE LINHAS DE CÓDIGO

| Arquivo | Linhas | Tipo | Status |
|---------|--------|------|--------|
| models.py | +50 | Python | Modificado |
| whatsapp_manager.py | 320+ | Python | Novo |
| whatsapp.py | 30 | Python | Novo |
| dashboard.html | 350+ | HTML/CSS/JS | Novo |
| detail.html | 150+ | HTML/JS | Novo |
| 0011_migration.py | 50+ | Python | Novo |
| **TOTAL** | **~1000** | **Misto** | **Pronto** |

---

## 🔐 DEPENDÊNCIAS PYTHON

### Já presentes no Django
```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import models
from django.utils import timezone
```

### Necessário instalar
```bash
pip install qrcode[pil]
```

### Não usado (já deve estar)
```python
import base64
from io import BytesIO
```

---

## ✅ CHECKLIST DE ARQUIVOS

- [x] models.py modificado com 8 campos
- [x] whatsapp_manager.py criado com 8 views
- [x] whatsapp.py criado com 8 URLs
- [x] dashboard.html criado com UI completa
- [x] detail.html criado com detalhes
- [x] 0011_migration.py gerada
- [x] [ ] config/urls.py pendente de edição

---

**Próximo passo:** Editar `config/urls.py` e aplicar migration! 🚀
