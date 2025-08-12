# Minimização da Sidebar

## Funcionalidade

A sidebar do Nations-Flow agora possui funcionalidade de minimização que permite mostrar apenas os ícones quando minimizada, economizando espaço na tela.

## Como Usar

### Botão de Toggle
- Clique no botão de toggle (ícone de lista) no canto superior direito da sidebar
- A sidebar alternará entre os estados expandido e minimizado

### Atalho de Teclado
- Use `Ctrl + B` (Windows/Linux) ou `Cmd + B` (Mac) para alternar rapidamente

### Estado Persistente
- O estado da sidebar é salvo automaticamente no navegador
- Na próxima visita, a sidebar manterá o estado anterior

## Comportamento

### Sidebar Expandida
- Mostra ícones e textos dos itens de menu
- Largura: 250px
- Exibe nome do usuário e botão de logout com texto

### Sidebar Minimizada
- Mostra apenas os ícones
- Largura: 60px
- Tooltips aparecem ao passar o mouse sobre os ícones
- Efeitos de hover melhorados

## Recursos

### Tooltips
- Quando minimizada, passar o mouse sobre os ícones mostra tooltips com o nome do item
- Tooltips aparecem com animação suave

### Transições Suaves
- Todas as transições são animadas com CSS
- Duração: 0.3 segundos
- Curva de animação: cubic-bezier(0.4, 0, 0.2, 1)

### Responsividade
- Em dispositivos móveis (≤768px), a sidebar é automaticamente minimizada
- O comportamento se adapta ao tamanho da tela

### Ícones Dinâmicos
- O botão de toggle muda de ícone conforme o estado:
  - `bi-list`: quando expandida
  - `bi-chevron-right`: quando minimizada

## Estrutura HTML

```html
<div class="sidebar" id="sidebar">
    <div class="sidebar-header">
        <h5 class="sidebar-brand">{{ title }}</h5>
        <button class="btn btn-link sidebar-toggle" id="sidebarToggle">
            <i class="bi bi-list"></i>
        </button>
    </div>
    
    <div class="sidebar-content">
        <ul class="sidebar-nav">
            <li class="sidebar-item">
                <a class="sidebar-link" href="{% url 'index' %}" title="Dashboard">
                    <i class="bi bi-graph-up"></i> <span>Dashboard</span>
                </a>
            </li>
            <!-- Outros itens... -->
        </ul>
    </div>
</div>
```

## Classes CSS Principais

- `.sidebar`: Container principal da sidebar
- `.sidebar.collapsed`: Estado minimizado
- `.sidebar-link`: Links de navegação
- `.sidebar-toggle`: Botão de toggle
- `.main-content.expanded`: Conteúdo principal quando sidebar está minimizada

## JavaScript

O comportamento é controlado pelo arquivo `app/static/js/index.js` com as seguintes funcionalidades:

- Toggle da sidebar
- Persistência do estado no localStorage
- Atalhos de teclado
- Responsividade automática
- Atualização dinâmica dos ícones 