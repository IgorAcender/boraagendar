# 🔍 DEBUG: Reordenação de Seções

## Como Testar e Debugar

### 1. **Abra o DevTools do Navegador**
   - **Chrome/Edge**: Pressione `F12`
   - **Firefox**: Pressione `F12`
   - **Safari**: Cmd + Option + I

### 2. **Vá até a Página de Configurações de Marca**
   - URL: `https://seu-dominio/dashboard/configuracoes-marca/`

### 3. **Abra a Aba "Console"** no DevTools

### 4. **Tente Reordenar uma Seção**
   - Clique no botão ⬆️ para mover uma seção para cima
   - **Verifique o console** - você deve ver:
     ```
     🔄 updateSectionsState() chamado, seções encontradas: 5
       → about: order=0, visible=true
       → team: order=1, visible=true
       → hours: order=2, visible=true
       → contact: order=3, visible=true
       → social: order=4, visible=true
     ✅ id_sections_config atualizado: {"about":{...}, ...}
     ```

### 5. **Clique em "Salvar Configurações"**
   - **No console, você deve ver:**
     ```
     ✅ Form encontrado, adicionando listener de submit
     📤 Form submit disparado
     🔄 updateSectionsState() chamado, seções encontradas: 5
       → about: order=1, visible=true
       → team: order=0, visible=true
       ... (nova ordem)
     ✅ updateSectionsState() executado antes do submit
     📝 sections_config value: {"about":{"visible":true,"order":1},...}
     ```

## 📝 O Que Procurar

### ✅ Se Funciona:
- Console mostra os logs sem erros
- A página recarrega após salvar
- A ordem é mantida ao recarregar

### ❌ Se NÃO Funciona:
- **Campo não encontrado**: `❌ Campo id_sections_config NÃO ENCONTRADO no DOM!`
  - Solução: Verifique se o formulário tem `{{ form.sections_config }}`
  
- **Form não encontrado**: `❌ Nenhum form encontrado no DOM!`
  - Solução: Verifique se existe uma tag `<form>` na página
  
- **Erro 500 ao salvar**: Verifique os logs do servidor com `docker logs container-id`
  
- **Nada muda**: Pode ser um erro JavaScript silencioso - procure por erros vermelhos na aba "Console"

## 🔧 Dicas de Debug

### Ver o valor do campo hidden:
```javascript
console.log(document.getElementById('id_sections_config').value)
```

### Simular um movimento:
```javascript
// Encontra a primeira seção e a move
const field = document.querySelector('[data-section-id="about"]');
moveSectionFieldUp(field);
// Depois verifique o console
```

### Verificar se o formulário será enviado:
```javascript
// Simula um clique em "Salvar"
document.querySelector('form').submit();
// Verifique o console e veja se updateSectionsState é chamado
```

---

## 📊 Status Esperado

Após reordenar e salvar, o banco de dados deve ter:

```python
# Django shell
from tenants.models import BrandingSettings
branding = BrandingSettings.objects.first()
print(branding.sections_config)

# Esperado:
# {'about': {'visible': True, 'order': 1}, 'team': {'visible': True, 'order': 0}, ...}
```
