from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from decimal import Decimal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from core.models import BaseModel
import os


def transaction_proof_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    user = slugify(instance.user.get_full_name() or instance.user.username)[:60]
    return f"proofs/{instance.date:%Y/%m/%d}/{user}_transacao_{instance.date:%d_%m_%Y}_{datetime.now():%H_%M_%S}{ext}"


def church_contract_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    name = slugify(instance.name)[:50]
    return f"churches/{datetime.now():%Y/%m/%d}/{name}_igreja_{datetime.now():%d_%m_%Y_%H_%M_%S}{ext}"


def shepherd_contract_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    name = slugify(instance.name)[:50]
    return f"shepherds/{datetime.now():%Y/%m/%d}/{name}_pastor_{datetime.now():%d_%m_%Y_%H_%M_%S}{ext}"


class Field(BaseModel):
    name = models.CharField(max_length=200, verbose_name="Nome do Campo")

    class Meta(BaseModel.Meta):
        verbose_name = "Campo"
        verbose_name_plural = "Campos"
        ordering = ['-updated_at', 'name']

    def __str__(self):
        return self.name


class Shepherd(BaseModel):
    name = models.CharField(max_length=200, verbose_name="Nome do Pastor")
    contract = models.FileField(
        upload_to=shepherd_contract_path,
        blank=True,
        null=True,
        verbose_name="Contrato do Pastor"
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Pastor"
        verbose_name_plural = "Pastores"
        ordering = ['-updated_at', 'name']

    def __str__(self):
        return self.name


class Church(BaseModel):
    name = models.CharField(max_length=200, verbose_name="Nome da Igreja")
    address = models.CharField(max_length=300, blank=True, null=True, verbose_name="Endereço")
    shepherd = models.ForeignKey(Shepherd, on_delete=models.CASCADE, verbose_name="Pastor Responsável")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, verbose_name="Campo")
    contract = models.FileField(
        upload_to=church_contract_path,
        blank=True,
        null=True,
        verbose_name="Contrato da Igreja"
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Igreja"
        verbose_name_plural = "Igrejas"
        ordering = ['-updated_at', 'name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('treasurer', 'Tesoureiro'),
        ('supervisor', 'Supervisor'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='treasurer', verbose_name="Função")
    fields = models.ManyToManyField(Field, blank=True, verbose_name="Campos")
    password_changed = models.BooleanField(default=False, verbose_name="Senha Alterada")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

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

    def is_supervisor(self):
        return self.role == 'supervisor'

    def get_fields(self):
        return self.fields.all()

    def has_field(self, field):
        return self.fields.filter(id=field.id).exists()


class Category(BaseModel):
    name = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    mandatory_proof = models.BooleanField(default=True, verbose_name="Anexo de Comprovante Obrigatório")

    class Meta(BaseModel.Meta):
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['-updated_at', 'name']

    def __str__(self):
        return self.name


class Transaction(BaseModel):
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
        upload_to=transaction_proof_path,
        blank=True,
        null=True,
        verbose_name="Comprovante"
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        ordering = ['-updated_at', '-date', '-created_at']

    def __str__(self):
        return f"{self.get_type_display()} - {self.category.name} - R$ {self.value}"

    def get_formatted_value(self):
        return f"R$ {self.value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()
        if self.category and self.category.mandatory_proof and not self.proof:
            raise ValidationError({
                'proof': 'Esta categoria requer anexo de comprovante obrigatório.'
            })


class AccessLog(BaseModel):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Criação'),
        ('update', 'Edição'),
        ('delete', 'Exclusão'),
    ]

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora", db_column='timestamp')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Ação")
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    description = models.TextField(blank=True, verbose_name="Descrição")

    class Meta(BaseModel.Meta):
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_action_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M:%S')}"

    def save(self, *args, **kwargs):
        if self.user and (self.user.is_superuser or self.user.email == settings.SYSTEM_HIDDEN_EMAIL):
            return
        super().save(*args, **kwargs)


def log_action(user, action, obj=None, description='', request=None):
    if user and (user.is_superuser or user.email == settings.SYSTEM_HIDDEN_EMAIL):
        return
    kwargs = {
        'user': user,
        'action': action,
        'description': description,
    }
    if obj:
        kwargs['content_object'] = obj
        if not description:
            kwargs['description'] = f'{action} em {obj._meta.verbose_name}'
    AccessLog.objects.create(**kwargs)


class Notification(BaseModel):
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
    repeat_frequency = models.CharField(
        max_length=10,
        choices=REPEAT_CHOICES,
        default='none',
        verbose_name="Frequência de Repetição"
    )
    repeat = models.BooleanField(default=True, verbose_name="Repetir Notificação")

    class Meta(BaseModel.Meta):
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-created_at', '-date']

    def __str__(self):
        status = "Lida" if self.is_read else "Não lida"
        repeat_info = f" ({self.get_repeat_frequency_display()})" if self.repeat else ""
        return f"{self.title} - {self.date.strftime('%d/%m/%Y %H:%M')} ({status}){repeat_info}"

    def schedule_next(self):
        if self.repeat_frequency == 'daily':
            self.date += timedelta(days=1)
        elif self.repeat_frequency == 'weekly':
            self.date += timedelta(weeks=1)
        elif self.repeat_frequency == 'monthly':
            self.date += relativedelta(months=1)
        elif self.repeat_frequency == 'annually':
            self.date += relativedelta(years=1)
        else:
            self.repeat = False

        self.is_read = False
        self.save()


class ShepherdHistory(BaseModel):
    church = models.ForeignKey(Church, on_delete=models.CASCADE, verbose_name="Igreja")
    shepherd = models.ForeignKey(Shepherd, on_delete=models.CASCADE, verbose_name="Pastor")
    start_date = models.DateField(verbose_name="Data Início")
    end_date = models.DateField(null=True, blank=True, verbose_name="Data Fim")

    class Meta(BaseModel.Meta):
        verbose_name = "Histórico de Pastor"
        verbose_name_plural = "Histórico de Pastores"
        ordering = ['-start_date']

    def __str__(self):
        end = self.end_date.strftime('%d/%m/%Y') if self.end_date else 'Atual'
        return f"{self.shepherd.name} → {self.church.name} ({self.start_date.strftime('%d/%m/%Y')} - {end})"


@receiver(pre_delete, sender=Transaction)
def delete_transaction_proof(sender, instance, **kwargs):
    if instance.proof:
        instance.proof.delete(save=False)
