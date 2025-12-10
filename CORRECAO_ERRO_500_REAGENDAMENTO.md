# 🔧 Correção: Erro 500 no Reagendamento

## ❌ Problema

Ao clicar em "Reagendar" na página "Meus Agendamentos" (cliente), o sistema retornava erro 500:

```
django.core.exceptions.FieldError: Cannot resolve keyword 'auto_assign' into field.
```

## 🔍 Causa Raiz

Na função `reschedule_booking()` do arquivo `src/scheduling/views/public.py`, o código estava tentando filtrar profissionais usando o nome incorreto do campo do modelo `Professional`.

**Campo correto no modelo:** `allow_auto_assign`  
**Campo usado incorretamente:** `auto_assign`

## ✅ Solução Implementada

### Arquivo: `src/scheduling/views/public.py`

#### Correção 1 - Linha ~1005
**Antes:**
```python
available_professionals = Professional.objects.filter(
    tenant=tenant,
    is_active=True
).filter(
    Q(services=booking.service) | Q(auto_assign=True)  # ❌ INCORRETO
).distinct().order_by('display_name')
```

**Depois:**
```python
available_professionals = Professional.objects.filter(
    tenant=tenant,
    is_active=True
).filter(
    Q(services=booking.service) | Q(allow_auto_assign=True)  # ✅ CORRETO
).distinct().order_by('display_name')
```

#### Correção 2 - Linha ~1014
**Antes:**
```python
has_auto_assign = available_professionals.filter(auto_assign=True).exists()  # ❌ INCORRETO
```

**Depois:**
```python
has_auto_assign = available_professionals.filter(allow_auto_assign=True).exists()  # ✅ CORRETO
```

## 🧪 Validação

Teste realizado com sucesso:
```
✅ FLUXO COMPLETO DE REAGENDAMENTO
✅ Login: 302 (redirecionado conforme esperado)
✅ Lista de agendamentos: 200 (carregou)
✅ Formulário de reagendamento: 200 (carregou sem erro 500)
```

## 📋 Resumo das Mudanças

| Arquivo | Linhas | Alteração |
|---------|--------|-----------|
| `src/scheduling/views/public.py` | 1005, 1014 | Corrigir nome do campo de `auto_assign` para `allow_auto_assign` |

**Commit:** `4c72025` - Fix: Corrige erro 500 no reagendamento

## 🚀 Impacto

- ✅ Clientes agora conseguem acessar a página de reagendamento sem erro 500
- ✅ Profissionais com `allow_auto_assign=True` são listados corretamente
- ✅ Nenhuma mudança no banco de dados necessária
- ✅ Nenhuma mudança de API ou interface pública

## 📝 Notas

- O modelo `Professional` possui o campo `allow_auto_assign` (não `auto_assign`)
- Todas as outras referências no código já usavam o nome correto
- Esta era a única localização com o nome incorreto

