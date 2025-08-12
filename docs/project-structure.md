# Estrutura do Projeto

Esta página detalha a estrutura de arquivos e diretórios do projeto Nations Flow.

## 📁 Visão Geral da Estrutura

```
nations-flow/
├── app/                    # Aplicação principal Django
│   ├── __init__.py
│   ├── admin.py           # Configuração do admin
│   ├── apps.py            # Configuração da app
│   ├── decorators.py      # Decoradores personalizados
│   ├── forms.py           # Formulários Django
│   ├── management/        # Comandos personalizados
│   │   └── commands/
│   │       ├── create_initial_data.py
│   │       └── wait_for_database.py
│   ├── migrations/        # Migrações do banco
│   ├── models.py          # Modelos de dados
│   ├── static/           # Arquivos estáticos
│   │   ├── css/
│   │   ├── img/
│   │   └── js/
│   ├── templates/        # Templates HTML
│   │   ├── pages/
│   │   └── registration/
│   ├── templatetags/     # Tags personalizadas
│   ├── tests.py          # Testes
│   ├── urls.py           # URLs da aplicação
│   └── views.py          # Views/Controllers
├── core/                 # Configurações do projeto
│   ├── __init__.py
│   ├── asgi.py          # Configuração ASGI
│   ├── settings.py      # Configurações Django
│   ├── urls.py          # URLs principais
│   └── wsgi.py          # Configuração WSGI
├── docs/                # Documentação MkDocs
├── docker-compose.yml   # Configuração Docker
├── Dockerfile           # Imagem Docker
├── manage.py            # Script de gerenciamento Django
├── requirements.txt     # Dependências Python
└── README.md           # Documentação principal
```

## 🏗️ Aplicação Principal (app/)

### Modelos (models.py)

```python
# Principais modelos
class User(AbstractUser):
    # Usuário personalizado com roles

class State(models.Model):
    # Estados brasileiros

class City(models.Model):
    # Cidades

class Field(models.Model):
    # Campos/Regiões

class Church(models.Model):
    # Igrejas

class Category(models.Model):
    # Categorias de transações

class Transaction(models.Model):
    # Transações financeiras
```

### Views (views.py)

```python
# Views principais
class DashboardView(LoginRequiredMixin, View):
    # Dashboard principal

class UserListView(LoginRequiredMixin, ListView):
    # Lista de usuários

class TransactionListView(LoginRequiredMixin, ListView):
    # Lista de transações

class ChurchListView(LoginRequiredMixin, ListView):
    # Lista de igrejas
```

### URLs (urls.py)

```python
# Padrões de URL
urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
    path('churches/', ChurchListView.as_view(), name='church_list'),
    # ... outras URLs
]
```

### Templates (templates/)

```
templates/
├── pages/               # Páginas principais
│   ├── dashboard.html   # Dashboard
│   ├── user_list.html   # Lista de usuários
│   ├── user_form.html   # Formulário de usuário
│   ├── transaction_list.html
│   ├── transaction_form.html
│   ├── church_list.html
│   ├── church_form.html

└── registration/        # Autenticação
    └── login.html       # Página de login
```

### Arquivos Estáticos (static/)

```
static/
├── css/
│   └── base.css        # Estilos principais
├── img/
│   ├── icon.svg        # Ícone do sistema
│   └── finance.svg     # Ícone financeiro
└── js/
    ├── index.js        # JavaScript do dashboard
    ├── login.js        # JavaScript do login
    └── search.js       # Funcionalidade de busca
```

## ⚙️ Configurações (core/)

### settings.py

```python
# Configurações principais
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',  # Nossa aplicação
]

# Configurações de banco
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DATABASE_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DATABASE_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("DATABASE_USER", "user"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD", "password"),
        "HOST": os.environ.get("DATABASE_HOST", "localhost"),
        "PORT": os.environ.get("DATABASE_PORT", "5432"),
    }
}

# Modelo de usuário personalizado
AUTH_USER_MODEL = 'app.User'
```

### urls.py

```python
# URLs principais
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
```

## 🛠️ Comandos Personalizados (management/)

### create_initial_data.py

```python
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Cria dados iniciais:
        # - Estados e cidades
        # - Campos
        # - Igrejas
        # - Categorias
        # - Usuários (admin, tesoureiro)
        # - Transações de exemplo
```

### wait_for_database.py

```python
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Aguarda o banco estar disponível
        # Útil para Docker
```

## 📊 Migrações (migrations/)

```
migrations/
├── __init__.py
├── 0001_initial.py      # Migração inicial
├── 0002_remove_church_from_user.py
├── 0003_apply_new_rules.py
└── 0004_add_timestamps_to_field.py
```

## 🎨 Templates e Frontend

### Base Template

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Nations Flow{% endblock %}</title>
    <link href="{% static 'css/base.css' %}" rel="stylesheet">
</head>
<body>
    <div class="sidebar" id="sidebar">
        <!-- Sidebar com navegação -->
    </div>
    
    <div class="main-content" id="main-content">
        {% block content %}
        {% endblock %}
    </div>
    
    <script src="{% static 'js/index.js' %}"></script>
</body>
</html>
```

### Dashboard Template

```html
<!-- templates/pages/dashboard.html -->
{% extends 'base.html' %}

