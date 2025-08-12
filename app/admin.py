from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import State, City, Church, User, Field, Category, Transaction

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'uf']
    search_fields = ['name', 'uf']
    list_filter = ['uf']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'state']
    search_fields = ['name', 'state__name']
    list_filter = ['state']

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'field', 'phone', 'created_at']
    search_fields = ['name', 'city__name', 'address']
    list_filter = ['city__state', 'field', 'created_at']
    date_hierarchy = 'created_at'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'field', 'is_active']
    list_filter = ['role', 'field', 'is_active']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name')}),
        ('Permissões', {'fields': ('role', 'field', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'field'),
        }),
    )

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
    readonly_fields = ['created_at', 'last_update']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Administradores veem todas as transações
        if request.user.is_admin():
            return qs
        # Tesoureiros veem apenas suas transações
        return qs.filter(user=request.user)