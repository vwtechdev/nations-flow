# Sistema de Permissões

## Visão Geral

O Nations Flow implementa um sistema de permissões baseado em **roles (funções)** com controle de acesso granular por campo e funcionalidade.

## Roles (Funções)

### 1. Administrador (`admin`)

**Características:**
- Acesso completo ao sistema
- Pode gerenciar todos os recursos
- Acesso ao dashboard
- Pode criar, editar e excluir qualquer transação
- Pode gerenciar usuários, campos, igrejas, pastores e categorias
- Acesso a logs de acesso
- Pode criar lembretes em transações

**Permissões Específicas:**
- ✅ Dashboard completo
- ✅ Todas as transações (criar, editar, excluir, visualizar)
- ✅ Gerenciar usuários (criar, editar, desativar, reativar, resetar senha)
- ✅ Gerenciar campos, igrejas, pastores, categorias
- ✅ Visualizar logs de acesso
- ✅ Criar notificações
- ✅ Exportar relatórios (PDF, Excel)
- ✅ Filtros completos (incluindo filtro por usuário)

---

### 2. Tesoureiro (`treasurer`)

**Características:**
- Acesso limitado às transações
- Pode criar e visualizar apenas suas próprias transações
- Não pode editar ou excluir transações
- Acesso restrito aos campos associados ao usuário

**Permissões Específicas:**
- ❌ Dashboard (redirecionado para lista de transações)
- ✅ Criar transações (apenas em seus campos)
- ✅ Visualizar suas próprias transações
- ❌ Editar transações
- ❌ Excluir transações
- ✅ Exportar relatórios (apenas suas transações)
- ❌ Gerenciar usuários, campos, igrejas, pastores, categorias
- ❌ Logs de acesso
- ❌ Notificações
- ✅ Filtros limitados (sem filtro por usuário)

**Restrições:**
- Ve apenas campos associados ao seu perfil
- Ve apenas igrejas dos seus campos
- Não pode criar lembretes

---

### 3. Supervisor (`supervisor`)

**Características:**
- Acesso intermediário entre Admin e Tesoureiro
- Pode visualizar suas próprias transações
- Pode visualizar transações de tesoureiros que compartilham os mesmos campos
- Não pode editar ou excluir transações
- Acesso restrito aos campos associados

**Permissões Específicas:**
- ❌ Dashboard (redirecionado para lista de transações)
- ✅ Criar transações (apenas em seus campos)
- ✅ Visualizar suas próprias transações
- ✅ Visualizar transações de tesoureiros dos mesmos campos
- ❌ Editar transações
- ❌ Excluir transações
- ✅ Exportar relatórios (suas transações + tesoureiros dos mesmos campos)
- ❌ Gerenciar usuários, campos, igrejas, pastores, categorias
- ❌ Logs de acesso
- ❌ Notificações
- ✅ Filtros limitados (pode filtrar por usuário: ele mesmo ou tesoureiros dos mesmos campos)

**Lógica de Acesso:**
- Supervisor vê transações de tesoureiros que:
  1. Têm pelo menos um campo em comum com o supervisor
  2. As transações são de igrejas dos campos compartilhados

---

## Decorators de Permissão

### `@admin_required`

**Localização**: `app/decorators.py`

**Funcionalidade:**
- Restringe acesso apenas para administradores
- Redireciona outros usuários para o dashboard com mensagem de erro

**Uso:**
```python
@admin_required
def minha_view(request):
    # Apenas admins podem acessar
    pass
```

**Views que usam:**
- Gerenciamento de categorias, campos, igrejas, pastores, usuários
- Edição e exclusão de transações
- Logs de acesso
- Notificações

---

### `@treasurer_required`

**Localização**: `app/decorators.py`

**Funcionalidade:**
- Restringe acesso apenas para tesoureiros
- Redireciona outros usuários para o dashboard

**Uso:**
```python
@treasurer_required
def minha_view(request):
    # Apenas tesoureiros podem acessar
    pass
```

**Nota**: Atualmente não é usado no código, mas está disponível.

---

### `@admin_or_treasurer_required`

**Localização**: `app/decorators.py`

**Funcionalidade:**
- Permite acesso para Admin, Tesoureiro ou Supervisor
- Redireciona outros usuários para o dashboard

**Uso:**
```python
@admin_or_treasurer_required
def minha_view(request):
    # Admin, Tesoureiro ou Supervisor podem acessar
    pass
```

**Views que usam:**
- Lista de transações
- Criação de transações
- Visualização de transações
- Exportação de relatórios

---

### `@password_changed_required`

**Localização**: `app/decorators.py`

**Funcionalidade:**
- Verifica se o usuário já trocou a senha
- Redireciona para `/change-password/` se `password_changed=False`
- Usado em conjunto com outros decorators

**Uso:**
```python
@password_changed_required
@admin_required
def minha_view(request):
    # Requer senha alterada E ser admin
    pass
```

**Views que usam:**
- Praticamente todas as views autenticadas

---

## Controle de Acesso por Campo

### Associação de Campos

- Usuários (exceto admin) têm campos associados via `ManyToManyField`
- Admin tem acesso a todos os campos
- Tesoureiro e Supervisor veem apenas seus campos

### Filtros Baseados em Campos

