# Proposta: Implementação do Role Supervisor

## 📋 Objetivo

Adicionar um novo role **Supervisor** que pode visualizar transações de Tesoureiros, mas apenas daqueles que compartilham os mesmos campos (regiões) que o Supervisor.

## 🎯 Requisitos

- Supervisor pode ver **suas próprias transações**
- Supervisor pode ver transações de **Tesoureiros** que compartilham campos
- Supervisor pode **criar transações**
- Supervisor **NÃO** pode **editar/excluir transações** (nem suas próprias)
- Transações de tesoureiros devem ser de **igrejas dos campos do Supervisor**
- Tesoureiros devem ter **pelo menos um campo em comum** com o Supervisor
- Supervisor **NÃO** pode ver transações de outros Supervisores ou Admins
- **Tesoureiro** pode criar e visualizar suas próprias transações, mas **NÃO pode editar/excluir**

## 🔧 Implementação Proposta

### 1. Atualizar Modelo User

**Arquivo**: `app/models.py`

```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('treasurer', 'Tesoureiro'),
        ('supervisor', 'Supervisor'),  # NOVO
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='treasurer', verbose_name="Função")
    # ... resto do código
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_treasurer(self):
        return self.role == 'treasurer'
    
    def is_supervisor(self):  # NOVO
        return self.role == 'supervisor'
    
    def can_view_treasurer_transactions(self, treasurer):
        """
        Verifica se o supervisor pode ver transações de um tesoureiro específico.
        Retorna True se compartilham pelo menos um campo.
        """
        if not self.is_supervisor():
            return False
        if not treasurer.is_treasurer():
            return False
        # Verifica interseção de campos
        supervisor_fields = set(self.fields.values_list('id', flat=True))
        treasurer_fields = set(treasurer.fields.values_list('id', flat=True))
        return bool(supervisor_fields & treasurer_fields)
```

### 2. Criar Função Helper para Query de Transações

**Arquivo**: `app/views.py` (ou criar `app/utils.py`)

```python
def get_transactions_for_user(user):
    """
    Retorna QuerySet de transações baseado no role do usuário.
    
    - Admin: Todas as transações
    - Tesoureiro: Apenas suas próprias transações
    - Supervisor: Transações de tesoureiros que compartilham campos
    """
    if user.is_admin():
        return Transaction.objects.all()
    
    elif user.is_treasurer():
        return Transaction.objects.filter(user=user)
    
    elif user.is_supervisor():
        # Obter campos do supervisor
        supervisor_fields = user.fields.all()
        
        if not supervisor_fields.exists():
            return Transaction.objects.none()
        
        # Obter igrejas dos campos do supervisor
        supervisor_churches = Church.objects.filter(field__in=supervisor_fields)
        
        # Obter tesoureiros que compartilham pelo menos um campo com o supervisor
        treasurer_ids = User.objects.filter(
            role='treasurer',
            fields__in=supervisor_fields
        ).distinct().values_list('id', flat=True)
        
        # Retornar: transações próprias + transações de tesoureiros em igrejas dos campos do supervisor
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

### 3. Atualizar Views

#### 3.1 Dashboard (index)

**Arquivo**: `app/views.py` (função `index`)

```python
@password_changed_required
def index(request):
    """Dashboard principal - Admin e Supervisor"""
    # Redirecionar tesoureiros para a lista de transações
    if request.user.is_treasurer():
        return redirect('transaction_list')
    
    # Admin e Supervisor podem acessar o dashboard
    if not (request.user.is_admin() or request.user.is_supervisor()):
        return redirect('transaction_list')
    
    # ... código de filtros ...
    
    # Base de transações
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    elif request.user.is_supervisor():
        base_transactions = get_transactions_for_user(request.user)
    else:
        base_transactions = Transaction.objects.none()
    
    # ... resto do código ...
```

#### 3.2 Lista de Transações (transaction_list)

**Arquivo**: `app/views.py` (função `transaction_list`)

```python
@password_changed_required
@admin_or_treasurer_required  # ATUALIZAR para incluir supervisor
def transaction_list(request):
    """Lista de transações"""
    if request.user.is_admin():
        transactions = Transaction.objects.all()
    elif request.user.is_supervisor():
        transactions = get_transactions_for_user(request.user)
    else:
        # Tesoureiro: ver apenas transações criadas por ele
        transactions = Transaction.objects.filter(user=request.user)
    
    # ... resto do código ...
