# 🔧 Próximos Passos: Configurar Horários na Produção

## Status Atual

✅ Migration aplicada na produção  
❓ Horários configurados?  

---

## O Que Pode Estar Acontecendo

### Cenário 1: Você já configurou os horários via admin
→ Vá para **Checklist 1** abaixo

### Cenário 2: Você não configurou os horários ainda
→ Vá para **Checklist 2** abaixo

---

## Checklist 1: Se Você JÁ Configurou via Admin

### 1. Deploy do Código
```bash
# Local
git add src/scheduling/views/public.py
git commit -m "Add debug to business_hours view"
git push origin main

# Produção
cd /app
git pull origin main
```

### 2. Verifique os Logs
- Acesse o mini site em produção: `https://seu-dominio.com/{slug}/`
- Procure pelos logs por mensagens `DEBUG: Business Hours Count:`
- Se contar `0`: Os horários NÃO foram salvo no banco

### 3. Solução
Se os horários não aparecerem:
- Vá em `/admin/tenants/businesshours/`
- Verifique se os registros estão lá
- Se não estiverem, vá para **Checklist 2**

---

## Checklist 2: Se Você AINDA NÃO Configurou

### Opção A: Via Admin (Manual)

1. Acesse `/admin/tenants/businesshours/` em produção
2. Clique em **Add Business Hours**
3. Para cada dia (segunda a domingo):
   - **Tenant**: Selecione sua empresa
   - **Dia da Semana**: Segunda, Terça, etc.
   - **É Fechado?**: Marque se FECHADO
   - **Horário Abertura**: Ex: 09:00
   - **Horário Fechamento**: Ex: 18:00
4. Salve cada um

### Opção B: Via Script (Automático)

Execute em produção:

```bash
cd /app/src
python3 manage.py shell < setup_business_hours.py
```

Este script vai:
- ✅ Criar horários padrão para TODOS os tenants
- ✅ Segunda-Sexta: 09:00 - 18:00
- ✅ Sábado: 09:00 - 15:00
- ✅ Domingo: FECHADO

---

## Verificação Final

### 1. Remova o Debug (Opcional)
Após confirmar que funciona, remova os prints da view:

```python
# Remover estas linhas:
print(f"DEBUG: Tenant: {tenant.name}")
print(f"DEBUG: Business Hours Count: {business_hours.count()}")
for bh in business_hours:
    print(f"DEBUG:   - {bh.get_day_of_week_display()}: {bh}")
```

### 2. Teste no Navegador
- Acesse `https://seu-dominio.com/{slug}/`
- Procure pela seção "Horário de Funcionamento"
- Deverá mostrar os dias da semana e horários

### 3. Confirmação
```
Segunda: 09:00 - 18:00
Terça: 09:00 - 18:00
Quarta: 09:00 - 18:00
Quinta: 09:00 - 18:00
Sexta: 09:00 - 18:00
Sábado: 09:00 - 15:00
Domingo: FECHADO
```

---

## Caso Não Funcione

1. Verifique os logs em produção
2. Procure por erros de `BusinessHours`
3. Certifique-se que a migration foi aplicada: `python3 manage.py showmigrations tenants | grep 0012`

---

## Resumo de Ações

- [ ] Migration aplicada ✅ (já feito)
- [ ] Código atualizado com debug
- [ ] Deploy em produção
- [ ] Verifique logs
- [ ] Configure horários (Manual ou Script)
- [ ] Teste no navegador
- [ ] Remova debug (opcional)

---

**Data**: 3 de dezembro de 2025  
**Prioridade**: 🟢 MÉDIA - Funcionalidade de exibição
