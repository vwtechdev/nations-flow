# Modelos de Dados

## Visão Geral

O sistema utiliza 9 modelos principais para gerenciar os dados da aplicação. Todos herdam do `BaseModel` abstrato (`core/models.py`), exceto `User` (que herda `AbstractUser`). O `BaseModel` fornece `created_at`, `updated_at`, `is_active` (soft delete), `created_by` e `updated_by`.

## Modelos Principais

### 1. Field (Campo)

Representa uma divisão geográfica ou administrativa.

**Campos:**
- `name` (CharField, max_length=200): Nome do campo
- `is_active` (BooleanField, default=True): Registro ativo (soft delete)
- `created_at` (DateTimeField, auto_now_add): Data de criação
- `updated_at` (DateTimeField, auto_now): Última atualização
- `created_by` / `updated_by` (ForeignKey → User, nullable): Auditoria

**Relacionamentos:**
- One-to-Many com `Church`
- Many-to-Many com `User`

**Métodos:**
- `__str__()`: Retorna o nome do campo

**Ordenação:** Por data de atualização (mais recente primeiro), depois por nome

---

### 2. Shepherd (Pastor)

Representa um pastor responsável por igrejas.

**Campos:**
- `name` (CharField, max_length=200): Nome do pastor
- `contract` (FileField, nullable): Contrato do pastor (`shepherds/%Y/%m/%d/`)
- `is_active` (BooleanField, default=True): Registro ativo (soft delete)
- `created_at` (DateTimeField, auto_now_add): Data de criação
- `updated_at` (DateTimeField, auto_now): Última atualização
- `created_by` / `updated_by` (ForeignKey → User, nullable): Auditoria

**Relacionamentos:**
- One-to-Many com `Church` (via `church_set`)

**Métodos:**
- `__str__()`: Retorna o nome do pastor

**Ordenação:** Por data de atualização (mais recente primeiro), depois por nome

---

### 3. Church (Igreja)

Representa uma igreja local vinculada a um campo e pastor.

**Campos:**
- `name` (CharField, max_length=200): Nome da igreja
- `address` (CharField, max_length=300, nullable): Endereço
- `shepherd` (ForeignKey → Shepherd): Pastor responsável
- `field` (ForeignKey → Field): Campo ao qual pertence
- `contract` (FileField, nullable): Contrato da igreja (`churches/%Y/%m/%d/`)
- `is_active` (BooleanField, default=True): Registro ativo (soft delete)
- `created_at` (DateTimeField, auto_now_add): Data de criação
- `updated_at` (DateTimeField, auto_now): Última atualização
- `created_by` / `updated_by` (ForeignKey → User, nullable): Auditoria

**Relacionamentos:**
- Many-to-One com `Field`
- Many-to-One com `Shepherd`
- One-to-Many com `Transaction`

**Métodos:**
- `__str__()`: Retorna o nome da igreja

**Ordenação:** Por data de atualização (mais recente primeiro), depois por nome

---

### 4. User (Usuário)

Modelo customizado de usuário que estende `AbstractUser`.

**Campos:**
- `email` (EmailField, unique=True): Email (usado como USERNAME_FIELD)
- `first_name` (CharField): Primeiro nome
- `last_name` (CharField): Sobrenome
- `username` (CharField): Nome de usuário (gerado automaticamente)
- `role` (CharField, choices): Função do usuário
  - `'admin'`: Administrador
  - `'treasurer'`: Tesoureiro
  - `'supervisor'`: Supervisor
- `fields` (ManyToManyField → Field): Campos aos quais o usuário tem acesso
- `is_owner` (BooleanField, default=False): Administrador Principal (definido só por superuser no `/admin/`)
- `password_changed` (BooleanField, default=False): Indica se a senha foi alterada
- `is_active` (BooleanField): Indica se o usuário está ativo
- `date_joined` (DateTimeField): Data de cadastro

**Relacionamentos:**
- Many-to-Many com `Field`
- One-to-Many com `Transaction`
- One-to-Many com `AccessLog`
- One-to-Many com `Notification` (created_by)

**Métodos:**
- `is_admin()`: Retorna True se o usuário é administrador
- `is_treasurer()`: Retorna True se o usuário é tesoureiro
- `is_supervisor()`: Retorna True se o usuário é supervisor
- `get_fields()`: Retorna QuerySet dos campos do usuário
- `has_field(field)`: Verifica se o usuário tem acesso a um campo específico
- `__str__()`: Retorna nome completo e função

**Configurações Especiais:**
- `USERNAME_FIELD = 'email'`: Email usado para login
- `REQUIRED_FIELDS = ['username', 'first_name', 'last_name']`

**Ordenação:** Por data de cadastro (mais recente primeiro), depois por nome

---

### 5. Category (Categoria)

Categoriza as transações financeiras.