```

#### 3.3 API de Transações (transaction_list_api)

**Arquivo**: `app/views.py` (função `transaction_list_api`)

```python
@password_changed_required
@admin_or_treasurer_required  # ATUALIZAR para incluir supervisor
def transaction_list_api(request):
    """API JSON para lista de transações"""
    if request.user.is_admin():
        transactions = Transaction.objects.all()
    elif request.user.is_supervisor():
        transactions = get_transactions_for_user(request.user)
    else:
        transactions = Transaction.objects.filter(user=request.user)
    
    # ... resto do código ...
```

#### 3.4 Resumo de Transações (transaction_summary_api)

**Arquivo**: `app/views.py` (função `transaction_summary_api`)

```python
@password_changed_required
@admin_or_treasurer_required  # ATUALIZAR para incluir supervisor
def transaction_summary_api(request):
    """API de resumo para dashboard"""
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    elif request.user.is_supervisor():
        base_transactions = get_transactions_for_user(request.user)
    else:
        if request.user.fields.exists():
            user_churches = Church.objects.filter(field__in=request.user.fields.all())
            base_transactions = Transaction.objects.filter(church__in=user_churches)
        else:
            return JsonResponse({'error': 'Usuário sem campos associados'}, status=400)
    
    # ... resto do código ...
```

#### 3.5 Exportação PDF/XLSX

**Arquivo**: `app/views.py` (funções `transaction_export_pdf` e `transaction_export_xlsx`)

```python
@password_changed_required
@admin_or_treasurer_required  # ATUALIZAR para incluir supervisor
def transaction_export_pdf(request):
    """Exportar transações para PDF"""
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    elif request.user.is_supervisor():
        base_transactions = get_transactions_for_user(request.user)
    else:
        base_transactions = Transaction.objects.filter(user=request.user)
    
    # ... resto do código ...
```

### 4. Atualizar Decorators

**Arquivo**: `app/decorators.py`

```python
def admin_or_treasurer_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_admin() or request.user.is_treasurer() or request.user.is_supervisor()):
            messages.error(request, 'Acesso negado. Você não tem permissão para acessar esta página.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# NOVO: Decorator específico para Supervisor
def supervisor_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_supervisor():
            messages.error(request, 'Acesso negado. Apenas supervisores podem acessar esta página.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# NOVO: Admin ou Supervisor
def admin_or_supervisor_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_admin() or request.user.is_supervisor()):
            messages.error(request, 'Acesso negado. Apenas administradores ou supervisores podem acessar esta página.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
```

### 5. Atualizar Formulário de Usuário

**Arquivo**: `app/forms.py`

```python
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'fields']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'fields': CheckboxTableWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # ... código existente ...
        
        # Se for um novo usuário (sem instância), remover o campo fields
        if not self.instance or not self.instance.pk:
            del self.fields['fields']
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        # Validar que Supervisor precisa ter campos atribuídos (apenas na edição)
        if role == 'supervisor' and self.instance and self.instance.pk:
            if not self.instance.fields.exists():
                raise ValidationError('Supervisor deve ter pelo menos um campo atribuído.')
        
        # ... resto do código ...
```

### 6. Atualizar Views de Criação/Edição de Usuário

**Arquivo**: `app/views.py`

```python
@password_changed_required
@admin_required
def user_create(request):
    """Criar novo usuário"""
    if request.method == 'POST':
        form = UserForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            # Administradores podem criar tesoureiros ou supervisores
            # Mas não podem criar outros admins (manter restrição se necessário)
            if user.role == 'admin':
                user.role = 'treasurer'  # Forçar tesoureiro
            user.save()
            
            # Salvar campos many-to-many se houver
            form.save()
            
            messages.success(request, f'Usuário {user.get_full_name()} criado com sucesso!')
            return redirect('user_list')
    # ... resto do código ...
```

### 7. Atualizar Lista de Usuários

**Arquivo**: `app/views.py` (função `user_list`)

```python
def user_list(request):
    """Lista de usuários"""
    users = User.objects.all()
    
    # Excluir o usuário vwtechdev@gmail.com da lista
    users = users.exclude(email='vwtechdev@gmail.com')
    
    # Busca por nome, email ou função
    search_query = request.GET.get('search', '').strip()
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(role__icontains=search_query)
        )
    
    # ... resto do código ...