{% block content %}
<div class="dashboard">
    <div class="stats-cards">
        <!-- Cards com estatísticas -->
    </div>
    
    <div class="charts">
        <!-- Gráficos Chart.js -->
    </div>
    
    <div class="recent-transactions">
        <!-- Transações recentes -->
    </div>
</div>
{% endblock %}
```

## 🔧 Configuração Docker

### docker-compose.yml

```yaml
services:
  db:
    image: postgres:15
    # Configuração do PostgreSQL
    
  web:
    build: .
    # Configuração do Django
    command: >
      sh -c "python manage.py wait_for_database &&
             python manage.py migrate && 
             python manage.py create_initial_data &&
             python manage.py runserver 0.0.0.0:8000"
```

### Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /usr/src/nations-flow
# Instalação de dependências
# Cópia do código
# Configuração do ambiente
```

## 📁 Arquivos de Configuração

### requirements.txt

```
Django==5.2.4
psycopg2-binary==2.9.10
python-dotenv==1.1.1
# ... outras dependências
```

### .env

```env
# Django Settings
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

# Database Configuration
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=nationsflow
DATABASE_USER=nations
DATABASE_PASSWORD=91Jgy0q8a5BnV
DATABASE_HOST=db
DATABASE_PORT=5432
```

## 🧪 Testes

### tests.py

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from app.models import Church, Transaction, Category

class UserModelTest(TestCase):
    def test_create_user(self):
        # Testes de criação de usuário

class TransactionModelTest(TestCase):
    def test_create_transaction(self):
        # Testes de criação de transação
```

## 📚 Documentação

### docs/

```
docs/
├── index.md              # Página inicial
├── overview.md           # Visão geral
├── installation.md       # Instalação
├── configuration.md      # Configuração
├── docker.md            # Docker
├── project-structure.md  # Esta página
├── api-models.md        # API e modelos
├── dashboard.md         # Dashboard
├── users.md             # Gestão de usuários
├── churches.md          # Gestão de igrejas
├── transactions.md      # Gestão de transações

├── sidebar-minimization.md
├── backup-restore.md    # Backup e restauração
├── troubleshooting.md   # Troubleshooting
├── contributing.md      # Guia de contribuição
└── img/                # Imagens da documentação
    └── icon.svg
```

## 🔍 Padrões de Nomenclatura

### Python

- **Classes**: PascalCase (ex: `UserListView`)
- **Funções/Variáveis**: snake_case (ex: `create_user`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `DEBUG`)
- **Módulos**: snake_case (ex: `user_views.py`)

### HTML/CSS

- **Classes CSS**: kebab-case (ex: `sidebar-nav`)
- **IDs**: camelCase (ex: `sidebarToggle`)
- **Arquivos**: snake_case (ex: `user_list.html`)

### JavaScript

- **Variáveis/Funções**: camelCase (ex: `toggleSidebar`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `API_URL`)

## 📋 Convenções do Projeto

### Estrutura de Views

```python
# Sempre herdar de LoginRequiredMixin para views protegidas
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'pages/user_list.html'
    context_object_name = 'users'
    
    def get_queryset(self):
        # Filtros personalizados
        return super().get_queryset()
```

### Estrutura de Models

```python
class Transaction(models.Model):
    # Campos sempre com verbose_name
    value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Valor"
    )
    
    # Sempre incluir __str__
    def __str__(self):
        return f"{self.desc} - R$ {self.value}"
    
    # Meta sempre presente
    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
```

### Estrutura de Templates

```html
<!-- Sempre usar extends -->
{% extends 'base.html' %}

<!-- Sempre usar block content -->
{% block content %}
<!-- Conteúdo aqui -->
{% endblock %}

<!-- Sempre usar static para assets -->
{% load static %}
<link href="{% static 'css/style.css' %}" rel="stylesheet">
```

## 🚀 Deploy

### Estrutura de Produção

```
/var/www/nations-flow/
├── app/                 # Código da aplicação
├── static/             # Arquivos estáticos coletados
├── media/              # Uploads de usuários
├── logs/               # Logs da aplicação
├── .env                # Variáveis de ambiente
└── manage.py           # Script Django
```

### Configuração de Servidor

```nginx
# /etc/nginx/sites-available/nations-flow
server {
    listen 80;
    server_name nations-flow.com;
    
    location /static/ {
        alias /var/www/nations-flow/static/;
    }
    
    location /media/ {
        alias /var/www/nations-flow/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoramento

### Logs

```
/var/log/nations-flow/
├── django.log          # Logs da aplicação
├── nginx_access.log    # Logs de acesso
├── nginx_error.log     # Logs de erro
└── postgresql.log      # Logs do banco
```

### Métricas

- **Uptime**: Monitoramento de disponibilidade
- **Performance**: Tempo de resposta das páginas
- **Erros**: Logs de erro e exceções
- **Banco**: Performance das consultas
- **Usuários**: Atividade dos usuários

## 🔧 Manutenção

### Backup

```bash
# Backup do banco
pg_dump -U nations nationsflow > backup.sql

# Backup dos arquivos
tar -czf nations-flow-backup.tar.gz /var/www/nations-flow/
```

### Atualizações

```bash
# Atualizar código
git pull origin main

# Aplicar migrações
python manage.py migrate

# Coletar estáticos
python manage.py collectstatic

# Reiniciar serviços
sudo systemctl restart gunicorn
sudo systemctl restart nginx
``` 