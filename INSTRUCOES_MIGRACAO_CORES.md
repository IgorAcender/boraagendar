# 🔧 Instruções para Aplicar as Migrações no Easy Panel

## ❌ Problema Atual
- Erro 500 na página de "Configurações de Marca"
- Causa: O banco de dados ainda tem os campos antigos (button_color_secondary, use_gradient_buttons, highlight_color)

## ✅ Solução

Execute **EXATAMENTE NESTA ORDEM** no terminal do Easy Panel:

```bash
cd /app

# Passo 1: Aplicar a migração que remove os campos antigos
python manage.py migrate tenants 0015

# Passo 2: Verificar se tudo está OK
python manage.py check
```

## 📋 O que vai acontecer:

1. A migração `0015_remove_old_branding_fields` será aplicada
2. Os seguintes campos serão removidos do banco de dados:
   - ❌ button_color_secondary
   - ❌ use_gradient_buttons
   - ❌ highlight_color

3. Os seguintes campos serão mantidos:
   - ✅ background_color
   - ✅ text_color
   - ✅ button_color_primary
   - ✅ button_text_color

## 🎯 Resultado

Após aplicar a migração, a página de "Configurações de Marca" funcionará perfeitamente com apenas 4 seletores de cor:
- Cor de Fundo
- Cor de Texto
- Cor do Botão
- Cor de Texto do Botão

O gradiente dos botões será gerado **automaticamente** (20% mais escuro que a cor primária).

## 🚀 Alternativa: Redeploy Automático

Se você fizer um redeploy do Easy Panel, o entrypoint.sh foi atualizado para executar `python manage.py migrate` automaticamente na inicialização.

---

**Status**: ✅ Código pronto para aplicar a migração
