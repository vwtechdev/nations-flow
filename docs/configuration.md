# Configuração

Esta página detalha todas as configurações disponíveis no Nations Flow.

## 🔧 Variáveis de Ambiente

O Nations Flow usa variáveis de ambiente para configuração. Crie um arquivo `.env` na raiz do projeto:

### Configurações Básicas do Django

```env
# Django Settings
SECRET_KEY=django-insecure-sua-chave-secreta-aqui
DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1] 0.0.0.0
```

### Configurações do Banco de Dados

#### PostgreSQL (Recomendado)

```env
# Database Configuration for PostgreSQL
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=nationsflow
DATABASE_USER=nations
DATABASE_PASSWORD=91Jgy0q8a5BnV
DATABASE_HOST=db
DATABASE_PORT=5432
```

#### SQLite (Desenvolvimento)

```env
# Database Configuration for SQLite
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
```

### Configurações de Produção

```env
# Production Settings
DEBUG=0
SECRET_KEY=sua-chave-secreta-forte-aqui
DJANGO_ALLOWED_HOSTS=seudominio.com www.seudominio.com

# Database (Production)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=nationsflow_prod
DATABASE_USER=nations_flow_prod
DATABASE_PASSWORD=senha_forte_aqui
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

## 🗄️ Configuração do Banco de Dados

### PostgreSQL

#### Instalação

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql postgresql-server

# Arch Linux
sudo pacman -S postgresql
```

#### Configuração Inicial

```bash
# Inicializar o banco
sudo -u postgres initdb -D /var/lib/postgres/data

# Iniciar o serviço
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar usuário e banco
sudo -u postgres psql
CREATE DATABASE nationsflow;
CREATE USER nations_flow_user WITH PASSWORD 'sua_senha_aqui';
GRANT ALL PRIVILEGES ON DATABASE nationsflow TO nations_flow_user;
\q
```

#### Configuração de Segurança

Edite `/etc/postgresql/15/main/pg_hba.conf`:

```conf
# Método de autenticação
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

### SQLite

Para desenvolvimento, você pode usar SQLite:

```env
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
```

## 🔐 Configurações de Segurança

### SECRET_KEY

Gere uma chave secreta forte:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### ALLOWED_HOSTS

Configure os hosts permitidos:

```env
# Desenvolvimento
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

# Produção
DJANGO_ALLOWED_HOSTS=seudominio.com www.seudominio.com api.seudominio.com
```

### DEBUG

```env
# Desenvolvimento
DEBUG=1

# Produção
DEBUG=0
```

## 📁 Configuração de Arquivos Estáticos

### Configuração Básica

```python
# settings.py
STATIC_URL = 'static/'
STATIC_ROOT = 'static'
MEDIA_URL = 'media/'
MEDIA_ROOT = 'media'
```

### Configuração com Nginx

```nginx
location /static/ {
    alias /path/to/nations-flow/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /path/to/nations-flow/media/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## 📊 Configuração de Logs

### Configuração Básica

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/nationsflow/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'app': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Configuração de Logs em Produção

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/nationsflow/django.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
```

## 🔧 Configurações Avançadas

### Configuração de Cache

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Configuração de Sessões

```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 semanas
SESSION_COOKIE_SECURE = True  # Para HTTPS
SESSION_COOKIE_HTTPONLY = True
```

### Configuração de Email

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-de-app'
```

## 🐳 Configuração Docker

### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: postgres-container
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=nations
      - POSTGRES_PASSWORD=91Jgy0q8a5BnV
      - POSTGRES_DB=nationsflow
    restart: unless-stopped

  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: django-container
    command: >
      sh -c "python manage.py wait_for_database &&
             python manage.py migrate && 
             python manage.py makemigrations &&
             python manage.py create_initial_data &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/usr/src/nations-flow/
    ports:
      - 8000:8000
    env_file:
      - ./.env
    depends_on:
      - db
    restart: unless-stopped

volumes:
  postgres_data:
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /usr/src/nations-flow

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
```

## 🔍 Configuração de Monitoramento

### Health Check

```python
# views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "healthy"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=500)
```

### Configuração de Métricas

```python
# settings.py
INSTALLED_APPS += [
    'django_prometheus',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... outros middlewares
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

## 📋 Checklist de Configuração

- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados configurado
- [ ] Migrações aplicadas
- [ ] Usuário admin criado
- [ ] Logs configurados
- [ ] Arquivos estáticos configurados
- [ ] Segurança configurada
- [ ] Email configurado (se necessário)
- [ ] Cache configurado (se necessário)
- [ ] Monitoramento configurado (se necessário)

## 🔧 Comandos Úteis

```bash
# Verificar configurações
python manage.py check

# Coletar arquivos estáticos
python manage.py collectstatic

# Verificar migrações
python manage.py showmigrations

# Criar superusuário
python manage.py createsuperuser

# Shell do Django
python manage.py shell

# Testes
python manage.py test
``` 