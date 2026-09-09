# Nations Flow

Sistema de gestão financeira para igrejas (controle de entradas/saídas, categorização, relatórios PDF/XLSX, notificações recorrentes, controle de acesso hierárquico por campos geográficos). Django 5.2 monolítico (pt-BR, `America/Sao_Paulo`). Python 3.12 web / 3.11 cron.

## Deploy

### Instalação e Configuração (Docker)

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
# Copie o exemplo e preencha os valores
cp .env.example .env
# O arquivo .env é gitignored (nunca commitar)
```
Veja `.env.example` para a lista completa de variáveis obrigatórias e opcionais.

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

- **Dashboard**: Visão geral das finanças (apenas admin), saldos separados em Caixa e PIX
- **Transações**: CRUD de entradas/saídas com comprovante (upload ≤1MB), validação por categoria, filtro e badge de Status (Conferido/Pendente), conferência em lote (apenas admin)
- **Categorias**: CRUD com flags `mandatory_proof` (anexo obrigatório) e `is_pix` (compõe o saldo PIX)
- **Campos**: CRUD de divisão geográfica
- **Igrejas**: CRUD vinculado a Campo + Pastor, com contrato (upload)
- **Pastores**: CRUD independente, com contrato (upload) e histórico por igreja
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
- **Migrações**: Aplicadas automaticamente no deploy (`docker compose run --rm web python manage.py migrate --noinput`)

### Variáveis de Ambiente Obrigatórias

Veja `core/settings.py` para a lista completa. Principais:
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`
- `DEFAULT_USER_PASSWORD`, `SYSTEM_HIDDEN_EMAIL`, `BACKUP_RETENTION_DAYS`
- `RECAPTCHA_PUBLIC_KEY`, `RECAPTCHA_PRIVATE_KEY`, `RECAPTCHA_DOMAIN`, `RECAPTCHA_REQUIRED_SCORE`
- `DOMAIN` (para `CSRF_TRUSTED_ORIGINS`), `WHATSAPP_GROUP_URL` (opcional)

---

## Desenvolvido por

**VWTech Dev | Soluções em Tecnologia**
