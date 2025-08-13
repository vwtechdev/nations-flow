from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db.models import Sum, Q
from django.http import JsonResponse, HttpResponse

from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import Church, User, Field, Category, Transaction
from .forms import (
    ChurchForm, UserForm, FieldForm, 
    CategoryForm, TransactionForm, ChangePasswordForm, EmailAuthenticationForm
)
from .decorators import admin_required, treasurer_required, admin_or_treasurer_required, password_changed_required
from calendar import monthrange

# Importações para PDF
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

# Views de Autenticação
def login_view(request):
    if request.user.is_authenticated:
        # Redirecionar tesoureiros para a lista de transações
        if not request.user.is_admin():
            return redirect('transaction_list')
        return redirect('index')
    
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # O campo username agora é email
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.get_full_name()}!')
                # Verifica se o usuário precisa trocar a senha
                if not user.password_changed:
                    return render(request, 'registration/redirect_to_change_password.html', {
                        'title': 'Redirecionando...',
                        'user': user
                    })
                # Se há um parâmetro next, redireciona para ele
                next_url = request.GET.get('next')
                if next_url and next_url != '/change-password/':
                    return redirect(next_url)
                # Redirecionar tesoureiros para a lista de transações
                if not user.is_admin():
                    return redirect('transaction_list')
                return redirect('index')
    else:
        form = EmailAuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form, 'title': 'Login'})

def logout_view(request):
    """View para fazer logout do usuário"""
    # Fazer logout do usuário
    logout(request)
    
    # Adicionar mensagem de sucesso
    messages.success(request, 'Você saiu do sistema com sucesso!')
    
    # Redirecionar para a página de login
    return redirect('login')

@login_required
def change_password(request):
    """Força o usuário a trocar a senha no primeiro login"""
    if request.user.password_changed:
        # Redirecionar tesoureiros para a lista de transações
        if not request.user.is_admin():
            return redirect('transaction_list')
        return redirect('index')
    
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Fazer logout do usuário após trocar a senha
            logout(request)
            messages.success(request, 'Senha alterada com sucesso! Faça login novamente com sua nova senha.')
            return render(request, 'registration/redirect_to_login.html', {
                'title': 'Redirecionando...'
            })
        else:
            print(f"DEBUG: Form errors: {form.errors}")
    else:
        form = ChangePasswordForm(request.user)
    
    context = {
        'title': 'Alterar Senha',
        'form': form,
        'force_change': True,
    }
    
    return render(request, 'registration/change_password.html', context)

# Views Principais
@password_changed_required
def index(request):
    """Dashboard principal - apenas para administradores"""
    # Redirecionar tesoureiros para a lista de transações
    if not request.user.is_admin():
        return redirect('transaction_list')
    
    from datetime import datetime, date
    from calendar import monthrange
    
    # Obter filtros da URL
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    selected_category = request.GET.get('category', '')
    selected_type = request.GET.get('type', '')
    selected_field = request.GET.get('field', '')
    selected_church = request.GET.get('church', '')
    
    # Definir datas padrão se não fornecidas
    today = date.today()
    if not date_from:
        # Primeiro dia do mês atual
        first_day = date(today.year, today.month, 1)
        date_from = first_day.strftime('%Y-%m-%d')
    
    if not date_to:
        # Último dia do mês atual
        last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])
        date_to = last_day.strftime('%Y-%m-%d')
    
    context = {
        'title': 'Dashboard',
        'user': request.user,
        'date_from': date_from,
        'date_to': date_to,
        'selected_category': selected_category,
        'selected_type': selected_type,
        'selected_field': selected_field,
        'selected_church': selected_church,
        'categories': Category.objects.all(),
        'current_year': datetime.now().year
    }
    
    # Adicionar campos e igrejas ao contexto baseado no tipo de usuário
    if request.user.is_admin():
        context['fields'] = Field.objects.all()
        context['churches'] = Church.objects.all()
    else:
        # Tesoureiro vê seus campos e suas igrejas
        if request.user.fields.exists():
            context['fields'] = request.user.fields.all()
            user_churches = Church.objects.filter(field__in=request.user.fields.all())
            context['churches'] = user_churches
        else:
            context['fields'] = Field.objects.none()
            context['churches'] = Church.objects.none()
    
    # Base de transações (todos para admin, apenas do usuário para tesoureiro)
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    else:
        base_transactions = Transaction.objects.filter(user=request.user)
    
    # Aplicar filtros
    filtered_transactions = base_transactions
    
    # Filtro por data inicial
    if date_from:
        filtered_transactions = filtered_transactions.filter(date__gte=date_from)
    
    # Filtro por data final
    if date_to:
        filtered_transactions = filtered_transactions.filter(date__lte=date_to)
    
    # Filtro por categoria
    if selected_category:
        filtered_transactions = filtered_transactions.filter(category_id=selected_category)
    
    # Filtro por tipo
    if selected_type:
        filtered_transactions = filtered_transactions.filter(type=selected_type)
    
    # Filtro por campo
    if selected_field:
        filtered_transactions = filtered_transactions.filter(church__field_id=selected_field)
    
    # Filtro por igreja
    if selected_church:
        filtered_transactions = filtered_transactions.filter(church_id=selected_church)
    
    # Calcular totais
    total_transactions = filtered_transactions.count()
    total_income = filtered_transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
    total_expense = filtered_transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
    balance = total_income - total_expense
    
    # Dados para o gráfico por categoria
    categories_data = []
    categories = Category.objects.all()
    
    for category in categories:
        category_transactions = filtered_transactions.filter(category=category)
        income = category_transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
        expense = category_transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
        
        if income > 0 or expense > 0:
            categories_data.append({
                'category': category.name,
                'income': float(income),
                'expense': float(expense)
            })
    
    # Dados por igreja
    churches_data = []
    if request.user.is_admin():
        fields = Field.objects.all()
        for field in fields:
            field_churches = Church.objects.filter(field=field)
            field_income = 0
            field_expense = 0
            
            for church in field_churches:
                church_transactions = filtered_transactions.filter(church=church)
                field_income += church_transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
                field_expense += church_transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
            
            if field_income > 0 or field_expense > 0:
                churches_data.append({
                    'name': field.name,
                    'income': float(field_income),
                    'expense': float(field_expense)
                })
    else:
        # Para tesoureiros, mostrar apenas suas igrejas
        if request.user.fields.exists():
            user_churches = Church.objects.filter(field__in=request.user.fields.all())
            for church in user_churches:
                church_transactions = filtered_transactions.filter(church=church)
                income = church_transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
                expense = church_transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
                
                if income > 0 or expense > 0:
                    churches_data.append({
                        'name': church.name,
                        'income': float(income),
                        'expense': float(expense)
                    })
        else:
            # Se o usuário não tem campos, não mostrar dados de igrejas
            pass
    
    # Dados para o gráfico de Entrada e Saída por Igreja individual
    churches_individual_data = []
    if request.user.is_admin():
        # Para administradores, mostrar todas as igrejas
        all_churches = Church.objects.all()
    else:
        # Para tesoureiros, mostrar apenas suas igrejas
        if request.user.fields.exists():
            all_churches = Church.objects.filter(field__in=request.user.fields.all())
        else:
            all_churches = Church.objects.none()
    
    for church in all_churches:
        church_transactions = filtered_transactions.filter(church=church)
        income = church_transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
        expense = church_transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
        
        if income > 0 or expense > 0:
            churches_individual_data.append({
                'name': church.name,
                'field': church.field.name,
                'income': float(income),
                'expense': float(expense)
            })
    
    # Ordenar por nome da igreja
    churches_individual_data.sort(key=lambda x: x['name'])
    
    # Transações recentes (últimas 10)
    recent_transactions = filtered_transactions.order_by('-date')[:10]
    
    # Adicionar dados ao contexto
    context.update({
        'total_transactions': total_transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'categories_data': categories_data,
        'churches_data': churches_data,
        'churches_individual_data': churches_individual_data, # Adicionado
        'recent_transactions': recent_transactions,
        'selected_category_name': Category.objects.get(id=selected_category).name if selected_category else None,
        'selected_field_name': Field.objects.get(id=selected_field).name if selected_field else None,
        'selected_church_name': Church.objects.get(id=selected_church).name if selected_church else None,
    })
    
    return render(request, 'pages/dashboard.html', context)

