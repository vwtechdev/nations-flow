from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal

class Field(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nome do Campo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Campo"
        verbose_name_plural = "Campos"
        ordering = ['-updated_at', 'name']
    
    def __str__(self):
        return self.name

class Shepherd(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nome do Pastor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Pastor"
        verbose_name_plural = "Pastores"
        ordering = ['-updated_at', 'name']
    
    def __str__(self):
        return self.name

class Church(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nome da Igreja")
    address = models.CharField(max_length=300, blank=True, null=True, verbose_name="Endereço")
    shepherd = models.ForeignKey(Shepherd, on_delete=models.CASCADE, verbose_name="Pastor Responsável")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, verbose_name="Campo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Igreja"
        verbose_name_plural = "Igrejas"
        ordering = ['-updated_at', 'name']
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('treasurer', 'Tesoureiro'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='treasurer', verbose_name="Função")
    fields = models.ManyToManyField(Field, blank=True, verbose_name="Campos")
    password_changed = models.BooleanField(default=False, verbose_name="Senha Alterada")
    
    # Usar email como campo de autenticação principal
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    # Sobrescrever o campo email para torná-lo único
    email = models.EmailField(unique=True, verbose_name="Email")
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['-date_joined', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_treasurer(self):
        return self.role == 'treasurer'
    
    def get_fields(self):
        """Retorna os campos do usuário"""
        return self.fields.all()
    
    def has_field(self, field):
        """Verifica se o usuário tem acesso a um campo específico"""
        return self.fields.filter(id=field.id).exists()
    
    # Removida a função has_default_password

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    mandatory_proof = models.BooleanField(default=True, verbose_name="Anexo de Comprovante Obrigatório")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['-updated_at', 'name']
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Entrada'),
        ('expense', 'Saída'),
    ]
    
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Tipo")
    desc = models.TextField(blank=True, null=True, verbose_name="Descrição")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Categoria")
    value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valor (R$)"
    )
    date = models.DateField(verbose_name="Data")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    church = models.ForeignKey(Church, on_delete=models.CASCADE, verbose_name="Igreja")
    proof = models.FileField(
        upload_to='proofs/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Comprovante"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        ordering = ['-updated_at', '-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.category.name} - R$ {self.value}"
    
    def get_formatted_value(self):
        return f"R$ {self.value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def clean(self):
        """Validação personalizada para verificar se o comprovante é obrigatório"""
        from django.core.exceptions import ValidationError
        
        super().clean()
        
        # Verificar se a categoria requer comprovante obrigatório
        if self.category and self.category.mandatory_proof and not self.proof:
            raise ValidationError({
                'proof': 'Esta categoria requer anexo de comprovante obrigatório.'
            })

class AccessLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="Ação")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Endereço IP")
    
    class Meta:
        verbose_name = "Log de Acesso"
        verbose_name_plural = "Logs de Acesso"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_action_display()} - {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}"


class Notification(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    body = models.TextField(verbose_name="Mensagem")
    date = models.DateTimeField(verbose_name="Data e Hora")
    is_read = models.BooleanField(default=False, verbose_name="Lida")

    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Criado por",
        related_name='notifications_created'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-created_at', '-date']
    
    def __str__(self):
        status = "Lida" if self.is_read else "Não lida"
        return f"{self.title} - {self.date.strftime('%d/%m/%Y %H:%M')} ({status})"
    
