# Instruções para Usar o Construtor de Seções

## Overview

O construtor de seções permite que você controle quais seções aparecem na página de landing e em qual ordem elas aparecem.

## Dados Salvos

Quando você clica em "Salvar Configurações" na página de branding settings, a configuração das seções é salva no campo `BrandingSettings.sections_config` como JSON:

```json
{
    "about": {"visible": true, "order": 0},
    "team": {"visible": true, "order": 1},
    "hours": {"visible": false, "order": 2},
    "contact": {"visible": true, "order": 3},
    "location": {"visible": true, "order": 4},
    "amenities": {"visible": true, "order": 5},
    "payment_methods": {"visible": true, "order": 6},
    "social": {"visible": true, "order": 7}
}
```

## No Template (tenant_landing.html)

### Opção 1: Usar template tags (recomendado)

```html
{% load sections %}

<!-- Carrega as configurações -->
{% with branding=tenant.branding_settings %}
    
    <!-- Verifica se a seção está visível -->
    {% if branding|section_visible:"about" %}
        <section id="about" class="section">
            <!-- Conteúdo da seção "Sobre" -->
        </section>
    {% endif %}
    
    {% if branding|section_visible:"team" %}
        <section id="team" class="section">
            <!-- Conteúdo da seção "Equipe" -->
        </section>
    {% endif %}
    
    <!-- ... mais seções ... -->
    
{% endwith %}
```

### Opção 2: Usar view helpers (para Python)

```python
from scheduling.views.sections_helper import is_section_visible, get_sections_order

# Na view
context = {
    'tenant': tenant,
    'sections_config': tenant.branding_settings.sections_config,
    'is_section_visible': is_section_visible,
    'get_sections_order': get_sections_order,
}
```

### Opção 3: Reordenar seções dinamicamente

Se quiser respeitar a ordem configurada, você pode fazer:

```html
{% load sections %}

{% with branding=tenant.branding_settings %}
    {% for section_id in branding|sections_order %}
        {% if section_id == "about" %}
            <section id="about" class="section">...</section>
        {% elif section_id == "team" %}
            <section id="team" class="section">...</section>
        {% endif %}
    {% endfor %}
{% endwith %}
```

## Seções Disponíveis

1. **about** - "Sobre Nós"
2. **team** - "Equipe"
3. **hours** - "Horário de Funcionamento"
4. **contact** - "Contato"
5. **location** - "Endereço"
6. **amenities** - "Comodidades"
7. **payment_methods** - "Formas de Pagamento"
8. **social** - "Redes Sociais"

## Arquivo Helper

**Localização:** `/src/scheduling/views/sections_helper.py`

**Funções disponíveis:**

- `get_sections_config(branding_settings)` - Retorna dict com toda a configuração
- `get_sections_order(branding_settings)` - Retorna lista de IDs visíveis em ordem
- `is_section_visible(branding_settings, section_id)` - Verifica se seção está visível
- `get_section_order(branding_settings, section_id)` - Retorna a posição da seção

## Próximos Passos

1. Importar as template tags em `tenant_landing.html`:
   ```html
   {% load sections %}
   ```

2. Envolver as seções com condicionais de visibilidade

3. Opcionalmente, reordenar as seções baseado na configuração salva