# Views de Transações
@password_changed_required
@admin_or_treasurer_required
def transaction_list(request):
    """Lista de transações"""
    from datetime import date
    from calendar import monthrange
    
    if request.user.is_admin():
        transactions = Transaction.objects.all()
    else:
        # Tesoureiros veem apenas transações de suas igrejas
        if request.user.fields.exists():
            user_churches = Church.objects.filter(field__in=request.user.fields.all())
            transactions = Transaction.objects.filter(church__in=user_churches)
        else:
            # Se o usuário não tem campos, mostrar mensagem de erro
            messages.error(request, 'Você não tem campos associados. Entre em contato com o administrador.')
            return redirect('index')
    
    # Filtros
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    transaction_type = request.GET.get('type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    selected_field = request.GET.get('field', '')
    selected_church = request.GET.get('church', '')
    
    # Definir datas padrão se não fornecidas
    today = date.today()
    if not date_from:
        # Primeiro dia do mês atual
        first_day = date(today.year, today.month, 1)
        date_from = first_day.strftime('%Y-%m-%d')
    
    if not date_to:
        # Último dia do mês atual
        last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])
        date_to = last_day.strftime('%Y-%m-%d')
    
    if search:
        transactions = transactions.filter(
            Q(desc__icontains=search) | 
            Q(category__name__icontains=search)
        )
    
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)
    
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
    
    # Filtro por campo (para administradores ou tesoureiros com múltiplos campos)
    if selected_field:
        if request.user.is_admin():
            # Administradores podem filtrar por qualquer campo
            transactions = transactions.filter(church__field_id=selected_field)
        elif request.user.fields.count() > 1:
            # Tesoureiros com múltiplos campos podem filtrar por seus campos
            if request.user.fields.filter(id=selected_field).exists():
                transactions = transactions.filter(church__field_id=selected_field)
    
    # Filtro por igreja
    if selected_church:
        transactions = transactions.filter(church_id=selected_church)
    
    # Calcular totais
    total_transactions = transactions.count()
    total_income = transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
    total_expense = transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
    balance = total_income - total_expense  
    
    # Preparar dados para os filtros
    if request.user.is_admin():
        fields = Field.objects.all()
        churches = Church.objects.all()
        if selected_field:
            churches = churches.filter(field_id=selected_field)
    else:
        # Verificar se o usuário tem campos associados
        if request.user.fields.exists():
            fields = request.user.fields.all()
            churches = Church.objects.filter(field__in=request.user.fields.all())
            
            # Se o usuário tem múltiplos campos, permitir filtro por campo
            if request.user.fields.count() > 1 and selected_field:
                churches = churches.filter(field_id=selected_field)
        else:
            # Se o usuário não tem campos, mostrar mensagem de erro
            messages.error(request, 'Você não tem campos associados. Entre em contato com o administrador.')
            return redirect('index')
    
    # Nomes dos filtros selecionados
    selected_field_name = fields.get(id=selected_field).name if selected_field and fields.filter(id=selected_field).exists() else None
    selected_church_name = churches.get(id=selected_church).name if selected_church and churches.filter(id=selected_church).exists() else None
    
    context = {
        'title': 'Transações',
        'categories': Category.objects.all(),
        'fields': fields,
        'churches': churches,
        'category_id': category_id,
        'selected_category': category_id,
        'transaction_type': transaction_type,
        'selected_type': transaction_type,
        'date_from': date_from,
        'date_to': date_to,
        'selected_field': selected_field,
        'selected_church': selected_church,
        'selected_field_name': selected_field_name,
        'selected_church_name': selected_church_name,
        'total_transactions': total_transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'user': request.user,
    }
    
    return render(request, 'pages/transaction_list.html', context)

