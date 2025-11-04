# Código para Implementação do Supervisor

## 1. Atualizar Modelo User

**Arquivo**: `app/models.py`

```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('treasurer', 'Tesoureiro'),
        ('supervisor', 'Supervisor'),  # ADICIONAR ESTA LINHA
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='treasurer', verbose_name="Função")
    fields = models.ManyToManyField(Field, blank=True, verbose_name="Campos")
    password_changed = models.BooleanField(default=False, verbose_name="Senha Alterada")
    
    # ... resto do código ...
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_treasurer(self):
        return self.role == 'treasurer'
    
    def is_supervisor(self):  # ADICIONAR ESTE MÉTODO
        return self.role == 'supervisor'
    
    # ... resto dos métodos ...
```

## 2. Criar Função Helper

**Arquivo**: `app/views.py` (adicionar no início, após imports)

```python
# ADICIONAR ESTA FUNÇÃO
def get_transactions_for_user(user):
    """
    Retorna QuerySet de transações baseado no role do usuário.
    
    - Admin: Todas as transações
    - Tesoureiro: Apenas suas próprias transações
    - Supervisor: Suas próprias transações + transações de tesoureiros que compartilham campos
    """
    if user.is_admin():
        return Transaction.objects.all()
    
    elif user.is_treasurer():
        return Transaction.objects.filter(user=user)
    
    elif user.is_supervisor():
        # Obter campos do supervisor
        supervisor_fields = user.fields.all()
        
        if not supervisor_fields.exists():
            # Se não tem campos, retorna apenas suas próprias transações
            return Transaction.objects.filter(user=user)
        
        # Obter igrejas dos campos do supervisor
        supervisor_churches = Church.objects.filter(field__in=supervisor_fields)
        
        # Obter tesoureiros que compartilham pelo menos um campo com o supervisor
        treasurer_ids = User.objects.filter(
            role='treasurer',
            fields__in=supervisor_fields
        ).distinct().values_list('id', flat=True)
        
        # Retornar: transações próprias + transações de tesoureiros em igrejas dos campos do supervisor
        # Nota: Q já deve estar importado no início do arquivo (from django.db.models import Q)
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

## 3. Atualizar View index (Dashboard)

**Arquivo**: `app/views.py` (função `index`)

**LOCALIZAR** (linha ~195):
```python
    # Base de transações (todos para admin, apenas do usuário para tesoureiro)
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    else:
        base_transactions = Transaction.objects.filter(user=request.user)
```

**SUBSTITUIR POR**:
```python
    # Base de transações
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    elif request.user.is_supervisor():
        base_transactions = get_transactions_for_user(request.user)
    else:
        base_transactions = Transaction.objects.filter(user=request.user)
```

**LOCALIZAR** (linha ~134):
```python
    # Redirecionar tesoureiros para a lista de transações
    if not request.user.is_admin():
        return redirect('transaction_list')
```

**SUBSTITUIR POR**:
```python
    # Redirecionar tesoureiros para a lista de transações
    if request.user.is_treasurer():
        return redirect('transaction_list')
    
    # Admin e Supervisor podem acessar o dashboard
    if not (request.user.is_admin() or request.user.is_supervisor()):
        return redirect('transaction_list')
```

## 4. Atualizar View transaction_list

**Arquivo**: `app/views.py` (função `transaction_list`)

**LOCALIZAR** (linha ~429):
```python
    if request.user.is_admin():
        transactions = Transaction.objects.all()
    else:
        # Tesoureiro: ver apenas transações criadas por ele
        transactions = Transaction.objects.filter(user=request.user)
```

**SUBSTITUIR POR**:
```python
    if request.user.is_admin():
        transactions = Transaction.objects.all()
    elif request.user.is_supervisor():
        transactions = get_transactions_for_user(request.user)
    else:
        # Tesoureiro: ver apenas transações criadas por ele
        transactions = Transaction.objects.filter(user=request.user)
```

## 5. Atualizar View transaction_list_api

**Arquivo**: `app/views.py` (função `transaction_list_api`)

**LOCALIZAR** (linha ~569):
```python
    if request.user.is_admin():
        transactions = Transaction.objects.all()
        print(f"DEBUG API - Usuário admin: {transactions.count()} transações totais")
    else:
        # Tesoureiro: ver apenas transações criadas por ele
        transactions = Transaction.objects.filter(user=request.user)
        print(f"DEBUG API - Usuário tesoureiro: {transactions.count()} transações do próprio usuário")
