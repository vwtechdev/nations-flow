# Nations Flow

Sistema de gestão financeira para igrejas (controle de entradas/saídas, categorização, relatórios PDF/XLSX, notificações recorrentes, controle de acesso hierárquico por campos geográficos). Django 5.2 monolítico (pt-BR, `America/Sao_Paulo`). Python 3.12 web / 3.11 cron.

## 🚀 Deploy

### Opção 1: Docker (Recomendado para Produção)
Veja as instruções abaixo para deploy com Docker.

### Opção 2: Desenvolvimento Local (SQLite)
Para desenvolvimento local sem Docker:

```bash
# Clone o projeto
git clone <url-do-repositorio>
cd nations-flow

# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Execute migrações
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py migrate

# Coletar arquivos estáticos
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py collectstatic --noinput

# Inicie o servidor de desenvolvimento
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py runserver
```

## 📋 Instalação e Configuração (Docker)

### Pré-requisitos
- Docker
- Docker Compose

### Primeira Execução

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd nations-flow
```

2. **Configure as variáveis de ambiente**
```bash
# Crie o arquivo .env com as variáveis necessárias (não existe .env.example)
# Variáveis obrigatórias: SECRET_KEY, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
# POSTGRES_HOST, POSTGRES_PORT, REDIS_HOST, REDIS_PORT, REDIS_DB, ALLOWED_HOSTS,
# DEBUG, DEFAULT_USER_PASSWORD, SYSTEM_HIDDEN_EMAIL, BACKUP_RETENTION_DAYS,
# RECAPTCHA_PUBLIC_KEY, RECAPTCHA_PRIVATE_KEY, RECAPTCHA_DOMAIN, RECAPTCHA_REQUIRED_SCORE
# Opcionais: DOMAIN, WHATSAPP_GROUP_URL
```

3. **Inicie os containers**
```bash
docker-compose up -d
```

> **Nota**: O banco de dados é inicializado automaticamente pelo container `web` (aplica migrações via `wait-for-database.sh` + `gunicorn`). O comando `backup_postgres` roda diariamente às 02:00 no container `cron`.

### Execuções Subsequentes

```bash
docker-compose up -d
```

### Acessos Padrão

- **URL**: http://localhost:8081 (nginx na porta 8081 do host)
- **Login**: Use as credenciais definidas nas variáveis de ambiente ou crie um superusuário:
  ```bash
  docker compose exec web python manage.py createsuperuser
  ```

### Comandos Úteis

```bash
# Parar os containers
docker-compose down

# Ver logs
docker-compose logs -f

# Reiniciar containers
docker-compose restart

# Acessar container web
docker-compose exec web bash

# Executar comandos Django
docker-compose exec web python manage.py shell

# Aplicar migrações
docker-compose exec web python manage.py migrate

# Processar notificações recorrentes
docker-compose exec web python manage.py process_repeat_notifications

# Testar cache Redis
docker-compose exec web python manage.py test_cache
```

### Estrutura do Projeto

```
nations-flow/
├── app/                    # Aplicação principal
│   ├── models.py          # Modelos do banco
│   ├── views.py           # Views do sistema
│   ├── forms.py           # Formulários
│   ├── urls.py            # URLs da app
│   ├── decorators.py      # Decorators de permissão
│   ├── backends.py        # Backend de autenticação por email
│   ├── middleware.py      # Middleware customizado
│   ├── search.py          # Busca case/acento-insensível
│   ├── templatetags/      # Template tags customizadas
│   ├── management/commands/  # Comandos customizados
│   └── migrations/        # Migrações do banco
├── core/                  # Configurações Django (projeto)
│   ├── settings.py        # Configurações produção (PostgreSQL + Redis)
│   ├── settings_dev.py    # Configurações dev (SQLite + LocMemCache)
│   ├── urls.py            # URLs raiz
│   ├── wsgi.py            # WSGI entry point
│   └── asgi.py            # ASGI entry point
├── static/                # Arquivos estáticos (fonte)
├── templates/             # Templates HTML
├── staticfiles/           # Arquivos estáticos coletados (gerado em runtime)
├── media/                 # Uploads (gerado em runtime)
├── nginx/                 # Configuração Nginx + Dockerfile
├── cron/                  # Container cron (Dockerfile, scripts)
├── docker-compose.yml     # Orquestração Docker (5 serviços)
├── Dockerfile             # Imagem web (Python 3.12)
├── wait-for-database.sh   # Aguarda DB antes de subir
├── deploy-nginx.sh        # Script rebuild nginx + collectstatic
├── deploy.yml             # GitHub Actions deploy (em .github/workflows/)
├── requirements.txt       # Dependências Python
└── README.md              # Este arquivo
```

### Funcionalidades

- **Dashboard**: Visão geral das finanças (apenas admin)
- **Transações**: CRUD de entradas/saídas com comprovante (upload ≤1MB), validação por categoria
- **Categorias**: CRUD com flag `mandatory_proof` (anexo obrigatório)
- **Campos**: CRUD de divisão geográfica
- **Igrejas**: CRUD vinculado a Campo + Pastor
- **Pastores**: CRUD independente
- **Usuários**: CRUD com roles (admin, treasurer, supervisor) + campos (M2M)
- **Notificações**: Criação com repetição (daily/weekly/monthly/annually), reprocessamento automático
- **Relatórios**: Exportação PDF (ReportLab) e XLSX (openpyxl)
- **Logs de Acesso**: Auditoria de login/logout/ações (exceto superusers)
- **Health Check**: Endpoint `/health/`

### Permissões (Roles)

| Role | Acesso |
|------|--------|
| **Administrador** | Tudo, exceto gerenciar outros admins |
| **Administrador Principal** (`is_owner`) | Tudo + gerenciar outros admins (protegido contra outros admins) |
| **Tesoureiro** | Apenas próprias transações |
| **Supervisor** | Próprias + de tesoureiros e supervisores no mesmo campo |

### Banco de Dados

- **Produção (Docker)**: PostgreSQL 15
- **Desenvolvimento Local**: SQLite (via `core.settings_dev`)
- **Migrações**: Aplicadas automaticamente no deploy (`docker compose run --rm web python manage.py migrate --noinput`)

### Variáveis de Ambiente Obrigatórias

Veja `core/settings.py` para a lista completa. Principais:
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`
- `DEFAULT_USER_PASSWORD`, `SYSTEM_HIDDEN_EMAIL`, `BACKUP_RETENTION_DAYS`
- `RECAPTCHA_PUBLIC_KEY`, `RECAPTCHA_PRIVATE_KEY`, `RECAPTCHA_DOMAIN`, `RECAPTCHA_REQUIRED_SCORE`
- `DOMAIN` (para `CSRF_TRUSTED_ORIGINS`), `WHATSAPP_GROUP_URL` (opcional)
