# 🔧 TESTE MANUAL NO CONSOLE

Copie e execute CADA UMA dessas linhas no console (F12) uma de cada vez:

## 1️⃣ Verificar se o botão existe:
```javascript
document.getElementById('btn-save-branding')
```
Deve retornar: `<button type="submit" class="btn-submit" id="btn-save-branding" ...>`

Se retornar `null`, o botão não foi encontrado.

---

## 2️⃣ Verificar se o formulário existe:
```javascript
document.querySelector('form')
```
Deve retornar: `<form method="post" enctype="multipart/form-data">`

---

## 3️⃣ Verificar se o campo hidden existe:
```javascript
document.getElementById('id_sections_config')
```
Deve retornar: `<input type="hidden" name="sections_config" id="id_sections_config" value="...">`

---

## 4️⃣ Ver o valor atual do sections_config:
```javascript
console.log(document.getElementById('id_sections_config').value)
```

---

## 5️⃣ Simular um clique no botão:
```javascript
document.getElementById('btn-save-branding').click()
```
Você deve ver no console:
- `🖱️ onclick disparado`
- `✅ updateSectionsState() chamado no onclick`
- E outros logs...

---

## 6️⃣ Se clicar não funciona, tente submeter o formulário manualmente:
```javascript
document.querySelector('form').submit()
```
Você deve ver:
- `📤 Form submit disparado`
- Depois a página deve recarregar

---

## 7️⃣ Se absolutamente nada funciona, verifique se há JavaScript errors:
Procure por **erros em vermelho** na aba Console.
Se houver, copie exatamente o que está escrito.

---

## 🎯 RESUMO DO QUE FAZER:

1. Abra F12 no navegador
2. Vá na aba **Console**
3. Reordene uma seção (clique em ⬆️)
4. Execute `document.getElementById('btn-save-branding').click()`
5. **Me manda TUDO que aparecer no console**, incluindo todos os logs
6. Se não funcionar, execute os testes acima e me mande o resultado de cada um

