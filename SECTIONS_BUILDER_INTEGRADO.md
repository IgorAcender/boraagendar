┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       ✅ CONSTRUTOR DE SEÇÕES - VERSÃO INTEGRADA COMPLETA          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 NOVO DESIGN - CAMPOS INTEGRADOS
═══════════════════════════════════════════════════════════════════

Agora os campos de edição do "Conteúdo" têm os botões de controle
diretamente neles, e deslizam verticalmente quando você usa as setas!

┌─────────────────────────────────────────────────────────────┐
│ Conteúdo                                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Sobre nós (mini site)              [☑️] [⬆️] [⬇️]       ││
│ ├──────────────────────────────────────────────────────────┤│
│ │ hhuhuhuhuhuhuhu                                          ││
│ │ (sua descrição)                                          ││
│ │ (textosão editáveis)                                    ││
│ │ ...                                                      ││
│ └──────────────────────────────────────────────────────────┘│
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Contatos (mini site)               [☑️] [⬆️] [⬇️]       ││
│ ├──────────────────────────────────────────────────────────┤│
│ │ (campo de contato)                                       ││
│ │ ...                                                      ││
│ └──────────────────────────────────────────────────────────┘│
│                                                              │
└─────────────────────────────────────────────────────────────┘

Quando você clica ⬆️ ou ⬇️, o campo se move para cima ou para baixo!


🎨 O QUE FOI IMPLEMENTADO
═══════════════════════════════════════════════════════════════

1️⃣  CHECKBOX DE VISIBILIDADE [☑️]
    • Ativa/desativa se a seção aparece na página pública
    • Salvo automaticamente no campo `sections_config`

2️⃣  BOTÃO PARA CIMA [⬆️]
    • Move o campo uma posição para cima
    • Desabilitado na primeira seção
    • Atualiza a ordem automaticamente

3️⃣  BOTÃO PARA BAIXO [⬇️]
    • Move o campo uma posição para baixo
    • Desabilitado na última seção
    • Atualiza a ordem automaticamente


💾 COMO FUNCIONA
═══════════════════════════════════════════════════════════════

1. Você edita os campos normalmente (tipo, escreve no campo)
2. Você usa os botões ⬆️ ⬇️ para mudar a posição do campo
3. Você usa o checkbox [☑️] para mostrar/ocultar a seção
4. Ao clicar "Salvar Configurações", tudo é salvo:
   - Conteúdo dos campos
   - Ordem dos campos
   - Visibilidade de cada seção


🔧 TÉCNICAMENTE
═══════════════════════════════════════════════════════════════

Backend:
  ✅ Campo `BrandingSettings.sections_config` (JSONField)
  ✅ Form renderiza o campo como HiddenInput
  ✅ Salva automaticamente ao submit

Frontend:
  ✅ Checkbox em cada campo (`.section-visible-toggle`)
  ✅ Botões ⬆️ ⬇️ em cada campo (`.btn-section-up` / `.btn-section-down`)
  ✅ JavaScript reordena DOM e atualiza JSON oculto
  ✅ CSS moderno com hover effects

JavaScript:
  ✅ Detecta cliques nos botões
  ✅ Move elementos no DOM (insertBefore)
  ✅ Atualiza ordem no JSON
  ✅ Atualiza estado dos botões (disabled/enabled)


📋 CAMPO "SOBRE NÓS" EXEMPLO
═══════════════════════════════════════════════════════════════

Estrutura HTML:

<div class="form-field section-field" data-section-id="about">
    <div class="section-field-header">
        <label>Sobre nós (mini site)</label>
        <div class="order-controls">
            <input type="checkbox" class="section-visible-toggle" checked>
            <button type="button" class="btn-section-up">⬆️</button>
            <button type="button" class="btn-section-down">⬇️</button>
        </div>
    </div>
    <textarea>... conteúdo ...</textarea>
</div>

Dados Salvos (JSON):

{
    "about": {
        "visible": true,      ← checkbox
        "order": 0            ← posição
    },
    ...
}


🚀 COMO USAR
═══════════════════════════════════════════════════════════════

1. Abra dashboard → Cores e Marca

2. Role até "Conteúdo"