# API para paginação AJAX das transações
@password_changed_required
@admin_or_treasurer_required
def transaction_list_api(request):
    """API para listar transações com paginação AJAX"""
    from datetime import date
    from calendar import monthrange
    
    if request.user.is_admin():
        transactions = Transaction.objects.all()
    else:
        # Tesoureiros veem apenas transações de suas igrejas
        if request.user.fields.exists():
            user_churches = Church.objects.filter(field__in=request.user.fields.all())
            transactions = Transaction.objects.filter(church__in=user_churches)
        else:
            return JsonResponse({'error': 'Usuário sem campos associados'}, status=400)
    
    # Filtros
    category_id = request.GET.get('category', '')
    transaction_type = request.GET.get('type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    selected_field = request.GET.get('field', '')
    selected_church = request.GET.get('church', '')
    
    # Definir datas padrão se não fornecidas
    today = date.today()
    if not date_from:
        first_day = date(today.year, today.month, 1)
        date_from = first_day.strftime('%Y-%m-%d')
    
    if not date_to:
        last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])
        date_to = last_day.strftime('%Y-%m-%d')
    
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)
    
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
    
    if selected_field:
        if request.user.is_admin():
            transactions = transactions.filter(church__field_id=selected_field)
        elif request.user.fields.count() > 1:
            if request.user.fields.filter(id=selected_field).exists():
                transactions = transactions.filter(church__field_id=selected_field)
    
    if selected_church:
        transactions = transactions.filter(church_id=selected_church)
    
    # Calcular totais
    total_transactions = transactions.count()
    total_income = transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
    total_expense = transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
    balance = total_income - total_expense
    
    # Paginação
    page = int(request.GET.get('page', 1))
    per_page = 50
    start = (page - 1) * per_page
    end = start + per_page
    
    # Obter transações da página atual
    page_transactions = transactions.order_by('-date')[start:end]
    
    # Preparar dados das transações
    transactions_data = []
    for transaction in page_transactions:
        transactions_data.append({
            'id': transaction.id,
            'date': transaction.date.strftime('%d/%m/%Y'),
            'type': transaction.type,
            'type_display': transaction.get_type_display(),
            'category_name': transaction.category.name,
            'field_name': transaction.church.field.name,
            'church_name': transaction.church.name,
            'desc': transaction.desc or '-',
            'value': float(transaction.value),
            'user_name': transaction.user.get_full_name() if request.user.is_admin() else None,
            'can_edit': request.user.is_admin(),
            'can_view': True,
        })
    
    # Calcular informações de paginação
    total_pages = (total_transactions + per_page - 1) // per_page
    
    return JsonResponse({
        'transactions': transactions_data,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'per_page': per_page,
            'total_items': total_transactions,
            'has_previous': page > 1,
            'has_next': page < total_pages,
            'previous_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None,
        },
        'totals': {
            'total_transactions': total_transactions,
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'balance': float(balance),
        }
    })

@password_changed_required
@admin_or_treasurer_required
def transaction_create(request):
    """Criar nova transação"""
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transação criada com sucesso!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user)
    
    context = {
        'title': 'Nova Transação',
        'form': form,
    }
    
    return render(request, 'pages/transaction_form.html', context)

@password_changed_required
@admin_or_treasurer_required
def transaction_view(request, pk):
    """Visualizar transação - Modo somente leitura"""
    transaction = get_object_or_404(Transaction, pk=pk)
    
    # Verificar se o usuário tem acesso à transação
    if not request.user.is_admin():
        # Tesoureiros só podem ver transações de suas igrejas
        if not request.user.fields.filter(id=transaction.church.field.id).exists():
            messages.error(request, 'Você não tem permissão para visualizar esta transação.')
            return redirect('transaction_list')
    
    form = TransactionForm(instance=transaction, user=request.user)
    
    # Desabilitar todos os campos do formulário
    for field_name in form.fields:
        form.fields[field_name].disabled = True
    
    context = {
        'title': 'Visualizar Transação',
        'form': form,
        'transaction': transaction,
        'readonly': True,
    }
    
    return render(request, 'pages/transaction_form.html', context)

@password_changed_required
@admin_required
def transaction_edit(request, pk):
    """Editar transação - Apenas administradores"""
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transação atualizada com sucesso!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
    context = {
        'title': 'Editar Transação',
        'form': form,
        'transaction': transaction,
    }
    
    return render(request, 'pages/transaction_form.html', context)

@password_changed_required
@admin_required
def transaction_delete(request, pk):
    """Excluir transação - Apenas administradores"""
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transação excluída com sucesso!')
        return redirect('transaction_list')
    
    context = {
        'title': 'Excluir Transação',
        'transaction': transaction,
    }
    
    return render(request, 'pages/transaction_confirm_delete.html', context)

# Views de Categorias (apenas admin)
@password_changed_required
@admin_required
def category_list(request):
    """Lista de categorias"""
    categories = Category.objects.all()
    
    context = {
        'title': 'Categorias',
        'categories': categories,
    }
    
    return render(request, 'pages/category_list.html', context)

@password_changed_required
@admin_required
def category_create(request):
    """Criar nova categoria"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    context = {
        'title': 'Nova Categoria',
        'form': form,
    }
    
    return render(request, 'pages/category_form.html', context)

@password_changed_required
@admin_required
def category_edit(request, pk):
    """Editar categoria"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'title': 'Editar Categoria',
        'form': form,
        'category': category,
    }
    
    return render(request, 'pages/category_form.html', context)

