from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin


class AdminAccessMiddleware(MiddlewareMixin):
    """
    Middleware para restringir acesso ao painel de administração
    para usuários administradores e tesoureiros
    """
    
    def process_request(self, request):
        # Verificar se a requisição é para o admin
        if request.path.startswith('/admin/'):
            # Se o usuário não está autenticado, deixar o Django lidar com o login
            if not request.user.is_authenticated:
                return None
            
            # Se o usuário é superusuário, permitir acesso total
            if request.user.is_superuser:
                return None
            
            # TODOS os outros usuários (incluindo administradores e tesoureiros) são negados
            messages.error(
                request, 
                'Apenas superusuários têm acesso ao painel de administração.'
            )
            # Redirecionar para a página inicial ou dashboard
            return redirect('index')
        
        return None