**Campos:**
- `name` (CharField, max_length=100): Nome da categoria
- `mandatory_proof` (BooleanField, default=True): Se o comprovante é obrigatório
- `is_pix` (BooleanField, default=False): Transações desta categoria compõem o saldo PIX (demais compõem o saldo em caixa)
- `is_active` (BooleanField, default=True): Registro ativo (soft delete)
- `created_at` (DateTimeField, auto_now_add): Data de criação
- `updated_at` (DateTimeField, auto_now): Última atualização
- `created_by` / `updated_by` (ForeignKey → User, nullable): Auditoria

**Relacionamentos:**
- One-to-Many com `Transaction`

**Métodos:**
- `__str__()`: Retorna o nome da categoria

**Ordenação:** Por data de atualização (mais recente primeiro), depois por nome

---

### 6. Transaction (Transação)

Registra entradas e saídas financeiras.

**Campos:**
- `type` (CharField, choices): Tipo de transação
  - `'income'`: Entrada
  - `'expense'`: Saída
- `desc` (TextField, nullable): Descrição da transação
- `category` (ForeignKey → Category): Categoria
- `value` (DecimalField, max_digits=10, decimal_places=2): Valor (R$)
- `date` (DateField): Data da transação
- `user` (ForeignKey → User): Usuário que criou a transação
- `church` (ForeignKey → Church): Igreja relacionada
- `proof` (FileField, nullable): Comprovante (PDF, JPG, PNG)
- `is_checked` (BooleanField, default=False): Conferência de caixa (marcado em lote só por admin)
- `is_active` (BooleanField, default=True): Registro ativo
- `created_at` (DateTimeField, auto_now_add): Data de criação
- `updated_at` (DateTimeField, auto_now): Última atualização
- `created_by` / `updated_by` (ForeignKey → User, nullable): Auditoria

**Relacionamentos:**
- Many-to-One com `Category`
- Many-to-One com `User`
- Many-to-One com `Church`

**Validações:**
- `value`: Deve ser maior que 0.01 (MinValueValidator)
- `clean()`: Valida se comprovante é obrigatório baseado na categoria

**Métodos:**
- `get_formatted_value()`: Retorna valor formatado em R$ (ex: "R$ 1.234,56")
- `__str__()`: Retorna tipo, categoria e valor

**Ordenação:** Por data de atualização (mais recente primeiro), depois por data, depois por criação

**Upload de Arquivos:**
- Diretório: `proofs/%Y/%m/%d/`
- Formatos aceitos: PDF, JPG, JPEG, PNG
- Tamanho máximo: 1MB

---

### 7. AccessLog (Log de Auditoria)

Registra logins, logouts e ações (criação, edição, exclusão, conferência).

**Campos:**
- `user` (ForeignKey → User): Usuário
- `action` (CharField, choices): Ação realizada
  - `'login'`: Login
  - `'logout'`: Logout
  - `'create'`: Criação
  - `'update'`: Edição (inclui conferência/desconferência)
  - `'delete'`: Exclusão
- `description` (TextField): Descrição da ação
- `content_type` (ForeignKey → ContentType, nullable) + `object_id` (PositiveIntegerField, nullable): Objeto genérico relacionado (GenericForeignKey)
- `created_at` (DateTimeField, auto_now_add, db_column='timestamp'): Data e hora
- `updated_at`, `is_active`, `created_by`, `updated_by`: Herdados do `BaseModel`

**Relacionamentos:**
- Many-to-One com `User`

**Métodos Especiais:**
- `save()`: Sobrescrito para não salvar logs de superuser nem de `SYSTEM_HIDDEN_EMAIL`
- `__str__()`: Retorna usuário, ação e data/hora formatada

**Ordenação:** Por data de criação (mais recente primeiro)

---

### 8. Notification (Notificação)

Sistema de notificações e lembretes.

**Campos:**
- `title` (CharField, max_length=200): Título da notificação
- `body` (TextField): Mensagem da notificação
- `date` (DateTimeField): Data e hora da notificação
- `is_read` (BooleanField, default=False): Se foi lida
- `repeat` (BooleanField, default=True): Se deve repetir
- `repeat_frequency` (CharField, choices): Frequência de repetição
  - `'none'`: Não repetir
  - `'daily'`: Diariamente
  - `'weekly'`: Semanalmente
  - `'monthly'`: Mensalmente
  - `'annually'`: Anualmente
- `created_by` (ForeignKey → User): Usuário que criou
- `is_active` (BooleanField, default=True): Registro ativo
- `created_at` (DateTimeField, auto_now_add): Data de criação
- `updated_at` (DateTimeField, auto_now): Última atualização
- `updated_by` (ForeignKey → User, nullable): Auditoria

**Relacionamentos:**
- Many-to-One com `User` (created_by)

