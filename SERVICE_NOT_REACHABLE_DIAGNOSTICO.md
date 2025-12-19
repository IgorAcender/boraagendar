# 🔴 "Service is not reachable" - App Down

## ❌ O Que Aconteceu

App está offline com mensagem:
```
Service is not reachable
Make sure the service is running and healthy.
```

---

## 🔍 Causas Possíveis

```
1. ❌ Docker build falhou
2. ❌ Migrations falharam
3. ❌ Erro no settings.py
4. ❌ Erro no entrypoint.sh
5. ❌ Porta 8000 não respondendo
```

---

## 📋 Próximos Passos

### Opção 1: Ver Logs do EasyPanel (Rápido)

1. Vá para **EasyPanel Dashboard**
2. Procure por **"Logs"** ou **"Container Logs"**
3. Copie os erros e cole aqui
4. Vou diagnosticar

### Opção 2: Reverter Temporariamente (Emergência)

Se precisar app online agora:

```bash
git revert 781b6d5  # Reverter última mudança
git push
```

Depois EasyPanel vai recompilar com versão anterior.

---

## 💡 Possível Causa

Erro na linha que adicionei:

```python
STATICFILES_DIRS = [
    BASE_DIR / "assets",
    BASE_DIR / "static",  # ← Caminho errado?
]
```

Deveria ser (em vez de `BASE_DIR / "static"`):

```python
STATICFILES_DIRS = [
    BASE_DIR / "assets",
    BASE_DIR.parent / "src" / "static",  # ← Caminho relativo correto?
]
```

---

## 🚀 Solução Rápida

Se o problema for o caminho, podemos consertar com:

```python
import os
STATICFILES_DIRS = [
    BASE_DIR / "assets",
]

# Adicionar caminho de src/static se existir
src_static = os.path.join(os.path.dirname(BASE_DIR), 'src', 'static')
if os.path.exists(src_static):
    STATICFILES_DIRS.append(src_static)
```

---

## 📞 Me Diga

1. **Você pode ver logs do EasyPanel?**
   - Se sim, copie mensagem de erro aqui

2. **Quer reverter temporariamente?**
   - Posso fazer isso agora

3. **Ou quer tentar corrigir?**
   - Preciso dos logs para saber exatamente qual erro

---

**Próximo Passo: Me envie os LOGS do EasyPanel!** 🔍