```

**SUBSTITUIR POR**:
```python
    if request.user.is_admin():
        transactions = Transaction.objects.all()
        print(f"DEBUG API - Usuário admin: {transactions.count()} transações totais")
    elif request.user.is_supervisor():
        transactions = get_transactions_for_user(request.user)
        print(f"DEBUG API - Usuário supervisor: {transactions.count()} transações de tesoureiros")
    else:
        # Tesoureiro: ver apenas transações criadas por ele
        transactions = Transaction.objects.filter(user=request.user)
        print(f"DEBUG API - Usuário tesoureiro: {transactions.count()} transações do próprio usuário")
```

## 6. Atualizar View transaction_summary_api

**Arquivo**: `app/views.py` (função `transaction_summary_api`)

**LOCALIZAR** (linha ~707):
```python
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    else:
        if request.user.fields.exists():
            user_churches = Church.objects.filter(field__in=request.user.fields.all())
            base_transactions = Transaction.objects.filter(church__in=user_churches)
        else:
            return JsonResponse({'error': 'Usuário sem campos associados'}, status=400)
```

**SUBSTITUIR POR**:
```python
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    elif request.user.is_supervisor():
        base_transactions = get_transactions_for_user(request.user)
        if not base_transactions.exists() and not request.user.fields.exists():
            return JsonResponse({'error': 'Supervisor sem campos associados'}, status=400)
    else:
        if request.user.fields.exists():
            user_churches = Church.objects.filter(field__in=request.user.fields.all())
            base_transactions = Transaction.objects.filter(church__in=user_churches)
        else:
            return JsonResponse({'error': 'Usuário sem campos associados'}, status=400)
```

## 7. Atualizar View transaction_export_pdf

**Arquivo**: `app/views.py` (função `transaction_export_pdf`)

**LOCALIZAR** (linha ~1913):
```python
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    else:
        # Tesoureiro: exportar apenas transações criadas por ele
        base_transactions = Transaction.objects.filter(user=request.user)
```

**SUBSTITUIR POR**:
```python
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    elif request.user.is_supervisor():
        base_transactions = get_transactions_for_user(request.user)
    else:
        # Tesoureiro: exportar apenas transações criadas por ele
        base_transactions = Transaction.objects.filter(user=request.user)
```

## 8. Atualizar View transaction_export_xlsx

**Arquivo**: `app/views.py` (função `transaction_export_xlsx`)

**LOCALIZAR** (deve ter código similar ao PDF):
```python
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    else:
        base_transactions = Transaction.objects.filter(user=request.user)
```

**SUBSTITUIR POR**:
```python
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    elif request.user.is_supervisor():
        base_transactions = get_transactions_for_user(request.user)
    else:
        base_transactions = Transaction.objects.filter(user=request.user)
```

## 9. Atualizar Views de Transação (Editar, Excluir, Visualizar)

**Arquivo**: `app/views.py`

### 9.1 Atualizar transaction_view

**LOCALIZAR** (linha ~967):
```python
    # Verificar se o usuário tem acesso à transação
    if not request.user.is_admin():
        # Tesoureiros só podem ver transações de suas igrejas
        if not request.user.fields.filter(id=transaction.church.field.id).exists():
            messages.error(request, 'Você não tem permissão para visualizar esta transação.')
            return redirect('transaction_list')
```

**SUBSTITUIR POR**:
```python
    # Verificar se o usuário tem acesso à transação
    if not request.user.is_admin():
        # Supervisor e Tesoureiro: verificar se têm acesso
        if request.user.is_supervisor():
            # Supervisor pode ver suas próprias transações ou de tesoureiros dos mesmos campos
            supervisor_fields = request.user.fields.all()
            can_view = (
                transaction.user == request.user or  # Sua própria transação
                (
                    transaction.user.role == 'treasurer' and
                    transaction.user.fields.filter(id__in=supervisor_fields.values_list('id', flat=True)).exists() and
                    supervisor_fields.filter(id=transaction.church.field.id).exists()
                )
            )
        else:
            # Tesoureiro: apenas suas próprias transações
            can_view = transaction.user == request.user
        
        if not can_view:
            messages.error(request, 'Você não tem permissão para visualizar esta transação.')
            return redirect('transaction_list')
```

### 9.2 Manter transaction_edit apenas para Admin

**LOCALIZAR** (linha ~1004):
```python
@admin_required
def transaction_edit(request, pk):
    """Editar transação - Apenas administradores"""
```

**MANTER COMO ESTÁ** - Apenas Admin pode editar:
```python
@admin_required
def transaction_edit(request, pk):
    """Editar transação - Apenas administradores"""
    # ... código existente ...
