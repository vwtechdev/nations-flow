from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal

class Field(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nome")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Campo"
        verbose_name_plural = "Campos"
        ordering = ['-updated_at', 'name']
    
    def __str__(self):
        return self.name

class Church(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nome")
    address = models.CharField(max_length=300, blank=True, null=True, verbose_name="Endereço")
    shepherd = models.CharField(max_length=200, verbose_name="Pastor Responsável")
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
    name = models.CharField(max_length=100, verbose_name="Nome")
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



    

