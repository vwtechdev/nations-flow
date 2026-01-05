# Formulários

## Visão Geral

O arquivo `app/forms.py` contém todos os formulários Django da aplicação. Os formulários são responsáveis por validação de dados, renderização de widgets e processamento de dados de entrada.

## Formulários Principais

### 1. FieldForm

**Modelo**: `Field`

**Campos:**
- `name` (TextInput): Nome do campo

**Widgets:**
- `name`: `TextInput` com classe `form-control`

**Validações:**
- Nenhuma validação customizada (validações padrão do modelo)

---

### 2. ChurchForm

**Modelo**: `Church`

**Campos:**
- `name` (TextInput): Nome da igreja
- `address` (TextInput): Endereço (opcional)
- `shepherd` (Select): Pastor responsável
- `field` (Select): Campo ao qual pertence

**Widgets:**
- `name`: `TextInput` com classe `form-control`
- `address`: `TextInput` com classe `form-control`

**Validações:**
- Nenhuma validação customizada

---

### 3. UserForm

**Modelo**: `User`

**Campos:**
- `first_name` (TextInput): Primeiro nome *
- `last_name` (TextInput): Sobrenome *
- `email` (EmailInput): Email *
- `role` (Select): Função *
- `fields` (CheckboxTableWidget): Campos (apenas em edição)

**Widgets Customizados:**
- `fields`: `CheckboxTableWidget` - Tabela com checkboxes para seleção múltipla

**Validações:**

#### `clean_email()`
- Verifica se email já existe (exceto para o usuário atual em edição)
- Retorna erro se email duplicado

#### `clean()`
- Gera `username` automaticamente para novos usuários
- Formato: `first_name.lower() + last_name.lower()` (sem espaços)
- Adiciona contador se username já existe

#### `save()`
- Define senha padrão (`nations123456`) para novos usuários
- Define `password_changed=False` para forçar troca de senha
- Salva campos Many-to-Many após salvar o usuário

**Comportamento Especial:**
- Campo `fields` removido para novos usuários (adicionado apenas em edição)
- Campos obrigatórios marcados com asterisco (*)

---

### 4. ChangePasswordForm

**Não é ModelForm** - Formulário standalone

**Campos:**
- `new_password1` (PasswordInput): Nova senha *
- `new_password2` (PasswordInput): Confirmação da nova senha *

**Validações:**

#### `clean_new_password1()`
Validações de senha forte:
- Mínimo 8 caracteres
- Não pode ser senha simples (`123`, `123456`, `password`, `senha`, `admin`, `user`, `teste`, `test`)
- Não pode ser a senha padrão (`nations123456`)
- Não pode conter apenas números
- Não pode conter apenas letras
- Deve conter pelo menos:
  - Uma letra maiúscula
  - Uma letra minúscula
  - Um número
  - Um símbolo (`!@#$%^&*(),.?":{}|<>`)

#### `clean_new_password2()`
- Verifica se as senhas coincidem
- Retorna erro se diferentes

#### `save()`
- Define nova senha no usuário
- Marca `password_changed=True`
- Salva apenas campos `password` e `password_changed`

---

### 5. CategoryForm

**Modelo**: `Category`

**Campos:**
- `name` (TextInput): Nome da categoria
- `mandatory_proof` (CheckboxInput): Comprovante obrigatório

**Widgets:**
- `name`: `TextInput` com classe `form-control`
- `mandatory_proof`: `CheckboxInput` com classe `form-check-input`

**Validações:**
- Nenhuma validação customizada

---

### 6. TransactionForm

**Modelo**: `Transaction`

**Campos do Modelo:**
- `type` (Select): Tipo (Entrada/Saída)
- `desc` (Textarea): Descrição
- `category` (Select): Categoria
- `value` (NumberInput): Valor (R$)
- `date` (DateInput): Data
- `church` (Select): Igreja
- `proof` (FileInput): Comprovante

**Campos Adicionais (não salvos no modelo):**
- `field` (ModelChoiceField): Campo (para filtrar igrejas)
- `create_reminder` (BooleanField): Criar lembrete (apenas admin)

**Widgets:**
- `type`: `Select` com classe `form-control`
- `desc`: `Textarea` com 3 linhas
- `category`: `Select` com classe `form-control`
- `value`: `NumberInput` com step 0.01, min 0.01
- `date`: `DateInput` tipo `date`
- `church`: `Select` com classe `form-control`
- `proof`: `FileInput` com accept `.pdf,.jpg,.jpeg,.png`

**Comportamento Dinâmico:**

#### `__init__(user)`
- **Tesoureiros**: 
  - Veem apenas seus campos
  - Campo `create_reminder` removido
- **Administradores**: 
  - Veem todos os campos
  - Campo `create_reminder` disponível

#### Filtro de Igrejas
- Igrejas filtradas dinamicamente baseado no campo selecionado
- Em edição, mostra igrejas do campo da transação
- Em criação, campo `church` desabilitado até selecionar campo

#### Data Máxima
- Para novas transações: data máxima = hoje
- Para edição: permite qualquer data