```

### 8. Atualizar Templates

**Arquivo**: `app/templates/pages/user_list.html`

Adicionar "Supervisor" na exibição de roles.

**Arquivo**: `app/templates/pages/user_form.html`

O formulário já deve funcionar com o novo role, mas verificar se há validações específicas.

### 9. Atualizar Admin Django

**Arquivo**: `app/admin.py`

```python
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'get_fields_display', 'is_active']
    list_filter = ['role', 'fields', 'is_active']  # Já inclui role
    # ... resto do código ...
```

### 10. Migração do Banco de Dados

**Criar migration**:

```bash
python manage.py makemigrations
```

Isso criará uma migration para adicionar o novo choice `'supervisor'` no campo `role`.

### 11. Atualizar Redirecionamento de Login

**Arquivo**: `app/views.py` (função `login_view`)

```python
def login_view(request):
    if request.user.is_authenticated:
        # Redirecionar tesoureiros para a lista de transações
        if request.user.is_treasurer():
            return redirect('transaction_list')
        # Admin e Supervisor vão para o dashboard
        return redirect('index')
    
    # ... resto do código ...
    
    if form.is_valid():
        # ... código de autenticação ...
        
        # Verifica se o usuário precisa trocar a senha
        if not user.password_changed:
            return render(request, 'registration/redirect_to_change_password.html', {
                'title': 'Redirecionando...',
                'user': user
            })
        
        # Redirecionar baseado no role
        if user.is_treasurer():
            return redirect('transaction_list')
        else:
            # Admin ou Supervisor vão para o dashboard
            return redirect('index')
```

## 📊 Permissões Resumidas

| Ação | Admin | Supervisor | Tesoureiro |
|------|-------|------------|------------|
| Ver todas transações | ✅ | ❌ | ❌ |
| Ver transações próprias | ✅ | ✅ | ✅ |
| Ver transações de tesoureiros (mesmos campos) | ✅ | ✅ | ❌ |
| Dashboard | ✅ | ✅ | ❌ |
| Gestão de recursos | ✅ | ❌ | ❌ |
| Criar transações | ✅ | ✅ | ✅ |
| Editar transações | ✅ | ❌ | ❌ |
| Excluir transações | ✅ | ❌ | ❌ |

## 🔍 Lógica de Filtro do Supervisor

```
Supervisor com campos: [Campo A, Campo B]

Pode ver transações de:
- Tesoureiro X (tem Campo A ou Campo B)
- Em igrejas de Campo A ou Campo B
- Criadas por Tesoureiro X

NÃO pode ver:
- Transações de outros Supervisores
- Transações de Admins
- Transações de Tesoureiros sem campos em comum
- Transações de igrejas fora de seus campos
```

## 🧪 Casos de Teste

1. **Supervisor com Campo A** pode ver transações de **Tesoureiro com Campo A** em **Igreja do Campo A** ✅
2. **Supervisor com Campo A** NÃO pode ver transações de **Tesoureiro com Campo B** ❌
3. **Supervisor com Campo A e B** pode ver transações de **Tesoureiro com Campo A** ✅
4. **Supervisor com Campo A e B** pode ver transações de **Tesoureiro com Campo B** ✅
5. **Supervisor** NÃO pode ver transações de **Admin** ❌
6. **Supervisor** NÃO pode ver transações de **outro Supervisor** ❌

## 🚀 Ordem de Implementação

1. ✅ Atualizar modelo User (adicionar role e método)
2. ✅ Criar migration
3. ✅ Criar função helper `get_transactions_for_user`
4. ✅ Atualizar decorators
5. ✅ Atualizar todas as views que filtram transações
6. ✅ Atualizar formulários
7. ✅ Atualizar templates
8. ✅ Testar fluxo completo
9. ✅ Atualizar documentação

## 📝 Notas Importantes

- **Campos obrigatórios**: Supervisor DEVE ter pelo menos um campo atribuído
- **Validação**: Adicionar validação no formulário para garantir campos
- **Performance**: A query do Supervisor pode ser otimizada com `select_related` e `prefetch_related`
- **Logs**: Considerar se Supervisor deve ter logs de acesso diferentes

## 🔄 Compatibilidade

- ✅ Compatível com estrutura existente
- ✅ Não quebra funcionalidades atuais
- ✅ Backward compatible (role padrão continua sendo 'treasurer')

---

**Pronto para implementação!** 🚀
