# Configuração de Usuários - Nations Flow

## 📋 Visão Geral

O sistema **Nations Flow** utiliza um modelo de usuário customizado que estende o `AbstractUser` do Django, com autenticação baseada em **email** e sistema de permissões por **roles** (funções).

---

## 🔐 Modelo de Usuário

### Herança e Campos Base
- **Herda de**: `AbstractUser` (Django)
- **Modelo customizado**: `AUTH_USER_MODEL = 'app.User'`
- **Campo de autenticação**: `email` (USERNAME_FIELD)

### Campos Customizados

```python
class User(AbstractUser):
    # Campos do AbstractUser herdados:
    # - username, password, first_name, last_name, email
    # - is_active, is_staff, is_superuser
    # - date_joined, last_login
    # - groups, user_permissions
    
    # Campos customizados:
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='treasurer')
    fields = models.ManyToManyField(Field, blank=True)
    password_changed = models.BooleanField(default=False)
    email = models.EmailField(unique=True)  # Sobrescrito para ser único
```

### Campos Específicos

1. **`role`** (Função)
   - **Tipo**: CharField com choices
   - **Valores possíveis**:
     - `'admin'` → Administrador
     - `'treasurer'` → Tesoureiro
   - **Padrão**: `'treasurer'`

2. **`fields`** (Campos/Regiões)
   - **Tipo**: ManyToMany com modelo `Field`
   - **Propósito**: Define quais campos geográficos o usuário tem acesso
   - **Obrigatório**: Não (blank=True)
   - **Uso**: Restringe visualização de transações e igrejas por região

3. **`password_changed`** (Senha Alterada)
   - **Tipo**: BooleanField
   - **Padrão**: `False`
   - **Propósito**: Força troca de senha no primeiro login
   - **Fluxo**: 
     - Novo usuário → `password_changed = False`
     - Primeiro login → Redirecionado para trocar senha
     - Após troca → `password_changed = True`

4. **`email`** (Email)
   - **Tipo**: EmailField
   - **Único**: Sim (unique=True)
   - **USERNAME_FIELD**: Sim (usado para login)
   - **Obrigatório**: Sim

---

## 🔑 Sistema de Autenticação

### Backend Customizado

O sistema usa um backend de autenticação personalizado que permite login com **email** ao invés de username:

```python
# settings.py
AUTHENTICATION_BACKENDS = [
    'app.backends.EmailBackend',  # Primeiro (prioridade)
    'django.contrib.auth.backends.ModelBackend',  # Fallback
]
```

### EmailBackend

```python
class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Busca usuário por email (não por username)
        user = User.objects.get(email=username)
        # Verifica senha e se pode autenticar
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
```

### Fluxo de Login

1. Usuário informa **email** e **senha**
2. Sistema busca usuário pelo email
3. Valida senha
4. Verifica `user.is_active`
5. Registra login no `AccessLog`
6. Verifica `password_changed`
7. Redireciona:
   - Se `password_changed = False` → `/change-password/`
   - Se Admin → Dashboard (`/`)
   - Se Tesoureiro → Lista de Transações (`/transactions/`)

---

## 👥 Roles (Funções) e Permissões

### 1. Superuser
- **Acesso**: Django Admin (apenas)
- **Criação**: Manual ou via script
- **Características**:
  - `is_superuser = True`
  - `is_staff = True`
  - Acesso total ao sistema
  - **Exceção especial**: `vwtechdev@gmail.com` não tem logs de acesso salvos

### 2. Administrador (`admin`)
- **Role**: `role = 'admin'`
- **Permissões**:
  - ✅ Dashboard completo
  - ✅ Todas as transações (sem restrição)
  - ✅ Gestão de todos os recursos:
    - Campos, Igrejas, Pastores, Usuários
    - Categorias, Transações
    - Notificações
    - Logs de acesso
  - ✅ Visualização de todos os campos e igrejas
  - ❌ Não tem acesso ao Django Admin (apenas superuser)

### 3. Tesoureiro (`treasurer`)
- **Role**: `role = 'treasurer'`
- **Permissões**:
  - ✅ Lista de transações (apenas próprias)
  - ✅ Criar/editar/excluir transações próprias
  - ✅ Filtros limitados aos campos atribuídos
  - ✅ Visualização apenas de igrejas dos seus campos
  - ❌ Sem acesso ao dashboard
  - ❌ Sem gestão de recursos (campos, igrejas, usuários, etc.)
  - ❌ Sem acesso a logs de acesso