**Em Views:**
```python
if request.user.is_admin():
    fields = Field.objects.all()
else:
    fields = request.user.fields.all()
```

**Em Formulários:**
```python
if user.is_treasurer():
    self.fields['field'].queryset = user.fields.all()
else:
    self.fields['field'].queryset = Field.objects.all()
```

---

## Função `get_transactions_for_user(user)`

**Localização**: `app/views.py`

**Funcionalidade:**
Retorna QuerySet de transações baseado no role do usuário.

**Lógica:**

```python
def get_transactions_for_user(user):
    if user.is_admin():
        # Admin: todas as transações
        return Transaction.objects.all()
    
    elif user.is_treasurer():
        # Tesoureiro: apenas suas transações
        return Transaction.objects.filter(user=user)
    
    elif user.is_supervisor():
        # Supervisor: suas transações + transações de tesoureiros dos mesmos campos
        supervisor_fields = user.fields.all()
        supervisor_churches = Church.objects.filter(field__in=supervisor_fields)
        treasurer_ids = User.objects.filter(
            role='treasurer',
            fields__in=supervisor_fields
        ).distinct().values_list('id', flat=True)
        
        return Transaction.objects.filter(
            Q(user=user) |  # Suas próprias transações
            Q(
                user_id__in=treasurer_ids,
                church__in=supervisor_churches
            )  # Transações de tesoureiros dos mesmos campos
        ).distinct()
    
    else:
        return Transaction.objects.none()
```

**Uso:**
- Lista de transações
- API de transações
- Exportação de relatórios
- Dashboard (para supervisores)

---

## Middleware de Acesso

### AdminAccessMiddleware

**Localização**: `app/middleware.py`

**Funcionalidade:**
- Bloqueia acesso ao painel `/admin/` para todos os usuários exceto superusuários
- Mesmo administradores (`role='admin'`) não têm acesso
- Apenas superusuários (`is_superuser=True`) podem acessar

**Comportamento:**
```python
if request.path.startswith('/admin/'):
    if not request.user.is_authenticated:
        return None  # Django lida com login
    
    if request.user.is_superuser:
        return None  # Permite acesso
    
    # Todos os outros são bloqueados
    messages.error(request, 'Apenas superusuários têm acesso ao painel de administração.')
    return redirect('index')
```

---

## Proteções Especiais

### Usuário `vwtechdev@gmail.com`

Este usuário tem proteções especiais:

- ❌ Não aparece em listagens de usuários
- ❌ Não pode ser editado
- ❌ Não pode ser desativado
- ❌ Não pode ter senha resetada
- ❌ Logs de acesso não são salvos (método `save()` sobrescrito em `AccessLog`)

**Implementação:**
```python
# Em views de usuários
users = users.exclude(email='vwtechdev@gmail.com')

# Em AccessLog.save()
if self.user.email == 'vwtechdev@gmail.com':
    return  # Não salva log
```

---

## Fluxo de Autenticação

### 1. Login
```
POST /login/
  → EmailAuthenticationForm valida email
  → EmailBackend autentica
  → Login registrado no AccessLog
  → Verifica password_changed
    → Se False: redireciona para /change-password/
    → Se True: redireciona conforme role
```

### 2. Acesso a View
```
Request
  → Middleware (AdminAccessMiddleware)
  → Decorator @login_required
  → Decorator @password_changed_required
  → Decorator de role (@admin_required, etc.)
  → View
```

### 3. Filtros de Dados
```
View
  → Verifica role do usuário
  → Aplica filtros baseados em campos
  → Retorna dados filtrados
```

---

## Exemplos de Uso

### Exemplo 1: Lista de Transações

```python
@password_changed_required
@admin_or_treasurer_required
def transaction_list(request):
    if request.user.is_admin():
        transactions = Transaction.objects.all()
    elif request.user.is_supervisor():
        transactions = get_transactions_for_user(request.user)
    else:
        transactions = Transaction.objects.filter(user=request.user)
    
    # Aplicar filtros...
    return render(request, 'pages/transaction_list.html', context)
```

### Exemplo 2: Criar Transação

```python
@password_changed_required
@admin_or_treasurer_required
def transaction_create(request):
    form = TransactionForm(user=request.user)  # Passa usuário para filtrar campos
    
    if request.user.is_admin():
        fields = Field.objects.all()
    else:
        fields = request.user.fields.all()
    
    # Renderiza formulário com campos filtrados
```

### Exemplo 3: Dashboard (Apenas Admin)

```python
@password_changed_required
def index(request):
    if not request.user.is_admin():
        return redirect('transaction_list')  # Redireciona não-admins
    
    # Dashboard completo
```

---

## Boas Práticas

### 1. Sempre Verificar Permissões
- Use decorators apropriados
- Verifique role dentro da view se necessário
- Filtre dados baseado em permissões

### 2. Filtros Consistentes
- Use `get_transactions_for_user()` para transações
- Filtre campos, igrejas e pastores baseado em permissões
- Mantenha consistência entre views

### 3. Mensagens de Erro Claras
- Informe ao usuário por que o acesso foi negado
- Use Django Messages Framework

### 4. Segurança em Múltiplas Camadas
- Decorators (camada de view)
- Filtros de QuerySet (camada de dados)
- Validações no formulário (camada de apresentação)
