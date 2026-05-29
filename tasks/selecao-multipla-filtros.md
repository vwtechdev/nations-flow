# Implementação: Seleção Múltipla nos Filtros

## Visão Geral

Esta tarefa implementa a funcionalidade de seleção múltipla nos filtros usando Select2, permitindo que os usuários selecionem mais de um valor simultaneamente nos seguintes filtros:

- **Categorias**
- **Campos**
- **Pastores**
- **Igrejas**
- **Usuários**

Esses filtros aparecem em:
- Dashboard (`/`)
- Lista de Transações (`/transactions/`)

## Objetivo

Permitir que os usuários filtrem transações selecionando múltiplos valores em cada filtro, facilitando análises mais complexas e comparações entre diferentes categorias, campos, pastores, igrejas ou usuários.

## Filtros Afetados

### 1. Categorias (`categoryFilter`)
- **Localização**: Dashboard e Lista de Transações
- **Elemento HTML**: `#categoryFilter` e `#categoryFilter_mobile`
- **Backend**: `request.GET.get('category')` → `request.GET.getlist('category')`

### 2. Campos (`fieldFilter`)
- **Localização**: Dashboard e Lista de Transações
- **Elemento HTML**: `#fieldFilter` e `#fieldFilter_mobile`
- **Backend**: `request.GET.get('field')` → `request.GET.getlist('field')`

### 3. Pastores (`shepherdFilter`)
- **Localização**: Dashboard e Lista de Transações
- **Elemento HTML**: `#shepherdFilter` e `#shepherdFilter_mobile`
- **Backend**: `request.GET.get('shepherd')` → `request.GET.getlist('shepherd')`

### 4. Igrejas (`churchFilter`)
- **Localização**: Dashboard e Lista de Transações
- **Elemento HTML**: `#churchFilter` e `#churchFilter_mobile`
- **Backend**: `request.GET.get('church')` → `request.GET.getlist('church')`

### 5. Usuários (`userFilter`)
- **Localização**: Dashboard e Lista de Transações (apenas Admin e Supervisor)
- **Elemento HTML**: `#userFilter` e `#userFilter_mobile`
- **Backend**: `request.GET.get('user')` → `request.GET.getlist('user')`

## Alterações Necessárias

### Frontend

#### 1. Templates HTML

**Arquivos a modificar:**
- `app/templates/pages/dashboard.html`
- `app/templates/pages/transaction_list.html`

**Mudanças:**
- Adicionar atributo `multiple` nos elementos `<select>` dos filtros
- Atualizar placeholders para indicar seleção múltipla
- Exemplo:
  ```html
  <!-- ANTES -->
  <select name="category" id="categoryFilter" class="form-control">
  
  <!-- DEPOIS -->
  <select name="category" id="categoryFilter" class="form-control" multiple>
  ```

#### 2. JavaScript - Select2 Configuration

**Arquivo:** `app/static/js/filters_form.js`

**Mudanças:**
- Adicionar `multiple: true` na configuração do Select2 para cada filtro
- Atualizar placeholders para indicar seleção múltipla
- Ajustar `closeOnSelect: false` para permitir múltiplas seleções sem fechar o dropdown

**Exemplo de configuração:**
```javascript
const select2Config = {
    theme: 'bootstrap-5',
    placeholder: 'Selecione um ou mais...',
    allowClear: true,
    width: '100%',
    language: 'pt-BR',
    multiple: true,  // NOVO
    closeOnSelect: false,  // MODIFICADO
    minimumResultsForSearch: 10,
    dropdownParent: 'body',
    selectionCssClass: 'filters-select2',
    dropdownCssClass: 'filters-dropdown'
};
```

#### 3. Sincronização Mobile/Desktop

**Arquivo:** `app/static/js/filters_form.js`

**Mudanças:**
- Ajustar função `syncSelect2Fields()` para lidar com arrays de valores
- Usar `.val(array)` em vez de `.val(value)` para múltiplos valores

