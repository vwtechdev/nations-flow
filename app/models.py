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
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para não salvar logs do superuser 'vwtechdev@gmail.com'
        """
        # Verificar se o usuário é o superuser que não deve ter logs salvos
        if self.user and self.user.email == 'vwtechdev@gmail.com':
            # Não salvar o log para este usuário específico
            return
        
        # Para todos os outros usuários, salvar normalmente
        super().save(*args, **kwargs)


class Notification(models.Model):
    REPEAT_CHOICES = [
        ('none', 'Não repetir'),
        ('daily', 'Diariamente'),
        ('weekly', 'Semanalmente'),
        ('monthly', 'Mensalmente'),
        ('annually', 'Anualmente'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Título")
    body = models.TextField(verbose_name="Mensagem")
    date = models.DateTimeField(verbose_name="Data e Hora")
    is_read = models.BooleanField(default=False, verbose_name="Lida")
    
    # Campos para repetição
    repeat = models.BooleanField(default=False, verbose_name="Repetir Notificação")
    repeat_frequency = models.CharField(
        max_length=20, 
        choices=REPEAT_CHOICES, 
        default='none',
        verbose_name="Frequência de Repetição"
    )
    original_notification = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Notificação Original",
        related_name='repeated_notifications'
    )
    next_repeat_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Próxima Data de Repetição"
    )

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
        repeat_info = f" ({self.get_repeat_frequency_display()})" if self.repeat else ""
        return f"{self.title} - {self.date.strftime('%d/%m/%Y %H:%M')} ({status}){repeat_info}"
    
    def calculate_next_repeat_date(self):
        """Calcula a próxima data de repetição baseada na frequência"""
        if not self.repeat or self.repeat_frequency == 'none':
            return None
            
        from datetime import timedelta
        import calendar
        
        if self.repeat_frequency == 'daily':
            return self.date + timedelta(days=1)
        elif self.repeat_frequency == 'weekly':
            return self.date + timedelta(weeks=1)
        elif self.repeat_frequency == 'monthly':
            # Para mensal, adicionar 1 mês mantendo o mesmo dia e hora
            current_month = self.date.month
            current_year = self.date.year
            
            # Calcular próximo mês e ano
            if current_month == 12:
                next_month = 1
                next_year = current_year + 1
            else:
                next_month = current_month + 1
                next_year = current_year
            
            # Verificar se o dia existe no próximo mês
            last_day_of_next_month = calendar.monthrange(next_year, next_month)[1]
            day = min(self.date.day, last_day_of_next_month)
            
            try:
                return self.date.replace(year=next_year, month=next_month, day=day)
            except ValueError:
                # Se ainda houver erro, usar o último dia do mês
                return self.date.replace(year=next_year, month=next_month, day=last_day_of_next_month)
        elif self.repeat_frequency == 'annually':
            # Para anual, adicionar 1 ano mantendo o mesmo dia e hora
            next_year = self.date.year + 1
            try:
                return self.date.replace(year=next_year)
            except ValueError:
                # Se o dia não existe no próximo ano (ex: 29/02), usar o último dia do mês
                last_day = calendar.monthrange(next_year, self.date.month)[1]
                day = min(self.date.day, last_day)
                return self.date.replace(year=next_year, day=day)
        
        return None
    
    def is_original(self):
        """Verifica se esta é a notificação original (não uma repetição)"""
        return self.original_notification is None
    