3. Você verá os campos com os controles:
   ┌────────────────────────────────────────┐
   │ Label                 [☑️] [⬆️] [⬇️] │
   ├────────────────────────────────────────┤
   │ Seu texto aqui                         │
   └────────────────────────────────────────┘

4. Use os botões:
   • [☑️] → Marque para mostrar, desmarque para ocultar
   • [⬆️] → Move para cima (se não for o primeiro)
   • [⬇️] → Move para baixo (se não for o último)

5. Clique "Salvar Configurações" para persistir tudo


✅ ARQUIVOS MODIFICADOS
═══════════════════════════════════════════════════════════════

📝 src/templates/scheduling/dashboard/branding_settings.html
   • Adicionados controles ao campo "about_us"
   • Adicionado CSS para os controles
   • Adicionado JavaScript para reordenação
   • Adicionado campo hidden do form

📝 src/tenants/forms.py
   • Adicionado widget HiddenInput para sections_config

📝 src/tenants/models.py
   • Já tinha o campo sections_config (nenhuma mudança)


🔄 FLUXO DE DADOS
═══════════════════════════════════════════════════════════════

Usuário clica ⬆️
    ↓
JavaScript detecta evento
    ↓
Reordena elementos no DOM (insertBefore)
    ↓
Chama updateButtonStates()
    ↓
Chama updateSectionsState()
    ↓
Atualiza JSON no campo hidden
    ↓
Usuário clica "Salvar Configurações"
    ↓
Form submit envia JSON para backend
    ↓
Django salva em BrandingSettings.sections_config


🎨 CSS CLASSES
═══════════════════════════════════════════════════════════════

.section-field
  • Container do campo
  • Tem atributo data-section-id="..."

.section-field-header
  • Flex container para label + botões
  • display: flex
  • justify-content: space-between

.order-controls
  • Flex container dos botões
  • display: flex
  • gap: 0.5rem

.section-visible-toggle
  • Checkbox
  • width: 20px, height: 20px

.btn-section-up / .btn-section-down
  • Botões com ícones
  • Hover com cor #667eea
  • Disabled com opacity 0.4


📊 ESTRUTURA JSON SALVA
═══════════════════════════════════════════════════════════════

Exemplo:

{
    "about": {
        "visible": true,
        "order": 0
    },
    "contact": {
        "visible": true,
        "order": 1
    }
}

Cada seção tem:
  • visible: bool → Se aparece na página pública
  • order: int → Posição (0 = primeira)


🎯 COMPATIBILIDADE
═══════════════════════════════════════════════════════════════

✓ Funciona em Chrome, Firefox, Safari, Edge
✓ Responsivo (mobile-friendly)
✓ Acessível (labels, titles)
✓ JavaScript puro (sem jQuery)
✓ Django 3.1+ (JSONField nativo)


💡 DICAS
═══════════════════════════════════════════════════════════════

1. Seções sempre podem ser movidas (não há limite)
2. Dados salvos transparentemente no background
3. Se desabilitar uma seção, ela não aparece no site público
4. Ordem é persistida quando você recarrega a página
5. Compatível com todas as seções (não é só o "Sobre Nós")


⚠️ NOTAS
═══════════════════════════════════════════════════════════════

• Campo oculto é renderizado via {{ form.sections_config }}
• Ordem começa do 0 (primeira seção = ordem 0)
• Seções sempre existem (não podem ser deletadas)
• Só o que pode mudar é: visibilidade + ordem


🧪 TESTE RÁPIDO
═══════════════════════════════════════════════════════════════

1. Abrir Dashboard
2. Ir para "Cores e Marca"
3. Procurar seção "Conteúdo"
4. Desmarcar checkbox ☐ em uma seção
5. Clicar ⬇️ para mover para baixo
6. Clicar "Salvar Configurações"
7. Recarregar página
8. Verificar se ordem e visibilidade persistiram ✅


╔═══════════════════════════════════════════════════════════════╗
║         ✅ PRONTO PARA USAR - MUITO MAIS INTUITIVO!         ║
║          Os campos deslizam direto no formulário 🎉          ║
╚═══════════════════════════════════════════════════════════════╝
