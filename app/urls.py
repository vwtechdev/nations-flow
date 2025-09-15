from django.urls import path
from . import views

urlpatterns = [
    # Views principais
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Transações
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/api/', views.transaction_list_api, name='transaction_list_api'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/view/', views.transaction_view, name='transaction_view'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    
    # API para buscar igrejas por campo
    path('api/churches-by-field/<int:field_id>/', views.churches_by_field_api, name='churches_by_field_api'),
    # API para buscar informações da categoria
    path('api/category/<int:category_id>/', views.category_info_api, name='category_info_api'),
    path('transactions/export-pdf/', views.transaction_export_pdf, name='transaction_export_pdf'),
    path('dashboard/export-pdf/', views.dashboard_export_pdf, name='dashboard_export_pdf'),
    
    # Categorias
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Igrejas
    path('churches/', views.church_list, name='church_list'),
    path('churches/create/', views.church_create, name='church_create'),
    path('churches/<int:pk>/edit/', views.church_edit, name='church_edit'),
    path('churches/<int:pk>/delete/', views.church_delete, name='church_delete'),
    
    # Usuários
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/activate/', views.user_activate, name='user_activate'),
    path('users/<int:pk>/reset-password/', views.user_reset_password, name='user_reset_password'),
    
    # Logs de Acesso
    path('access-logs/', views.access_log_list, name='access_log_list'),
    
    # Notificações
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/create/', views.notification_create, name='notification_create'),
    path('notifications/<int:pk>/edit/', views.notification_edit, name='notification_edit'),
    path('notifications/<int:pk>/delete/', views.notification_delete, name='notification_delete'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('api/notifications/today/', views.get_today_notifications, name='get_today_notifications'),
    
    # Campos
    path('fields/', views.field_list, name='field_list'),
    path('fields/create/', views.field_create, name='field_create'),
    path('fields/<int:pk>/edit/', views.field_edit, name='field_edit'),
    path('fields/<int:pk>/delete/', views.field_delete, name='field_delete'),
    
    # Pastores
    path('shepherds/', views.shepherd_list, name='shepherd_list'),
    path('shepherds/create/', views.shepherd_create, name='shepherd_create'),
    path('shepherds/<int:pk>/edit/', views.shepherd_edit, name='shepherd_edit'),
    path('shepherds/<int:pk>/delete/', views.shepherd_delete, name='shepherd_delete'),
    
    # API AJAX
    path('api/churches/', views.get_churches, name='get_churches'),
    
    # Health Check
    path('health/', views.health_check, name='health_check'),
    

]
