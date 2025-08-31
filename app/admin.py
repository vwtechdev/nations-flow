from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django import forms
from .models import Church, User, Field, Shepherd, Category, Transaction, AccessLog, Notification

# Formulário personalizado para Transaction com validação de tamanho
class TransactionAdminForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'
    
    def clean_proof(self):
        proof = self.cleaned_data.get('proof')
        if proof:
            # Limitar tamanho do arquivo para 1MB
            max_size = 1 * 1024 * 1024  # 1MB em bytes
            if proof.size > max_size:
                raise ValidationError(
                    f"O arquivo é muito grande. Tamanho máximo permitido: 1MB. "
                    f"Seu arquivo tem {proof.size / (1024*1024):.1f}MB."
                )
        return proof

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    def has_module_permission(self, request):
        """Verifica se o usuário tem permissão para acessar o módulo admin"""
        # Apenas superusuários têm acesso
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)

@admin.register(Shepherd)
class ShepherdAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    def has_module_permission(self, request):
        """Verifica se o usuário tem permissão para acessar o módulo admin"""
        # Apenas superusuários têm acesso
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)

@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = ['name', 'shepherd', 'field', 'created_at']
    search_fields = ['name', 'shepherd__name', 'address']
    list_filter = ['field', 'shepherd', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_module_permission(self, request):
        """Verifica se o usuário tem permissão para acessar o módulo admin"""
        # Apenas superusuários têm acesso
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'get_fields_display', 'is_active']
    list_filter = ['role', 'fields', 'is_active']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name')}),
        ('Permissões', {'fields': ('role', 'fields', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'fields'),
        }),
    )
    
    def get_fields_display(self, obj):
        """Exibe os campos do usuário na lista"""
        return ", ".join([field.name for field in obj.fields.all()])
    get_fields_display.short_description = 'Campos'
    
    def has_module_permission(self, request):
        """Verifica se o usuário tem permissão para acessar o módulo admin"""
        # Apenas superusuários têm acesso
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Verifica se o usuário tem permissão para visualizar objetos"""
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        """Verifica se o usuário tem permissão para adicionar objetos"""
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        """Verifica se o usuário tem permissão para alterar objetos"""
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        """Verifica se o usuário tem permissão para deletar objetos"""
        return self.has_module_permission(request)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'mandatory_proof', 'created_at']
    search_fields = ['name']
    list_filter = ['mandatory_proof', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_module_permission(self, request):
        """Verifica se o usuário tem permissão para acessar o módulo admin"""
        # Apenas superusuários têm acesso
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    form = TransactionAdminForm
    list_display = ['type', 'category', 'value', 'date', 'user', 'church', 'shepherd', 'proof', 'created_at']
    list_filter = ['type', 'category', 'date', 'user', 'church__field', 'church__shepherd', 'created_at']
    search_fields = ['desc', 'category__name', 'user__email', 'church__name', 'church__shepherd__name']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    
    def shepherd(self, obj):
        return obj.church.shepherd.name if obj.church and obj.church.shepherd else '-'
    shepherd.short_description = 'Pastor'
    
    def has_module_permission(self, request):
        """Verifica se o usuário tem permissão para acessar o módulo admin"""
        # Apenas superusuários têm acesso
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Apenas superusuários podem ver transações no admin
        return qs.none()

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp', 'user__role']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'ip_address']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'action', 'timestamp', 'ip_address']
    
    def has_module_permission(self, request):
        """Verifica se o usuário tem permissão para acessar o módulo admin"""
        # Apenas superusuários têm acesso
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        """Apenas superusuários podem adicionar logs manualmente"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Apenas superusuários podem editar logs"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Apenas superusuários podem deletar logs"""
        return request.user.is_superuser
    
    def get_queryset(self, request):
        """Apenas superusuários podem ver os logs"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Apenas superusuários podem ver logs
        return qs.none()


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'date', 'is_read', 
        'created_by', 'created_at'
    ]
    list_filter = [
        'is_read', 'created_at'
    ]
    search_fields = [
        'title', 'body', 'created_by__email'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'body', 'date')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Informações do Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """Verifica se o usuário tem permissão para acessar o módulo admin"""
        # Apenas superusuários têm acesso
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def save_model(self, request, obj, form, change):
        """Define automaticamente o usuário que criou a notificação"""
        if not change:  # Nova notificação
            obj.created_by = request.user
        super().save_model(request, obj, form, change)