@password_changed_required
@admin_required
def category_delete(request, pk):
    """Excluir categoria"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('category_list')
    
    context = {
        'title': 'Excluir Categoria',
        'category': category,
    }
    
    return render(request, 'pages/category_confirm_delete.html', context)

# Views de Igrejas (apenas admin)
@password_changed_required
@admin_required
def church_list(request):
    """Lista de igrejas"""
    churches = Church.objects.all()
    
    context = {
        'title': 'Igrejas',
        'churches': churches,
    }
    
    return render(request, 'pages/church_list.html', context)

@password_changed_required
@admin_required
def church_create(request):
    """Criar nova igreja"""
    if request.method == 'POST':
        form = ChurchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Igreja criada com sucesso!')
            return redirect('church_list')
    else:
        form = ChurchForm()
    
    context = {
        'title': 'Nova Igreja',
        'form': form,
    }
    
    return render(request, 'pages/church_form.html', context)

@password_changed_required
@admin_required
def church_edit(request, pk):
    """Editar igreja"""
    church = get_object_or_404(Church, pk=pk)
    
    if request.method == 'POST':
        form = ChurchForm(request.POST, instance=church)
        if form.is_valid():
            form.save()
            messages.success(request, 'Igreja atualizada com sucesso!')
            return redirect('church_list')
    else:
        form = ChurchForm(instance=church)
    
    context = {
        'title': 'Editar Igreja',
        'form': form,
        'church': church,
    }
    
    return render(request, 'pages/church_form.html', context)

@password_changed_required
@admin_required
def church_delete(request, pk):
    """Excluir igreja"""
    church = get_object_or_404(Church, pk=pk)
    
    if request.method == 'POST':
        church.delete()
        messages.success(request, 'Igreja excluída com sucesso!')
        return redirect('church_list')
    
    context = {
        'title': 'Excluir Igreja',
        'church': church,
    }
    
    return render(request, 'pages/church_confirm_delete.html', context)

# Views de Usuários (apenas admin)
@password_changed_required
@admin_required
def user_list(request):
    """Lista de usuários"""
    users = User.objects.all()
    
    context = {
        'title': 'Usuários',
        'users': users,
    }
    
    return render(request, 'pages/user_list.html', context)

@password_changed_required
@admin_required
def user_create(request):
    """Criar novo usuário"""
    if request.method == 'POST':
        form = UserForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            # Administradores só podem criar tesoureiros
            user.role = 'treasurer'
            user.save()
            
            # Salvar o formulário para processar campos many-to-many se houver
            form.save()
            
            messages.success(request, f'Usuário {user.get_full_name()} criado com sucesso!')
            return redirect('user_list')
    else:
        form = UserForm(user=request.user)
    
    context = {
        'title': 'Novo Usuário',
        'form': form,
    }
    
    return render(request, 'pages/user_form.html', context)

@password_changed_required
@admin_required
def user_edit(request, pk):
    """Editar usuário"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('user_list')
    else:
        form = UserForm(instance=user, user=request.user)
    
    context = {
        'title': 'Editar Usuário',
        'form': form,
        'user_obj': user,
    }
    
    return render(request, 'pages/user_form.html', context)

@password_changed_required
@admin_required
def user_delete(request, pk):
    """Desativar usuário"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.is_active = False
        user.save()
        messages.success(request, 'Usuário desativado com sucesso!')
        return redirect('user_list')
    
    context = {
        'title': 'Desativar Usuário',
        'user_obj': user,
    }
    
    return render(request, 'pages/user_confirm_delete.html', context)

@admin_required
def user_reset_password(request, pk):
    """Resetar senha do usuário para a senha padrão"""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        try:
            user.password = make_password('nations123456')
            user.password_changed = False  # Força o usuário a trocar a senha novamente
            user.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método não permitido'})



@password_changed_required
@admin_required
def user_activate(request, pk):
    """Reativar usuário"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.is_active = True
        user.save()
        messages.success(request, 'Usuário reativado com sucesso!')
        return redirect('user_list')
    
    context = {
        'title': 'Reativar Usuário',
        'user_obj': user,
    }
    
    return render(request, 'pages/user_confirm_delete.html', context)

# Views de Campos (apenas admin)
@password_changed_required
@admin_required
def field_list(request):
    """Lista de campos"""
    fields = Field.objects.all()
    
    context = {
        'title': 'Campos',
        'fields': fields,
    }
    
    return render(request, 'pages/field_list.html', context)

@password_changed_required
@admin_required
def field_create(request):
    """Criar novo campo"""
    if request.method == 'POST':
        form = FieldForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campo criado com sucesso!')
            return redirect('field_list')
    else:
        form = FieldForm()
    
    context = {
        'title': 'Novo Campo',
        'form': form,
    }
    
    return render(request, 'pages/field_form.html', context)

@password_changed_required
@admin_required
def field_edit(request, pk):
    """Editar campo"""
    field = get_object_or_404(Field, pk=pk)
    
    if request.method == 'POST':
        form = FieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campo atualizado com sucesso!')
            return redirect('field_list')
    else:
        form = FieldForm(instance=field)
    
    context = {
        'title': 'Editar Campo',
        'form': form,
        'field': field,
    }
    
    return render(request, 'pages/field_form.html', context)

@password_changed_required
@admin_required
def field_delete(request, pk):
    """Excluir campo"""
    field = get_object_or_404(Field, pk=pk)
    
    if request.method == 'POST':
        field.delete()
        messages.success(request, 'Campo excluído com sucesso!')
        return redirect('field_list')
    
    context = {
        'title': 'Excluir Campo',
        'field': field,
    }
    
    return render(request, 'pages/field_confirm_delete.html', context)

# API Views para AJAX
@password_changed_required
def get_churches(request):
    """Retorna igrejas de um campo via AJAX"""
    field_id = request.GET.get('field')
    
    churches = Church.objects.all()
    
    if field_id:
        churches = churches.filter(field_id=field_id)
    
    churches_data = churches.values('id', 'name')
    return JsonResponse({'churches': list(churches_data)})

