from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Church, User, Field, Category, Transaction

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = ['name', 'shepherd', 'field', 'created_at']
    search_fields = ['name', 'shepherd', 'address']
    list_filter = ['field', 'created_at']
    date_hierarchy = 'created_at'

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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['type', 'category', 'value', 'date', 'user', 'church', 'created_at']
    list_filter = ['type', 'category', 'date', 'user', 'church', 'created_at']
    search_fields = ['desc', 'category__name', 'user__email', 'church__name']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Administradores veem todas as transações
        if request.user.is_admin():
            return qs
        # Tesoureiros veem apenas suas transações
        return qs.filter(user=request.user)