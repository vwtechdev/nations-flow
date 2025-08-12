from django import forms
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
import re
from .models import State, City, Church, User, Field, Category, Transaction

class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = ['name', 'uf']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'uf': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
        }

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', 'state']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
        }

class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ChurchForm(forms.ModelForm):
    class Meta:
        model = Church
        fields = ['name', 'city', 'address', 'phone', 'field']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'field': forms.Select(attrs={'class': 'form-control'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'field']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'field': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Tornar campos obrigatórios
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['role'].required = True
        
        # Adicionar asterisco para campos obrigatórios
        self.fields['first_name'].label = 'Nome *'
        self.fields['last_name'].label = 'Sobrenome *'
        self.fields['email'].label = 'Email *'
        self.fields['role'].label = 'Função *'
        
        # Se o usuário logado for administrador, ocultar o campo field
        if self.user and self.user.is_admin():
            del self.fields['field']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar se o email já existe (exceto para o usuário atual em edição)
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance.pk else None)
            if existing_user.exists():
                raise ValidationError('Este email já está em uso por outro usuário.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Se for um novo usuário, gerar username automaticamente
        if not self.instance.pk:
            first_name = cleaned_data.get('first_name', '')
            last_name = cleaned_data.get('last_name', '')
            
            if first_name and last_name:
                # Gera o username baseado no primeiro nome + último nome (lowercase, sem espaços)
                username = f"{first_name.lower()}{last_name.lower()}".replace(' ', '')
                cleaned_data['username'] = username
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Define a senha padrão apenas para novos usuários
        if not user.pk:
            user.password = make_password('nations123456')
            user.password_changed = False  # Força troca de senha no primeiro login
        
        if commit:
            user.save()
        return user

class ChangePasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
        min_length=8,
        help_text="A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e símbolos."
    )
    new_password2 = forms.CharField(
        label="Confirme a nova senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password:
            # Verificar se a senha não é muito simples
            if password.lower() in ['123', '123456', 'password', 'senha', 'admin', 'user', 'teste', 'test']:
                raise ValidationError("Esta senha é muito simples. Escolha uma senha mais segura.")
            
            # Verificar se a senha não é a senha padrão
            if password == 'nations123456':
                raise ValidationError("Não é possível usar a senha padrão. Escolha uma nova senha.")
            
            # Verificar se a senha não contém apenas números
            if password.isdigit():
                raise ValidationError("A senha não pode conter apenas números.")
            
            # Verificar se a senha não contém apenas letras
            if password.isalpha():
                raise ValidationError("A senha deve conter pelo menos um número.")
            
            # Verificar se a senha tem pelo menos 8 caracteres
            if len(password) < 8:
                raise ValidationError("A senha deve ter pelo menos 8 caracteres.")
            
            # Verificar se a senha contém pelo menos uma letra maiúscula
            if not re.search(r'[A-Z]', password):
                raise ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
            
            # Verificar se a senha contém pelo menos uma letra minúscula
            if not re.search(r'[a-z]', password):
                raise ValidationError("A senha deve conter pelo menos uma letra minúscula.")
            
            # Verificar se a senha contém pelo menos um número
            if not re.search(r'\d', password):
                raise ValidationError("A senha deve conter pelo menos um número.")
            
            # Verificar se a senha contém pelo menos um símbolo
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError("A senha deve conter pelo menos um símbolo (!@#$%^&*(),.?\":{}|<>).")
        
        return password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("As senhas não coincidem.")
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        self.user.password_changed = True
        if commit:
            self.user.save(update_fields=['password', 'password_changed'])
        return self.user

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'desc', 'category', 'value', 'date', 'church']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'church': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.is_treasurer():
                # Tesoureiros só podem ver igrejas do seu campo
                if user.field:
                    self.fields['church'].queryset = Church.objects.filter(field=user.field)
                else:
                    self.fields['church'].queryset = Church.objects.none()
            else:
                # Administradores podem ver todas as igrejas
                self.fields['church'].queryset = Church.objects.all()
        
        # Garantir que o campo date use o formato correto
        if 'date' in self.fields:
            self.fields['date'].input_formats = ['%Y-%m-%d']
            
            # Se há uma instância (edição), formatar a data corretamente
            if self.instance and self.instance.pk and self.instance.date:
                # Formatar a data para o formato YYYY-MM-DD esperado pelo input type="date"
                formatted_date = self.instance.date.strftime('%Y-%m-%d')
                self.initial['date'] = formatted_date
    
    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value and value <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return value

class EmailAuthenticationForm(AuthenticationForm):
    """Formulário de autenticação usando email em vez de username"""
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu email'
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Usar email como campo de autenticação
        self.fields['username'].label = 'Email'
        self.fields['username'].widget.attrs['placeholder'] = 'Digite seu email'
    
    def clean_username(self):
        email = self.cleaned_data.get('username')
        if email:
            # Verificar se o email existe no sistema
            if not User.objects.filter(email=email).exists():
                raise ValidationError('Email não encontrado no sistema.')
        return email