@password_changed_required
@admin_or_treasurer_required
def transaction_export_pdf(request):
    """Exporta transações filtradas para PDF"""
    from datetime import date
    from calendar import monthrange
    
    # Debug: Log dos parâmetros recebidos
    print(f"DEBUG - Parâmetros recebidos na exportação PDF:")
    print(f"DEBUG - category: {request.GET.get('category', '')}")
    print(f"DEBUG - type: {request.GET.get('type', '')}")
    print(f"DEBUG - date_from: {request.GET.get('date_from', '')}")
    print(f"DEBUG - date_to: {request.GET.get('date_to', '')}")
    print(f"DEBUG - field: {request.GET.get('field', '')}")
    print(f"DEBUG - church: {request.GET.get('church', '')}")
    print(f"DEBUG - search: {request.GET.get('search', '')}")
    
    # Obter os mesmos filtros da view transaction_list
    if request.user.is_admin():
        transactions = Transaction.objects.all()
    else:
        # Tesoureiros veem apenas transações de suas igrejas
        if request.user.fields.exists():
            user_churches = Church.objects.filter(field__in=request.user.fields.all())
            transactions = Transaction.objects.filter(church__in=user_churches)
        else:
            # Se o usuário não tem campos, mostrar mensagem de erro
            messages.error(request, 'Você não tem campos associados. Entre em contato com o administrador.')
            return redirect('index')
    
    # Aplicar filtros
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    transaction_type = request.GET.get('type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    selected_field = request.GET.get('field', '')
    selected_church = request.GET.get('church', '')
    
    # Debug: Log dos filtros aplicados
    print(f"DEBUG - Filtros aplicados:")
    print(f"DEBUG - Total inicial de transações: {transactions.count()}")
    
    # Definir datas padrão se não fornecidas
    today = date.today()
    if not date_from:
        first_day = date(today.year, today.month, 1)
        date_from = first_day.strftime('%Y-%m-%d')
    
    if not date_to:
        last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])
        date_to = last_day.strftime('%Y-%m-%d')
    
    # Aplicar filtros
    if search:
        transactions = transactions.filter(
            Q(desc__icontains=search) | 
            Q(category__name__icontains=search)
        )
        print(f"DEBUG - Após filtro de busca: {transactions.count()} transações")
    
    if category_id:
        transactions = transactions.filter(category_id=category_id)
        print(f"DEBUG - Após filtro de categoria: {transactions.count()} transações")
    
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)
        print(f"DEBUG - Após filtro de tipo: {transactions.count()} transações")
    
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
        print(f"DEBUG - Após filtro de data inicial: {transactions.count()} transações")
    
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
        print(f"DEBUG - Após filtro de data final: {transactions.count()} transações")
    
    if selected_field:
        if request.user.is_admin():
            transactions = transactions.filter(church__field_id=selected_field)
        elif request.user.fields.count() > 1:
            if request.user.fields.filter(id=selected_field).exists():
                transactions = transactions.filter(church__field_id=selected_field)
        print(f"DEBUG - Após filtro de campo: {transactions.count()} transações")
    
    if selected_church:
        transactions = transactions.filter(church_id=selected_church)
        print(f"DEBUG - Após filtro de igreja: {transactions.count()} transações")
    
    print(f"DEBUG - Total final de transações: {transactions.count()}")
    
    # Calcular totais
    total_transactions = transactions.count()
    total_income = transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
    total_expense = transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
    balance = total_income - total_expense
    
    # Criar o PDF
    response = HttpResponse(content_type='application/pdf')
    # Formatar nome do arquivo no formato brasileiro (dia-mes-ano)
    filename_date = date.today().strftime("%d-%m-%Y")
    response['Content-Disposition'] = f'attachment; filename="transacoes_{filename_date}.pdf"'
    
    # Configurar o documento
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#673ab7')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=20,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#495057')
    )
    
    # Título com ícone
    # Criar uma tabela para alinhar o título e o ícone lado a lado
    title_data = []
    
    # Verificar se o ícone existe
    # Tentar diferentes caminhos para o ícone
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'static', 'img', 'icon.png'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static', 'img', 'icon.png'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'img', 'icon.png'),
        'app/static/img/icon.png',  # Caminho relativo
    ]
    
    icon_path = None
    icon_exists = False
    
    for path in possible_paths:
        if os.path.exists(path):
            icon_path = path
            icon_exists = True
            break
    
    if icon_exists:
        try:
            # Carregar o ícone PNG com tamanho maior
            icon = Image(icon_path, width=0.8*inch, height=0.8*inch)
            title_data = [[icon, Paragraph("Relatório de Transações", title_style)]]
        except Exception as e:
            # Se não conseguir carregar PNG, usar um símbolo como ícone
            print(f"Erro ao carregar ícone PNG: {e}")
            # Criar um símbolo como ícone usando texto
            icon_style = ParagraphStyle(
                'IconStyle',
                parent=styles['Normal'],
                fontSize=32,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#673ab7')
            )
            icon_symbol = Paragraph("●", icon_style)
            title_data = [[icon_symbol, Paragraph("Relatório de Transações", title_style)]]
    else:
        # Se o ícone não existir, usar um símbolo como ícone
        icon_style = ParagraphStyle(
            'IconStyle',
            parent=styles['Normal'],
            fontSize=32,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#673ab7')
        )
        icon_symbol = Paragraph("●", icon_style)
        title_data = [[icon_symbol, Paragraph("Relatório de Transações", title_style)]]
    
    # Criar tabela do título
    title_table = Table(title_data, colWidths=[1*inch, 5.5*inch] if len(title_data[0]) > 1 else [6.5*inch])
    title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(title_table)
    
    elements.append(Spacer(1, 20))
    
    # Informações do relatório
    # Formatar datas para o formato brasileiro
    try:
        date_from_formatted = datetime.strptime(date_from, '%Y-%m-%d').strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        date_from_formatted = date_from
    
    try:
        date_to_formatted = datetime.strptime(date_to, '%Y-%m-%d').strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        date_to_formatted = date_to
    
    report_info = [
        f"Período: {date_from_formatted} a {date_to_formatted}",
        f"Total de Transações: {total_transactions}",
        f"Total de Entradas: R$ {total_income:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        f"Total de Saídas: R$ {total_expense:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        f"Saldo: R$ {balance:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
    ]
    
    for info in report_info:
        elements.append(Paragraph(info, subtitle_style))
    
    elements.append(Spacer(1, 20))
    
    # Cabeçalho da tabela
    headers = ['Data', 'Tipo', 'Categoria', 'Descrição', 'Igreja', 'Valor (R$)']
    data = [headers]
    
    # Dados das transações
    for transaction in transactions.order_by('-date'):
        # Formatar valor monetário
        formatted_value = f"{transaction.value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        # Abreviar nome da igreja se for muito longo
        church_name = transaction.church.name
        if len(church_name) > 20:
            church_name = church_name[:17] + "..."
        
        row = [
            transaction.date.strftime('%d/%m/%Y'),
            'Entrada' if transaction.type == 'income' else 'Saída',
            transaction.category.name,
            transaction.desc or '-',
            church_name,
            formatted_value
        ]
        data.append(row)
    
    # Criar tabela
    table = Table(data, colWidths=[1*inch, 0.8*inch, 1.2*inch, 2*inch, 1.2*inch, 1*inch])
    
    # Estilo da tabela
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#673ab7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),  # Alinhar valores à direita
    ])
    
    # Alternar cores das linhas
    for i in range(1, len(data)):
        if i % 2 == 0:
            table_style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
    
    table.setStyle(table_style)
    elements.append(table)
    
    # Gerar PDF
    doc.build(elements)
    
    return response