### Backend

#### 1. Views Principais

**Arquivo:** `app/views.py`

**Views a modificar:**
- `index()` - Dashboard
- `transaction_list()` - Lista de transações
- `transaction_list_api()` - API de listagem
- `transaction_summary_api()` - API de resumo
- `transaction_export_pdf()` - Exportação PDF
- `transaction_export_xlsx()` - Exportação Excel

**Mudanças em cada view:**

**ANTES:**
```python
selected_category = request.GET.get('category', '')
if selected_category:
    transactions = transactions.filter(category_id=selected_category)
```

**DEPOIS:**
```python
selected_categories = request.GET.getlist('category')
if selected_categories:
    transactions = transactions.filter(category_id__in=selected_categories)
```

**Padrão para todos os filtros:**
- `selected_field` → `selected_fields = request.GET.getlist('field')`
- `selected_church` → `selected_churches = request.GET.getlist('church')`
- `selected_shepherd` → `selected_shepherds = request.GET.getlist('shepherd')`
- `selected_user` → `selected_users = request.GET.getlist('user')`

**Filtros a aplicar:**
- Categoria: `.filter(category_id__in=selected_categories)`
- Campo: `.filter(church__field_id__in=selected_fields)`
- Igreja: `.filter(church_id__in=selected_churches)`
- Pastor: `.filter(church__shepherd_id__in=selected_shepherds)`
- Usuário: `.filter(user_id__in=selected_users)`

#### 2. Validação de Permissões

**Para filtro de Campo:**
```python
if selected_fields:
    if request.user.is_admin():
        transactions = transactions.filter(church__field_id__in=selected_fields)
    elif request.user.fields.count() > 1:
        # Validar que todos os campos selecionados pertencem ao usuário
        valid_fields = request.user.fields.filter(id__in=selected_fields).values_list('id', flat=True)
        if valid_fields:
            transactions = transactions.filter(church__field_id__in=valid_fields)
```

**Para filtro de Usuário (Supervisor):**
```python
if selected_users:
    if request.user.is_admin():
        transactions = transactions.filter(user_id__in=selected_users)
    elif request.user.is_supervisor():
        supervisor_fields = request.user.fields.all()
        if supervisor_fields.exists():
            allowed_user_ids = User.objects.filter(
                Q(id=request.user.id) |
                Q(role='treasurer', fields__in=supervisor_fields)
            ).distinct().values_list('id', flat=True)
            valid_users = [uid for uid in selected_users if int(uid) in allowed_user_ids]
            if valid_users:
                transactions = transactions.filter(user_id__in=valid_users)
```

#### 3. Contexto para Templates

**Mudanças:**
- Converter listas de IDs em nomes para exibição
- Atualizar `selected_category_name`, `selected_field_name`, etc. para lidar com múltiplos valores

**Exemplo:**
```python
# ANTES
'selected_category_name': Category.objects.get(id=selected_category).name if selected_category else None,

# DEPOIS
'selected_category_names': [cat.name for cat in Category.objects.filter(id__in=selected_categories)] if selected_categories else [],
```

#### 4. APIs JSON

**Arquivo:** `app/views.py`

**APIs a modificar:**
- `transaction_list_api()` - Aceitar arrays nos parâmetros
- `transaction_summary_api()` - Processar arrays no payload JSON

**Mudanças:**
```python
# Para GET
selected_categories = request.GET.getlist('category')

# Para POST (JSON)
payload = json.loads(request.body or '{}')
selected_categories = payload.get('category', [])
if isinstance(selected_categories, str):
    selected_categories = [selected_categories]
```

### JavaScript - Leitura de Filtros

**Arquivo:** `app/templates/pages/dashboard.html` e `app/templates/pages/transaction_list.html`

**Função `readFiltersFromForm()`:**
- Modificar para ler arrays de valores do Select2
- Usar `.val()` que retorna array quando `multiple: true`

