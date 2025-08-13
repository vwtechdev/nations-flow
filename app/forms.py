from django import forms
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.utils.html import format_html
import re
from .models import Church, User, Field, Category, Transaction

class CheckboxTableWidget(forms.Widget):
    """Widget personalizado para exibir campos como uma tabela com checkboxes"""
    
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs)
        self.choices = choices
    
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        
        # Converter para lista se não for
        if not isinstance(value, (list, tuple)):
            value = [value]
        
        # Obter todos os campos disponíveis
        fields = Field.objects.all().order_by('name')
        
        # Converter para lista de IDs para comparação
        selected_ids = [str(v.id) if hasattr(v, 'id') else str(v) for v in value]
        
        output = ['<div class="checkbox-table-container">']
        output.append('<table class="table table-bordered table-hover">')
        output.append('<thead class="table-light">')
        output.append('<tr>')
        output.append('<th style="width: 50px; text-align: center;">Selecionar</th>')
        output.append('<th>Nome do Campo</th>')
        output.append('</tr>')
        output.append('</thead>')
        output.append('<tbody>')
        
        for field in fields:
            field_id = str(field.id)
            is_checked = field_id in selected_ids
            
            output.append('<tr>')
            output.append('<td style="text-align: center;">')
            output.append(f'<input type="checkbox" name="{name}" value="{field_id}"')
            if is_checked:
                output.append(' checked')
            output.append(' class="form-check-input">')
            output.append('</td>')
            output.append(f'<td>{field.name}</td>')
            output.append('</tr>')
        
        output.append('</tbody>')
        output.append('</table>')
        output.append('</div>')
        
        return format_html(''.join(output))
    
    def value_from_datadict(self, data, files, name):
        """Extrai os valores selecionados dos dados do formulário"""
        if hasattr(data, 'getlist'):
            values = data.getlist(name)
            # Converter para lista de IDs de campos
            if values:
                try:
                    return [int(v) for v in values if v.isdigit()]
                except (ValueError, TypeError):
                    return []
            return []
        elif isinstance(data, (list, tuple)):
            return data
        elif isinstance(data, dict):
            values = data.get(name, [])
            if isinstance(values, list):
                try:
                    return [int(v) for v in values if str(v).isdigit()]
                except (ValueError, TypeError):
                    return []
            return []
        return []
    
    def value_omitted_from_data(self, data, files, name):
        """Verifica se o campo foi omitido dos dados"""
        return name not in data

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
        fields = ['name', 'address', 'shepherd', 'field']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'shepherd': forms.TextInput(attrs={'class': 'form-control'}),
            'field': forms.Select(attrs={'class': 'form-control'}),
        }

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
        
        # Se for um novo usuário (sem instância), remover o campo fields
        if not self.instance or not self.instance.pk:
            del self.fields['fields']
    
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
                base_username = f"{first_name.lower()}{last_name.lower()}".replace(' ', '')
                
                # Verificar se o username já existe e gerar um único
                username = base_username
                counter = 1
                
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                cleaned_data['username'] = username
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Capturar os campos selecionados antes de salvar (apenas se existir)
        selected_fields = self.cleaned_data.get('fields', []) if 'fields' in self.cleaned_data else []
        
        # Define a senha padrão apenas para novos usuários
        if not user.pk:
            user.password = make_password('nations123456')
            user.password_changed = False  # Força troca de senha no primeiro login
            
            # Garantir que o username seja definido para novos usuários
            if not user.username and 'username' in self.cleaned_data:
                user.username = self.cleaned_data['username']
        
        if commit:
            # Salvar o usuário primeiro para obter o ID
            user.save()
            
            # Aplicar campos apenas se existirem (edição)
            if selected_fields:
                user.fields.set(selected_fields)
            elif 'fields' in self.cleaned_data:
                # Se o campo fields foi enviado mas está vazio, limpar
                user.fields.clear()
        else:
            # Se não estiver commitando, armazenar os campos para uso posterior
            if selected_fields:
                user._selected_fields = selected_fields
        
        return user
    
    def save_m2m(self):
        """Salva os campos many-to-many após o usuário ser salvo"""
        super().save_m2m()
        
        # Aplicar campos selecionados se existirem
        if hasattr(self.instance, '_selected_fields'):
            selected_fields = self.instance._selected_fields
            if selected_fields:
                self.instance.fields.set(selected_fields)
            else:
                self.instance.fields.clear()
            # Limpar o atributo temporário
            delattr(self.instance, '_selected_fields')

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
    # Campo para seleção do campo (não é salvo no modelo Transaction)
    field = forms.ModelChoiceField(
        queryset=Field.objects.all(),
        empty_label="Selecione um campo",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Campo"
    )
    
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
        
        # Configurar o campo de seleção de campo baseado no usuário
        if user:
            if user.is_treasurer():
                # Tesoureiros só podem ver seus campos
                if user.fields.exists():
                    self.fields['field'].queryset = user.fields.all()
                    # Configurar o campo inicial se for edição
                    if self.instance and self.instance.pk and self.instance.church:
                        self.fields['field'].initial = self.instance.church.field
                else:
                    self.fields['field'].queryset = Field.objects.none()
            else:
                # Administradores podem ver todos os campos
                self.fields['field'].queryset = Field.objects.all()
                # Configurar o campo inicial se for edição
                if self.instance and self.instance.pk and self.instance.church:
                    self.fields['field'].initial = self.instance.church.field
        
        # Configurar o campo church baseado no campo selecionado
        # Primeiro verificar se há dados no formulário (POST)
        if hasattr(self, 'data') and self.data:
            field_id = self.data.get('field')
            if field_id:
                try:
                    selected_field = Field.objects.get(id=field_id)
                    self.fields['church'].queryset = Church.objects.filter(field=selected_field)
                except Field.DoesNotExist:
                    self.fields['church'].queryset = Church.objects.none()
            else:
                self.fields['church'].queryset = Church.objects.none()
        # Se não há dados, verificar initial (para edição)
        elif 'field' in self.initial and self.initial['field']:
            selected_field = self.initial['field']
            self.fields['church'].queryset = Church.objects.filter(field=selected_field)
        else:
            # Inicialmente, church está desabilitado até que um campo seja selecionado
            self.fields['church'].queryset = Church.objects.none()
        
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
    
    def clean(self):
        cleaned_data = super().clean()
        field = cleaned_data.get('field')
        church = cleaned_data.get('church')
        
        # Validar que um campo foi selecionado
        if not field:
            raise forms.ValidationError("É necessário selecionar um campo antes de selecionar a igreja.")
        
        # Validar que a igreja foi selecionada
        if not church:
            raise forms.ValidationError("É necessário selecionar uma igreja.")
        
        # Validar que a igreja pertence ao campo selecionado
        if church and field and church.field != field:
            raise forms.ValidationError("A igreja selecionada não pertence ao campo selecionado.")
        
        return cleaned_data

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