**Métodos:**
- `schedule_next()`: Reagenda a notificação baseado na frequência
  - Diária: +1 dia
  - Semanal: +1 semana
  - Mensal: +1 mês (relativedelta)
  - Anual: +1 ano (relativedelta)
  - Reseta `is_read` para False
- `__str__()`: Retorna título, data, status e frequência

**Ordenação:** Por data de criação (mais recente primeiro), depois por data

---

### 9. ShepherdHistory (Histórico de Pastor)

Registra as trocas de pastor responsável por igreja (criado automaticamente ao cadastrar igreja e ao trocar o pastor na edição).

**Campos:**
- `church` (ForeignKey → Church): Igreja
- `shepherd` (ForeignKey → Shepherd): Pastor do período
- `start_date` (DateField): Início do período
- `end_date` (DateField, nullable): Fim do período (`null` = pastor atual)
- `is_active` (BooleanField, default=True): Registro ativo
- `created_at` (DateTimeField, auto_now_add): Data de criação
- `updated_at` (DateTimeField, auto_now): Última atualização
- `created_by` / `updated_by` (ForeignKey → User, nullable): Auditoria

**Relacionamentos:**
- Many-to-One com `Church`
- Many-to-One com `Shepherd`

**Ordenação:** Por data de início (mais recente primeiro)

---

## Relacionamentos Entre Modelos

```
Field
  ├── Church (Many)
  │     ├── Transaction (Many)
  │     │     ├── Category (One)
  │     │     └── User (One)
  │     ├── Shepherd (One)
  │     └── ShepherdHistory (Many)

User
  ├── Transaction (Many)
  ├── AccessLog (Many)
  └── Notification (Many, created_by)

Shepherd
  └── Church (Many)
```

## Índices e Performance

### Índices Implícitos
- ForeignKeys criam índices automaticamente
- Campos `created_at` e `updated_at` são indexados implicitamente

### Otimizações de Query
- Uso de `select_related()` para ForeignKeys
- Uso de `prefetch_related()` para ManyToMany
- Filtros otimizados com `values()` e `values_list()`

## Validações e Regras de Negócio

### Transaction
- Valor mínimo: R$ 0,01
- Data não pode ser futura (apenas para novas transações)
- Comprovante obrigatório se categoria requer
- Igreja deve pertencer ao campo selecionado

### User
- Email único
- Senha deve ser alterada no primeiro login
- Username gerado automaticamente (first_name + last_name)

### Notification
- Se `repeat=True`, `repeat_frequency` não pode ser `'none'`
- Se `repeat=False`, `repeat_frequency` é definido como `'none'`

## Migrações

### Migrações Principais
1. `0001_initial.py`: Criação inicial de todos os modelos
2. `0002_notification_repeat_notification_repeat_frequency_and_more.py`: Adição de campos de repetição em Notification
3. `0003_basemodel.py`: Adição do modelo abstrato `BaseModel` (created_at, updated_at, is_active, created_by, updated_by)
4. `0004_contract_shepherdhistory.py`: Campos `contract` (FileField) em `Church` e `Shepherd` + criação de `ShepherdHistory`
5. `0005_shepherd_history_backfill.py`: Backfill de dados históricos de pastores
6. `0006_alter_church_contract_alter_shepherd_contract_and_more.py`: Ajustes em contratos e relacionamentos
7. `0007_alter_accesslog_options_remove_accesslog_ip_address_and_more.py`: Remoção de `ip_address` do AccessLog, ajustes de opções
8. `0008_user_is_owner.py`: Adição do campo `is_owner` (BooleanField) ao User
9. `0009_enable_unaccent.py`: Habilita extensão PostgreSQL `unaccent` para busca case/acento-insensível (no-op em SQLite)
10. `0010_category_is_pix.py`: Adição do campo `is_pix` (BooleanField) à Category
11. `0011_transaction_is_checked.py`: Adição do campo `is_checked` (BooleanField) à Transaction

### Comandos de Migração
```bash
python manage.py makemigrations
python manage.py migrate
```

### Validar sem Criar
```bash
python manage.py makemigrations --check --dry-run
```

### Deploy Aplica Migrações Automaticamente
Via `.github/workflows/deploy.yml`: `docker compose run --rm web python manage.py migrate --noinput`

## Auditoria

Todos os modelos (exceto `User`) herdam do `BaseModel` e incluem:
- `created_at`: Data de criação (auto_now_add)
- `updated_at`: Data de última atualização (auto_now)
- `is_active`: Registro ativo — exclusões na interface são inativação (soft delete), não remoção física (exceção: transações, que são excluídas de verdade com remoção do comprovante via signal `pre_delete`)
- `created_by` / `updated_by`: Usuário que criou/atualizou (nullable, `SET_NULL`)

Troca de arquivo (comprovante/contrato) na edição apaga o arquivo antigo do disco via signals `pre_save` (`_delete_old_file_field`).