### Decorators de Permissão

```python
@admin_required          # Apenas administradores
@treasurer_required      # Apenas tesoureiros
@admin_or_treasurer_required  # Admin OU tesoureiro
@password_changed_required     # Força troca de senha
```

---

## 🛡️ Sistema de Segurança

### 1. Troca de Senha Obrigatória

**Fluxo:**
1. Novo usuário criado com `password_changed = False`
2. Senha padrão: `nations123456`
3. Primeiro login → Redirecionado para `/change-password/`
4. Usuário não pode acessar outras páginas até trocar
5. Após troca → Logout automático
6. Login novamente com nova senha
7. `password_changed = True`

**Implementação:**
- Decorator `@password_changed_required` em todas as views protegidas
- Middleware verifica antes de processar requisições

### 2. Restrição de Acesso ao Django Admin

**Middleware**: `AdminAccessMiddleware`
- Bloqueia acesso ao `/admin/` para todos exceto superusers
- Administradores e tesoureiros são redirecionados

### 3. Logs de Acesso

**Modelo**: `AccessLog`
- Registra todos os logins e logouts
- Campos: `user`, `action`, `timestamp`, `ip_address`
- **Exceção**: `vwtechdev@gmail.com` não tem logs salvos

---

## 📝 Criação e Gestão de Usuários

### Criação de Novo Usuário

**Formulário**: `UserForm`

**Campos obrigatórios:**
- `first_name` (Nome)
- `last_name` (Sobrenome)
- `email` (Email - único)
- `role` (Função)

**Processo automático:**
1. `username` gerado automaticamente: `{first_name.lower()}{last_name.lower()}`
   - Exemplo: "João Silva" → `joaosilva`
   - Se já existe: `joaosilva1`, `joaosilva2`, etc.
2. Senha padrão: `nations123456`
3. `password_changed = False` (força troca no primeiro login)
4. Campos (fields) atribuídos via ManyToMany (apenas na edição)

**Restrições:**
- Administradores só podem criar **tesoureiros** (forçado no código)
- Email deve ser único
- Validação de email no formulário

### Edição de Usuário

**Permissões:**
- Apenas administradores podem editar
- Não pode editar `vwtechdev@gmail.com`
- Campos (fields) podem ser atribuídos/removidos via checkbox table

### Reset de Senha

**Funcionalidade**: `user_reset_password`
- Admin pode resetar senha de qualquer usuário
- Nova senha: `nations123456`
- `password_changed = False` (força troca novamente)
- Não pode resetar `vwtechdev@gmail.com`

### Ativação/Desativação

**Funcionalidades**: `user_activate`, `user_delete`
- Desativar: `is_active = False`
- Reativar: `is_active = True`
- Usuário desativado não pode fazer login
- Não pode desativar `vwtechdev@gmail.com`

### Exclusão de Listagens

**Especial**: `vwtechdev@gmail.com`
- Excluído de todas as listagens de usuários
- Não pode ser editado, desativado ou ter senha resetada
- Não tem logs de acesso salvos

---

## 🌍 Sistema de Campos (Fields)

### Conceito
- **Campos** = Divisões geográficas/regiões
- Cada usuário pode ter acesso a múltiplos campos
- Relacionamento: ManyToMany (`User.fields`)

### Uso

**Para Administradores:**
- Veem todos os campos
- Filtros não são restritivos

**Para Tesoureiros:**
- Veem apenas campos atribuídos
- Filtros limitados aos seus campos
- Transações apenas de igrejas dos seus campos

### Métodos do Modelo

```python
user.get_fields()           # Retorna QuerySet de campos
user.has_field(field)        # Verifica se tem acesso a um campo
```

---

## 🔧 Configurações Importantes

### Settings.py

```python
# Modelo de usuário customizado
AUTH_USER_MODEL = 'app.User'

# Backends de autenticação
AUTHENTICATION_BACKENDS = [
    'app.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# URLs de autenticação
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'login'
```

### URLs de Usuários

```python
/users/                    # Lista de usuários
/users/create/             # Criar usuário
/users/<id>/edit/         # Editar usuário
/users/<id>/delete/        # Desativar usuário
/users/<id>/activate/     # Reativar usuário
/users/<id>/reset-password/  # Resetar senha
```

---

## 📊 Dados Iniciais

### Usuários Padrão