**Exemplo:**
```javascript
function readFiltersFromForm() {
    const val = id => {
        const element = document.getElementById(id);
        if (!element) return [];
        // Select2 com multiple retorna array
        const select2Instance = $(element).data('select2');
        if (select2Instance) {
            return $(element).val() || [];
        }
        return element.value ? [element.value] : [];
    };
    
    return {
        category: val('categoryFilter') || val('categoryFilter_mobile'),
        field: val('fieldFilter') || val('fieldFilter_mobile'),
        // ... outros filtros
    };
}
```

## Considerações de UX

### 1. Placeholders
- Atualizar placeholders para indicar seleção múltipla
- Exemplos:
  - "Selecione uma ou mais categorias..."
  - "Selecione um ou mais campos..."
  - "Selecione um ou mais pastores..."

### 2. Visualização de Seleções
- Select2 já exibe tags para múltiplas seleções
- Garantir que o CSS suporte bem a exibição de múltiplas tags

### 3. Limpeza de Filtros
- Botão "Limpar" deve limpar todas as seleções
- `allowClear: true` já funciona com múltiplas seleções

### 4. Sincronização Mobile/Desktop
- Garantir que seleções múltiplas sejam sincronizadas corretamente
- Usar arrays ao invés de valores únicos

## Testes Necessários

### 1. Testes Funcionais
- [ ] Selecionar múltiplas categorias e verificar filtro
- [ ] Selecionar múltiplos campos e verificar filtro
- [ ] Selecionar múltiplos pastores e verificar filtro
- [ ] Selecionar múltiplas igrejas e verificar filtro
- [ ] Selecionar múltiplos usuários e verificar filtro
- [ ] Combinar múltiplos filtros simultaneamente
- [ ] Limpar filtros múltiplos
- [ ] Sincronização mobile/desktop com múltiplas seleções

### 2. Testes de Permissões
- [ ] Admin pode selecionar múltiplos campos
- [ ] Tesoureiro só pode selecionar seus próprios campos
- [ ] Supervisor pode selecionar múltiplos usuários (dentro de permissões)
- [ ] Validação de campos inválidos

### 3. Testes de Performance
- [ ] Performance com muitos valores selecionados
- [ ] Performance de queries com múltiplos filtros `__in`
- [ ] Carregamento de Select2 com muitas opções

### 4. Testes de APIs
- [ ] API de listagem com múltiplos valores
- [ ] API de resumo com múltiplos valores
- [ ] Exportação PDF com múltiplos filtros
- [ ] Exportação Excel com múltiplos filtros

## Arquivos a Modificar

### Frontend
- `app/templates/pages/dashboard.html`
- `app/templates/pages/transaction_list.html`
- `app/static/js/filters_form.js`

### Backend
- `app/views.py` (múltiplas funções)

### CSS (se necessário)
- `app/static/css/filters_form.css` (ajustes visuais para múltiplas seleções)

## Ordem de Implementação Sugerida

1. **Frontend - HTML**: Adicionar `multiple` nos selects
2. **Frontend - JavaScript**: Configurar Select2 com `multiple: true`
3. **Backend - Views**: Modificar uma view por vez (começar com `transaction_list`)
4. **Backend - APIs**: Atualizar APIs para aceitar arrays
5. **Testes**: Testar cada filtro individualmente
6. **Testes Integrados**: Testar combinações de filtros
7. **Ajustes de UX**: Melhorar placeholders e mensagens

## Notas Adicionais

- Manter compatibilidade com código existente
- Considerar adicionar indicador visual de quantos itens estão selecionados
- Documentar comportamento de filtros múltiplos na documentação do projeto
- Considerar limite máximo de seleções (se necessário para performance)

## Referências

- [Select2 Multiple Selection](https://select2.org/getting-started/basic-usage#multi-select-boxes-pillbox)
- Django QuerySet `__in` lookup: https://docs.djangoproject.com/en/stable/ref/models/querysets/#in