@password_changed_required
@admin_or_treasurer_required
def dashboard_export_pdf(request):
    """Exporta os gráficos do dashboard para PDF usando VerticalBarChart do ReportLab"""
    from datetime import date
    from calendar import monthrange
    
    # Obter os mesmos filtros da view index (dashboard)
    if request.user.is_admin():
        base_transactions = Transaction.objects.all()
    else:
        # Tesoureiros veem apenas transações de suas igrejas
        if request.user.fields.exists():
            user_churches = Church.objects.filter(field__in=request.user.fields.all())
            base_transactions = Transaction.objects.filter(church__in=user_churches)
        else:
            # Se o usuário não tem campos, mostrar mensagem de erro
            messages.error(request, 'Você não tem campos associados. Entre em contato com o administrador.')
            return redirect('index')
    
    # Aplicar filtros
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    selected_category = request.GET.get('category', '')
    selected_type = request.GET.get('type', '')
    selected_field = request.GET.get('field', '')
    selected_church = request.GET.get('church', '')
    
    # Definir datas padrão se não fornecidas
    today = date.today()
    if not date_from:
        first_day = date(today.year, today.month, 1)
        date_from = first_day.strftime('%Y-%m-%d')
    
    if not date_to:
        last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])
        date_to = last_day.strftime('%Y-%m-%d')
    
    # Aplicar filtros
    filtered_transactions = base_transactions
    
    if date_from:
        filtered_transactions = filtered_transactions.filter(date__gte=date_from)
    
    if date_to:
        filtered_transactions = filtered_transactions.filter(date__lte=date_to)
    
    if selected_category:
        filtered_transactions = filtered_transactions.filter(category_id=selected_category)
    
    if selected_type:
        filtered_transactions = filtered_transactions.filter(type=selected_type)
    
    if selected_field:
        filtered_transactions = filtered_transactions.filter(church__field_id=selected_field)
    
    if selected_church:
        filtered_transactions = filtered_transactions.filter(church_id=selected_church)
    
    # Calcular totais
    total_transactions = filtered_transactions.count()
    total_income = filtered_transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
    total_expense = filtered_transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
    balance = total_income - total_expense
    
    # Dados para o gráfico por categoria
    categories_data = []
    categories = Category.objects.all()
    
    for category in categories:
        category_transactions = filtered_transactions.filter(category=category)
        income = category_transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
        expense = category_transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
        
        if income > 0 or expense > 0:
            categories_data.append({
                'category': category.name,
                'income': float(income),
                'expense': float(expense)
            })
    
    # Dados por igreja/campo
    churches_data = []
    if request.user.is_admin():
        fields = Field.objects.all()
        for field in fields:
            field_churches = Church.objects.filter(field=field)
            field_income = 0
            field_expense = 0
            
            for church in field_churches:
                church_transactions = filtered_transactions.filter(church=church)
                field_income += church_transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
                field_expense += church_transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
            
            if field_income > 0 or field_expense > 0:
                churches_data.append({
                    'name': field.name,
                    'income': float(field_income),
                    'expense': float(field_expense)
                })
    else:
        # Para tesoureiros, mostrar apenas suas igrejas
        if request.user.fields.exists():
            user_churches = Church.objects.filter(field__in=request.user.fields.all())
            for church in user_churches:
                church_transactions = filtered_transactions.filter(church=church)
                income = church_transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
                expense = church_transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
                
                if income > 0 or expense > 0:
                    churches_data.append({
                        'name': church.name,
                        'income': float(income),
                        'expense': float(expense)
                    })
    
    # Dados para o gráfico de Entrada e Saída por Igreja individual
    churches_individual_data = []
    if request.user.is_admin():
        # Para administradores, mostrar todas as igrejas
        all_churches = Church.objects.all()
    else:
        # Para tesoureiros, mostrar apenas suas igrejas
        if request.user.fields.exists():
            all_churches = Church.objects.filter(field__in=request.user.fields.all())
        else:
            all_churches = Church.objects.none()
    
    for church in all_churches:
        church_transactions = filtered_transactions.filter(church=church)
        income = church_transactions.filter(type='income').aggregate(total=Sum('value'))['total'] or 0
        expense = church_transactions.filter(type='expense').aggregate(total=Sum('value'))['total'] or 0
        
        if income > 0 or expense > 0:
            churches_individual_data.append({
                'name': church.name,
                'field': church.field.name,
                'income': float(income),
                'expense': float(expense)
            })
    
    # Ordenar por nome da igreja
    churches_individual_data.sort(key=lambda x: x['name'])
    
    # Criar o PDF
    response = HttpResponse(content_type='application/pdf')
    filename_date = date.today().strftime("%d-%m-%Y")
    response['Content-Disposition'] = f'attachment; filename="dashboard_graficos_{filename_date}.pdf"'
    
    # Configurar o documento
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#673ab7')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=20,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#495057')
    )
    
    # Título
    title_data = []
    
    # Verificar se o ícone existe
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'static', 'img', 'icon.png'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static', 'img', 'icon.png'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'img', 'icon.png'),
        'app/static/img/icon.png',
    ]
    
    icon_path = None
    icon_exists = False
    
    for path in possible_paths:
        if os.path.exists(path):
            icon_path = path
            icon_exists = True
            break
    
    if icon_exists:
        try:
            icon = Image(icon_path, width=0.8*inch, height=0.8*inch)
            title_data = [[icon, Paragraph("Relatório de Gráficos do Dashboard", title_style)]]
        except Exception as e:
            print(f"Erro ao carregar ícone PNG: {e}")
            icon_style = ParagraphStyle(
                'IconStyle',
                parent=styles['Normal'],
                fontSize=32,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#673ab7')
            )
            icon_symbol = Paragraph("●", icon_style)
            title_data = [[icon_symbol, Paragraph("Relatório de Gráficos do Dashboard", title_style)]]
    else:
        icon_style = ParagraphStyle(
            'IconStyle',
            parent=styles['Normal'],
            fontSize=32,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#673ab7')
        )
        icon_symbol = Paragraph("●", icon_style)
        title_data = [[icon_symbol, Paragraph("Relatório de Gráficos do Dashboard", title_style)]]
    
    # Criar tabela do título
    title_table = Table(title_data, colWidths=[1*inch, 5.5*inch] if len(title_data[0]) > 1 else [6.5*inch])
    title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#673ab7')),
        ('ROUNDEDCORNERS', [10]),
    ]))
    
    elements.append(title_table)
    elements.append(Spacer(1, 20))
    
    # Informações do período
    period_info = f"Período: {date_from} a {date_to}"
    if selected_category:
        category_name = Category.objects.get(id=selected_category).name
        period_info += f" | Categoria: {category_name}"
    if selected_field:
        field_name = Field.objects.get(id=selected_field).name
        period_info += f" | Campo: {field_name}"
    if selected_church:
        church_name = Church.objects.get(id=selected_church).name
        period_info += f" | Igreja: {church_name}"
    
    period_paragraph = Paragraph(period_info, styles['Normal'])
    elements.append(period_paragraph)
    elements.append(Spacer(1, 20))
    
    # Resumo dos totais
    summary_data = [
        ['Total de Transações', 'Total de Entradas', 'Total de Saídas', 'Saldo'],
        [str(total_transactions), f'R$ {total_income:.2f}', f'R$ {total_expense:.2f}', f'R$ {balance:.2f}']
    ]
    
    summary_table = Table(summary_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#673ab7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Gráfico por Categoria usando VerticalBarChart
    if categories_data:
        elements.append(Paragraph("Gráfico por Categoria", subtitle_style))
        
        # Preparar dados para o gráfico
        category_names = [item['category'] for item in categories_data]
        income_values = [item['income'] for item in categories_data]
        expense_values = [item['expense'] for item in categories_data]
        
        # Criar dados para o gráfico
        data = []
        for i, name in enumerate(category_names):
            data.append([name, income_values[i], expense_values[i]])
        
        # Criar o gráfico de barras
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from reportlab.graphics.charts.legends import Legend
        from reportlab.graphics.shapes import Drawing, String
        from reportlab.graphics.charts.textlabels import Label
        
        # Gráfico de barras para categorias
        drawing = Drawing(400, 200)
        
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 300
        bc.data = [income_values, expense_values]
        bc.categoryAxis.categoryNames = category_names
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(max(income_values), max(expense_values)) * 1.2
        bc.valueAxis.valueStep = 1000  # Incrementos de 1000 em 1000
        bc.categoryAxis.labels.angle = 45  # Legendas do eixo X na diagonal
        
        # Configurar cores
        bc.bars[0].fillColor = colors.HexColor('#28a745')  # Verde para entradas
        bc.bars[1].fillColor = colors.HexColor('#ff6b6b')  # Vermelho para saídas
        
        # Adicionar legendas
        legend = Legend()
        legend.x = 350
        legend.y = 100
        legend.alignment = 'right'
        legend.fontName = 'Helvetica'
        legend.fontSize = 10
        legend.colorNamePairs = [
            (colors.HexColor('#28a745'), 'Entradas'),
            (colors.HexColor('#ff6b6b'), 'Saídas')
        ]
        
        drawing.add(bc)
        drawing.add(legend)
        
        elements.append(drawing)
        elements.append(Spacer(1, 20))
        
        # Tabela com dados das categorias
        category_table_data = [['Categoria', 'Entradas', 'Saídas']]
        for item in categories_data:
            category_table_data.append([
                item['category'],
                f'R$ {item["income"]:.2f}',
                f'R$ {item["expense"]:.2f}'
            ])
        
        category_table = Table(category_table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(category_table)
        elements.append(Spacer(1, 30))
    
    # Gráfico por Igreja/Campo usando VerticalBarChart
    if churches_data:
        elements.append(Paragraph("Gráfico por Igreja/Campo", subtitle_style))
        
        # Preparar dados para o gráfico
        church_names = [item['name'] for item in churches_data]
        church_income_values = [item['income'] for item in churches_data]
        church_expense_values = [item['expense'] for item in churches_data]
        
        # Criar o gráfico de barras
        drawing2 = Drawing(400, 200)
        
        bc2 = VerticalBarChart()
        bc2.x = 50
        bc2.y = 50
        bc2.height = 125
        bc2.width = 300
        bc2.data = [church_income_values, church_expense_values]
        bc2.categoryAxis.categoryNames = church_names
        bc2.valueAxis.valueMin = 0
        bc2.valueAxis.valueMax = max(max(church_income_values), max(church_expense_values)) * 1.2
        bc2.valueAxis.valueStep = 1000  # Incrementos de 1000 em 1000
        bc2.categoryAxis.labels.angle = 45  # Legendas do eixo X na diagonal
        
        # Configurar cores
        bc2.bars[0].fillColor = colors.HexColor('#28a745')  # Verde para entradas
        bc2.bars[1].fillColor = colors.HexColor('#ff6b6b')  # Vermelho para saídas
        
        # Adicionar legendas
        legend2 = Legend()
        legend2.x = 350
        legend2.y = 100
        legend2.alignment = 'right'
        legend2.fontName = 'Helvetica'
        legend2.fontSize = 10
        legend2.colorNamePairs = [
            (colors.HexColor('#28a745'), 'Entradas'),
            (colors.HexColor('#ff6b6b'), 'Saídas')
        ]
        
        drawing2.add(bc2)
        drawing2.add(legend2)
        
        elements.append(drawing2)
        elements.append(Spacer(1, 20))
        
        # Tabela com dados das igrejas/campos
        church_table_data = [['Nome', 'Entradas', 'Saídas']]
        for item in churches_data:
            church_table_data.append([
                item['name'],
                f'R$ {item["income"]:.2f}',
                f'R$ {item["expense"]:.2f}'
            ])
        
        church_table = Table(church_table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        church_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff6b6b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(church_table)
        elements.append(Spacer(1, 30))
    
    # Gráfico de Entrada e Saída por Igreja Individual usando VerticalBarChart
    if churches_individual_data:
        elements.append(Paragraph("Gráfico de Entrada e Saída por Igreja", subtitle_style))
        
        # Preparar dados para o gráfico
        individual_names = [item['name'] for item in churches_individual_data]
        individual_income_values = [item['income'] for item in churches_individual_data]
        individual_expense_values = [item['expense'] for item in churches_individual_data]
        
        # Criar o gráfico de barras
        drawing3 = Drawing(400, 200)
        
        bc3 = VerticalBarChart()
        bc3.x = 50
        bc3.y = 50
        bc3.height = 125
        bc3.width = 300
        bc3.data = [individual_income_values, individual_expense_values]
        bc3.categoryAxis.categoryNames = individual_names
        bc3.valueAxis.valueMin = 0
        bc3.valueAxis.valueMax = max(max(individual_income_values), max(individual_expense_values)) * 1.2
        bc3.valueAxis.valueStep = 1000  # Incrementos de 1000 em 1000
        bc3.categoryAxis.labels.angle = 45  # Legendas do eixo X na diagonal
        
        # Configurar cores
        bc3.bars[0].fillColor = colors.HexColor('#28a745')  # Verde para entradas
        bc3.bars[1].fillColor = colors.HexColor('#ff6b6b')  # Vermelho para saídas
        
        # Adicionar legendas
        legend3 = Legend()
        legend3.x = 350
        legend3.y = 100
        legend3.alignment = 'right'
        legend3.fontName = 'Helvetica'
        legend3.fontSize = 10
        legend3.colorNamePairs = [
            (colors.HexColor('#28a745'), 'Entradas'),
            (colors.HexColor('#ff6b6b'), 'Saídas')
        ]
        
        drawing3.add(bc3)
        drawing3.add(legend3)
        
        elements.append(drawing3)
        elements.append(Spacer(1, 20))
        
        # Tabela com dados das igrejas individuais
        individual_table_data = [['Igreja', 'Campo', 'Entradas', 'Saídas']]
        for item in churches_individual_data:
            individual_table_data.append([
                item['name'],
                item['field'],
                f'R$ {item["income"]:.2f}',
                f'R$ {item["expense"]:.2f}'
            ])
        
        individual_table = Table(individual_table_data, colWidths=[2*inch, 2*inch, 1*inch, 1*inch])
        individual_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#673ab7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(individual_table)
        elements.append(Spacer(1, 20))
    
    # Rodapé
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    footer_text = f"Relatório gerado em {date.today().strftime('%d/%m/%Y')} às {datetime.now().strftime('%H:%M')}"
    footer_paragraph = Paragraph(footer_text, footer_style)
    elements.append(footer_paragraph)
    
    # Construir o PDF
    doc.build(elements)
    
    return response


@password_changed_required
def churches_by_field_api(request, field_id):
    """API para retornar igrejas de um campo específico"""
    try:
        field = get_object_or_404(Field, pk=field_id)
        
        # Verificar permissões do usuário
        if not request.user.is_admin():
            # Tesoureiros só podem ver igrejas dos seus campos
            if not request.user.fields.filter(id=field_id).exists():
                return JsonResponse({'error': 'Acesso negado'}, status=403)
        
        # Buscar igrejas do campo
        churches = Church.objects.filter(field=field).order_by('name')
        
        churches_data = []
        for church in churches:
            churches_data.append({
                'id': church.id,
                'name': church.name,
                'address': church.address or '',
                'shepherd': church.shepherd
            })
        
        return JsonResponse({
            'field': field.name,
            'churches': churches_data
        })
        
    except Field.DoesNotExist:
        return JsonResponse({'error': 'Campo não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