```

### 9.3 Manter transaction_delete apenas para Admin

**LOCALIZAR** (linha ~1064):
```python
@admin_required
def transaction_delete(request, pk):
    """Excluir transação - Apenas administradores"""
```

**MANTER COMO ESTÁ** - Apenas Admin pode excluir:
```python
@admin_required
def transaction_delete(request, pk):
    """Excluir transação - Apenas administradores"""
    # ... código existente ...
```

## 10. Importar Q no início do arquivo views.py

**Arquivo**: `app/views.py`

**LOCALIZAR** (linha ~6):
```python
from django.db.models import Sum, Q, Count
```

Se `Q` já estiver importado, não precisa fazer nada. Caso contrário, adicionar.

## 11. Atualizar Decorator admin_or_treasurer_required

**Arquivo**: `app/decorators.py`

**LOCALIZAR**:
```python
def admin_or_treasurer_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_admin() or request.user.is_treasurer()):
            messages.error(request, 'Acesso negado. Você não tem permissão para acessar esta página.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
```

**SUBSTITUIR POR**:
```python
def admin_or_treasurer_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_admin() or request.user.is_treasurer() or request.user.is_supervisor()):
            messages.error(request, 'Acesso negado. Você não tem permissão para acessar esta página.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
```

## 12. Atualizar View login_view

**Arquivo**: `app/views.py` (função `login_view`)

**LOCALIZAR** (linha ~37):
```python
    if request.user.is_authenticated:
        # Redirecionar tesoureiros para a lista de transações
        if not request.user.is_admin():
            return redirect('transaction_list')
        return redirect('index')
```

**SUBSTITUIR POR**:
```python
    if request.user.is_authenticated:
        # Redirecionar tesoureiros para a lista de transações
        if request.user.is_treasurer():
            return redirect('transaction_list')
        # Admin e Supervisor vão para o dashboard
        return redirect('index')
```

**LOCALIZAR** (linha ~70):
```python
                # Redirecionar tesoureiros para a lista de transações
                if not user.is_admin():
                    return redirect('transaction_list')
                return redirect('index')
```

**SUBSTITUIR POR**:
```python
                # Redirecionar tesoureiros para a lista de transações
                if user.is_treasurer():
                    return redirect('transaction_list')
                # Admin ou Supervisor vão para o dashboard
                return redirect('index')
```

## 13. Atualizar Templates (Opcional mas Recomendado)

**Arquivo**: `app/templates/pages/transaction_list.html` e `app/static/js/transaction_list.js`

**IMPORTANTE**: Os botões de editar/excluir devem ser ocultos para Supervisor e Tesoureiro. Se o sistema renderiza os botões via JavaScript, verificar onde os botões são criados e adicionar condição:

```javascript
// No JavaScript que renderiza a tabela, adicionar verificação
const canEdit = userIsAdmin; // ou verificar role do usuário
const canDelete = userIsAdmin; // ou verificar role do usuário

// Ao renderizar botões de ação:
if (canEdit) {
    // Mostrar botão de editar
}
if (canDelete) {
    // Mostrar botão de excluir
}
```

**Alternativa**: Se os botões são renderizados no backend, adicionar no template:
```django
{% if user.is_admin %}
    <a href="{% url 'transaction_edit' transaction.id %}" class="btn btn-sm btn-primary">Editar</a>
    <a href="{% url 'transaction_delete' transaction.id %}" class="btn btn-sm btn-danger">Excluir</a>
{% endif %}
```

**Nota**: Como as views `transaction_edit` e `transaction_delete` já têm `@admin_required`, mesmo que os botões apareçam, o acesso será negado. Mas é melhor ocultar os botões para melhor UX.

## 14. Criar Migration

**Executar no terminal**:
```bash
cd /home/deploy/projects/nations-flow
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## 15. Testar

Após implementar, testar:

1. ✅ Criar um usuário Supervisor com campos atribuídos
2. ✅ Criar uma transação como Supervisor (deve funcionar)
3. ✅ Verificar se vê suas próprias transações
4. ✅ Verificar se vê transações de tesoureiros dos mesmos campos
5. ✅ Verificar se NÃO vê transações de outros supervisores
6. ✅ Verificar se NÃO vê transações de admins
7. ✅ Verificar se NÃO pode editar/excluir transações (botões não devem aparecer)
8. ✅ Verificar dashboard funciona para supervisor
9. ✅ Verificar exportação PDF/XLSX funciona
10. ✅ Testar como Tesoureiro: criar transação OK, editar/excluir NÃO deve funcionar

---

**Nota**: Todos os arquivos devem ser atualizados seguindo esta ordem para evitar erros.