O comando `create_initial_data` cria **18 usuários** iniciais:

**Administradores (2):**
1. `Israelbruna0@gmail.com` - Bruna dos Santos Colaço (superuser)
2. `Lirian.floriano2018@gmail.com` - Lirian Nara Floriano de Lima (superuser)

**Tesoureiros (16):**
- Vários tesoureiros com acesso a campos específicos
- Senha padrão: `nations123456`
- Alguns com `password_changed = True`, outros com `False`

### Atribuições de Campos

Usuários têm campos atribuídos via ManyToMany:
- Exemplo: Jamille → Canoinhas, Porto União, Três Barras
- Exemplo: Marco → São Paulo, Curitiba

---

## 🔐 Senhas Padrão

### Criação de Usuário
- **Senha padrão**: `nations123456`
- **Senha inicial**: Criada via `make_password('nations123456')`
- **Força troca**: Sim (`password_changed = False`)

### Reset de Senha
- **Nova senha**: `nations123456`
- **Força troca**: Sim (`password_changed = False`)

### ⚠️ Segurança
- **IMPORTANTE**: Senhas padrão devem ser alteradas no primeiro login
- Documentação menciona senhas padrão (devem ser alteradas em produção)

---

## 📋 Resumo das Configurações

| Aspecto | Configuração |
|---------|--------------|
| **Autenticação** | Email (USERNAME_FIELD) |
| **Backend** | EmailBackend + ModelBackend |
| **Roles** | admin, treasurer |
| **Campos** | ManyToMany com Field |
| **Troca de Senha** | Obrigatória no primeiro login |
| **Senha Padrão** | `nations123456` |
| **Admin Django** | Apenas superusers |
| **Logs de Acesso** | Automáticos (exceto vwtechdev@gmail.com) |
| **Criação de Usuários** | Apenas administradores |
| **Username** | Gerado automaticamente |

---

## 🎯 Fluxo Completo de Usuário

### 1. Criação
```
Admin cria usuário → 
Username gerado automaticamente → 
Senha padrão (nations123456) → 
password_changed = False → 
Campos atribuídos (opcional)
```

### 2. Primeiro Login
```
Usuário faz login com email/senha → 
Sistema verifica password_changed → 
Redireciona para /change-password/ → 
Usuário troca senha → 
Logout automático → 
Login novamente
```

### 3. Login Normal
```
Usuário faz login → 
password_changed = True → 
Redireciona baseado no role:
  - Admin → Dashboard (/)
  - Tesoureiro → Transações (/transactions/)
```

### 4. Acesso ao Sistema
```
Admin → Acesso completo
Tesoureiro → Apenas transações próprias + campos atribuídos
```

---

## 🔍 Exemplos de Uso

### Verificar se usuário é admin
```python
if user.is_admin():
    # Código para admin
```

### Verificar se usuário tem acesso a campo
```python
if user.has_field(field):
    # Usuário tem acesso
```

### Obter campos do usuário
```python
fields = user.get_fields()  # QuerySet de Field
```

### Criar novo usuário (programaticamente)
```python
user = User.objects.create_user(
    email='novo@example.com',
    username='joaosilva',
    first_name='João',
    last_name='Silva',
    role='treasurer',
    password='nations123456'
)
user.password_changed = False
user.fields.add(field1, field2)
user.save()
```

---

## ⚠️ Pontos de Atenção

1. **Senha Padrão**: `nations123456` é conhecida - deve ser alterada
2. **Username**: Gerado automaticamente, pode não ser intuitivo
3. **Email Único**: Não pode haver dois usuários com mesmo email
4. **Superuser Especial**: `vwtechdev@gmail.com` tem tratamento especial
5. **Criação de Admin**: Código força criação apenas de tesoureiros
6. **ManyToMany Fields**: Só pode ser atribuído na edição (não na criação)

---

## 📚 Arquivos Relacionados

- **Modelo**: `app/models.py` (classe User)
- **Formulário**: `app/forms.py` (UserForm)
- **Views**: `app/views.py` (user_*)
- **Backend**: `app/backends.py` (EmailBackend)
- **Decorators**: `app/decorators.py` (permissões)
- **Admin**: `app/admin.py` (CustomUserAdmin)
- **Settings**: `core/settings.py` (AUTH_USER_MODEL, backends)
- **Comando**: `app/management/commands/create_initial_data.py`

---

**Última atualização**: 2024
