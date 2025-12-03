# 📸 Mini Site - Hero Image Responsivo

## O que foi implementado

### **Desktop** (≥ 768px)
- Logo pequena: **140x140px**
- Posição: Centro do topo
- Borda arredondada e sombra
- Layout compacto

### **Mobile** (< 768px)
- Foto **preenche toda a altura** da viewport (60vh)
- Foto **preenche toda a largura** sem extrapolação das laterais
- A imagem é cortada nas laterais mantendo o topo e fundo visíveis
- Overlay com gradiente para legibilidade do nome
- Nome da empresa em grande destaque sobre a foto

---

## Como Funciona

### **Estrutura CSS**

```css
/* Mobile Hero */
@media (max-width: 767px) {
    .header-section {
        width: 100vw;                           /* Preenche viewport */
        margin-left: calc(-50vw + 50%);        /* Centraliza sem overflow */
        min-height: 60vh;                       /* Altura grande */
    }

    .logo-container {
        width: 100vw;                          /* Mesma largura do header */
        object-fit: cover;                     /* Corta laterais se necessário */
    }
}
```

### **Resultado Visual**

```
┌─────────────────────────────┐
│                             │
│      [FOTO PREENCHENDO]     │  ← 60vh de altura
│      [    TELA MÓVEL   ]    │
│          (1x1 ratio)        │
│     Overlay com gradiente   │
├─────────────────────────────┤
│  Nome da Empresa (z-index) │
├─────────────────────────────┤
│  Menu de Navegação          │  ← Abaixo do hero
└─────────────────────────────┘
```

---

## Especificações Técnicas

| Aspecto | Mobile | Desktop |
|---------|--------|---------|
| **Altura** | 60vh | Automática |
| **Largura** | 100vw | Restrita ao container |
| **Ratio** | Mantém proporção | 140x140px |
| **Overlay** | Gradient overlay | Nenhum |
| **Nome** | Sobre a foto | Abaixo da foto |
| **Laterais** | Cortadas se necessário | Visíveis |

---

## Efeitos Aplicados

1. **Brightness**: 0.7 (foto mais escura)
2. **Contrast**: 1.1 (mais definição)
3. **Gradiente overlay**: `rgba(0,0,0,0.1)` → `rgba(15,23,42,0.8)`
4. **Text shadow**: Para legibilidade do nome
5. **Z-index**: Nome fica acima da foto

---

## Comportamento em Diferentes Telas

### **iPhone SE (375px)**
```
┌───────────────────────┐
│                       │
│  [  FOTO (CROPPED)  ] │
│  [  HERO 60VH         │
│  [                    │
├───────────────────────┤
│    NOME DA EMPRESA    │
├───────────────────────┤
│  ☰  Menu Items        │
└───────────────────────┘
```

### **iPhone 12 (390px)**
```
┌─────────────────────────┐
│                         │
│  [   FOTO (CROPPED)   ] │
│  [    HERO 60VH        │
│  [                     │
├─────────────────────────┤
│     NOME DA EMPRESA     │
├─────────────────────────┤
│  ☰  Menu Items          │
└─────────────────────────┘
```

### **Tablet (768px+)**
```
┌──────────────────────────────┐
│                              │
│         [LOGO 140x140]       │
│                              │
│      NOME DA EMPRESA         │
│                              │
├──────────────────────────────┤
│   Menu Items (horizontal)    │
└──────────────────────────────┘
```

---

## CSS Técnico

### **Viewport Width (100vw)**
Garante que a foto ocupe **toda a largura** sem deixar espaços ou exceder.

### **Object-fit: Cover**
Mantém a proporção da imagem enquanto preenche o container, cortando as partes que não cabem.

### **Margin Recentralização**
```css
margin-left: calc(-50vw + 50%);
```
Compensa o `100vw` para evitar horizontal scroll.

### **Z-index Layering**
- Logo (imagem): z-index 1
- Overlay (gradient): z-index 2
- Nome: z-index 3
- Menu: z-index 10

---

## Animações e Efeitos

✅ **Fade-in** ao carregar  
✅ **Brightness dinâmica** para melhor contraste  
✅ **Gradient overlay** para legibilidade  
✅ **Text shadow** no nome para destaque  

---

## Validação

✅ Sem overflow horizontal no mobile  
✅ Foto preenche 100% da altura (60vh)  
✅ Foto preenche 100% da largura (100vw)  
✅ Nome legível com sombra  
✅ Menu visível abaixo  
✅ Desktop mantém layout original  

---

## Data de Implementação
**3 de dezembro de 2025**

## Status
✅ **IMPLEMENTADO E TESTADO**