#### Comprovante
- Em edição, mostra arquivo atual
- Help text com nome e tamanho do arquivo atual
- Campo não obrigatório se já há arquivo

**Validações:**

#### `clean_value()`
- Valor deve ser maior que zero
- Retorna erro se valor <= 0

#### `clean_date()`
- Para novas transações: data não pode ser futura
- Retorna erro se data > hoje

#### `clean_proof()`
- Tamanho máximo: 1MB
- Formatos aceitos: PDF, JPG, JPEG, PNG
- Retorna erro se arquivo inválido

#### `clean()`
- Valida que campo foi selecionado
- Valida que igreja foi selecionada
- Valida que igreja pertence ao campo selecionado
- Valida comprovante obrigatório baseado na categoria:
  - Nova transação: comprovante obrigatório se categoria requer
  - Edição: comprovante obrigatório se categoria requer E não há arquivo atual

---

### 7. EmailAuthenticationForm

**Herda de**: `AuthenticationForm`

**Campos:**
- `username` (EmailInput): Email (usado como username)
- `password` (PasswordInput): Senha

**Widgets:**
- `username`: `EmailInput` com placeholder "Digite seu email"
- `password`: `PasswordInput` com placeholder "Digite sua senha"

**Validações:**

#### `clean_username()`
- Verifica se email existe no sistema
- Retorna erro se email não encontrado

**Comportamento:**
- Usa email em vez de username para autenticação
- Integrado com `EmailBackend`

---

### 8. ShepherdForm

**Modelo**: `Shepherd`

**Campos:**
- `name` (TextInput): Nome do pastor

**Widgets:**
- `name`: `TextInput` com classe `form-control`

**Validações:**
- Nenhuma validação customizada

---

### 9. NotificationForm

**Modelo**: `Notification`

**Campos:**
- `title` (TextInput): Título da notificação
- `body` (Textarea): Mensagem
- `date` (DateTimeInput): Data e hora (tipo `datetime-local`)
- `is_read` (CheckboxInput): Marcar como lida
- `repeat` (CheckboxInput): Repetir notificação
- `repeat_frequency` (Select): Frequência de repetição

**Widgets:**
- `title`: `TextInput` com placeholder
- `body`: `Textarea` com 4 linhas e placeholder
- `date`: `DateTimeInput` tipo `datetime-local`
- `is_read`: `CheckboxInput`
- `repeat`: `CheckboxInput` com JavaScript `onchange`
- `repeat_frequency`: `Select` com classe `form-control`

**Comportamento:**

#### `__init__()`
- Formata data para HTML5 `datetime-local` em edição
- Adiciona JavaScript para mostrar/ocultar campo de frequência

**Validações:**

#### `clean()`
- Se `repeat=True`, `repeat_frequency` não pode ser `'none'`
- Se `repeat=False`, define `repeat_frequency='none'`
- Retorna erro se validação falhar

---

## Widgets Customizados

### CheckboxTableWidget

**Uso**: Campo `fields` em `UserForm`

**Funcionalidade:**
- Renderiza uma tabela HTML com checkboxes
- Cada linha representa um campo disponível
- Permite seleção múltipla
- Mantém estado de seleção

**Métodos:**
- `render()`: Gera HTML da tabela
- `value_from_datadict()`: Extrai valores selecionados do POST
- `value_omitted_from_data()`: Verifica se campo foi omitido

**HTML Gerado:**
```html
<div class="checkbox-table-container">
  <table class="table table-bordered table-hover">
    <thead>
      <tr>
        <th>Selecionar</th>
        <th>Nome do Campo</th>
      </tr>
    </thead>
    <tbody>
      <!-- Checkboxes para cada campo -->
    </tbody>
  </table>
</div>
```

---

## Padrões de Validação

### Validações de Campo
- Usam `clean_<field_name>()` para validação individual
- Retornam valor limpo ou levantam `ValidationError`

### Validações de Formulário
- Usam `clean()` para validações que dependem de múltiplos campos
- Retornam `cleaned_data` ou levantam `ValidationError` com dicionário de erros

### Mensagens de Erro
- Mensagens em português
- Específicas e descritivas
- Incluem valores quando relevante

---

## Integração com Views

### Processamento de Formulários
1. **GET**: Formulário vazio ou com instância (edição)
2. **POST**: 
   - `form.is_valid()`: Valida dados
   - `form.save()`: Salva no banco
   - Redireciona com mensagem de sucesso

### Contexto para Templates
- Formulário passado no contexto como `form`
- Dados relacionados (categorias, campos, igrejas) também no contexto
- Mensagens de erro exibidas automaticamente pelo Django

---

## Boas Práticas

### 1. Validação em Múltiplas Camadas
- Validação no formulário (cliente)
- Validação no modelo (banco de dados)
- Validação na view (lógica de negócio)

### 2. Mensagens de Erro Claras
- Específicas e descritivas
- Em português
- Incluem valores quando relevante

### 3. Widgets Customizados
- Reutilizáveis
- Acessíveis
- Responsivos

### 4. Processamento de Arquivos
- Validação de tipo e tamanho
- Upload seguro
- Feedback ao usuário
