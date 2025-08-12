from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_admin():
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta página.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def treasurer_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_treasurer():
            messages.error(request, 'Acesso negado. Apenas tesoureiros podem acessar esta página.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_or_treasurer_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_admin() or request.user.is_treasurer()):
            messages.error(request, 'Acesso negado. Você não tem permissão para acessar esta página.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def password_changed_required(view_func):
    """Decorator para verificar se o usuário já trocou a senha"""
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.password_changed:
            messages.warning(request, 'Você deve alterar sua senha antes de continuar.')
            return redirect('change_password')
        return view_func(request, *args, **kwargs)
    return _wrapped_view 