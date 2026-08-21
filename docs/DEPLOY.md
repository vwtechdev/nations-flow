# Deploy e Configuração

## Visão Geral

O Nations Flow suporta deploy com Docker (produção) e desenvolvimento local sem Docker.

## Deploy com Docker (Produção)

### Pré-requisitos
- Docker
- Docker Compose

### Configuração Inicial

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd nations-flow
```

2. **Configure variáveis de ambiente**
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

> **Nota**: O banco de dados é inicializado automaticamente (o container `web` roda `wait-for-database.sh` e aplica migrações via `gunicorn` startup). O container `cron` executa `backup_postgres` diariamente às 02:00 e `process_repeat_notifications` a cada hora.

### Serviços Docker

- **nginx**: Servidor web e proxy reverso (porta 8081 no host, health check `/health`)
- **web**: Aplicação Django com Gunicorn (porta 8000 interna, 2 workers sync, timeout 120)
- **db**: PostgreSQL 15
- **redis**: Redis 7 para cache e sessões (appendonly, allkeys-lru 64mb)
- **cron**: Tarefas agendadas (Python 3.11, TZ America/Sao_Paulo)

### Comandos Úteis

```bash
# Parar containers
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

## Desenvolvimento Local

### Setup

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar migrações
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py migrate

# Coletar arquivos estáticos
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py collectstatic --noinput

# Criar superusuário (opcional)
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py createsuperuser

# Executar servidor
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py runserver
```

### Validação de Mudanças

```bash
# Verificar sintaxe e configuração
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py check

# Verificar se há migrações pendentes (sem criar)
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py makemigrations --check --dry-run
```

## Variáveis de Ambiente

### Obrigatórias

- `SECRET_KEY`: Chave secreta do Django
- `DEBUG`: `True` ou `False`
- `ALLOWED_HOSTS`: Hosts permitidos (separados por vírgula)
- `POSTGRES_DB`: Nome do banco de dados
- `POSTGRES_USER`: Usuário do PostgreSQL
- `POSTGRES_PASSWORD`: Senha do PostgreSQL
- `POSTGRES_HOST`: Host do PostgreSQL
- `POSTGRES_PORT`: Porta do PostgreSQL
- `REDIS_HOST`: Host do Redis
- `REDIS_PORT`: Porta do Redis
- `REDIS_DB`: Número do banco Redis
- `DEFAULT_USER_PASSWORD`: Senha padrão para novos usuários
- `SYSTEM_HIDDEN_EMAIL`: Email do sistema oculto (ex.: `example@example.com`)
- `BACKUP_RETENTION_DAYS`: Dias de retenção de backups
- `RECAPTCHA_PUBLIC_KEY`: Chave pública do reCAPTCHA v3
- `RECAPTCHA_PRIVATE_KEY`: Chave privada do reCAPTCHA v3
- `RECAPTCHA_DOMAIN`: Domínio do reCAPTCHA (ex.: `www.google.com`)
- `RECAPTCHA_REQUIRED_SCORE`: Score mínimo (0.0 a 1.0, recomendado 0.5)

### Opcionais

- `DOMAIN`: Domínio principal (usado em `CSRF_TRUSTED_ORIGINS` e Traefik)
- `WHATSAPP_GROUP_URL`: URL do grupo WhatsApp (exposto em templates via context processor)

## Configuração do Nginx

O Nginx atua como proxy reverso e serve arquivos estáticos/media.

### Configuração Traefik

Labels para integração com Traefik (rede externa `proxy`):
- `traefik.enable=true`
- `traefik.http.routers.nations-flow.rule=Host(...)`
- `traefik.http.routers.nations-flow.entrypoints=websecure`
- `traefik.http.routers.nations-flow.tls.certresolver=myresolver`

### Rate Limiting e Segurança

- Login: 60 req/min (burst 60)
- API: 10 req/s
- Static: 50 req/s
- Conexões simultâneas: 200/IP
- **Importante**: `set_real_ip_from 172.16.0.0/12` + `real_ip_header X-Forwarded-For` para IP real do cliente (sem isso, rate limit vira global pelo IP do Traefik)

### CSP para reCAPTCHA v3

O `nginx/nginx.conf` inclui `Content-Security-Policy` permitindo `www.google.com` e `www.gstatic.com` para o reCAPTCHA v3 do login. Se `RECAPTCHA_DOMAIN` for `www.recaptcha.net`, atualize a CSP.

## Tarefas Agendadas (Cron)

### Processamento de Notificações

Comando executado hourly:
```bash
python manage.py process_repeat_notifications [--dry-run]
```

### Backup de Banco de Dados

Executado diariamente às 02:00 (TZ America/Sao_Paulo):
```bash
python manage.py backup_postgres
```
Salva em `/backups/` (volume montado no container cron).

### Variáveis de Ambiente no Cron

O cron não herda variáveis de ambiente. O `start-cron.sh` serializa o `.env` em `/etc/cron.env` e o crontab faz `source /etc/cron.env` antes de cada comando.

## Backup

### Banco de Dados (PostgreSQL)

```bash
# Backup
docker-compose exec db pg_dump -U postgres nationsflow > backup.sql

# Restaurar
docker-compose exec -T db psql -U postgres nationsflow < backup.sql
```

### Arquivos Media

```bash
# Backup
tar -czf media_backup.tar.gz media/

# Restaurar
tar -xzf media_backup.tar.gz
```

## Monitoramento

### Health Check

Endpoint: `/health/` (nginx health check em `/health`, Django em `/health/`)

Verifica:
- Conexão com banco de dados
- Status da aplicação

### Logs

- Django: `/app/logs/django.log` (container web)
- Nginx: `/var/log/nginx/` (volume `$HOME/logs/.../nginx`)
- Cron: `/var/log/` (volume `$HOME/logs/.../cron`)

## Troubleshooting

### Problemas Comuns

1. **Banco de dados não conecta**
   - Verifique variáveis de ambiente
   - Verifique se container db está rodando (`docker-compose ps`)

2. **Arquivos estáticos não carregam**
   - Execute `collectstatic`: `docker-compose exec web python manage.py collectstatic --noinput`
   - Verifique permissões do diretório staticfiles

3. **Redis não conecta**
   - Verifique variáveis de ambiente
   - Verifique se container redis está rodando

4. **Notificações não processam**
   - Verifique se container cron está rodando
   - Execute comando manualmente: `docker-compose exec web python manage.py process_repeat_notifications`

5. **Rate limit global (todos usuários bloqueados)**
   - Verifique `set_real_ip_from 172.16.0.0/12` no `nginx/nginx.conf`
   - Se a rede do Traefik mudar de faixa, ajuste esse CIDR

6. **reCAPTCHA v3 falha no login (produção)**
   - Verifique `RECAPTCHA_DOMAIN` definida (ex.: `www.google.com`)
   - Verifique `RECAPTCHA_PUBLIC_KEY` e `RECAPTCHA_PRIVATE_KEY`
   - Confirme `FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'` no settings
   - Verifique se templates `django_recaptcha/widget_v3.html` e `includes/js_v3.html` existem

## Deploy Automatizado

Push em `main` → `.github/workflows/deploy.yml` → SSH na VPS → `git pull` + `docker compose up -d --build --remove-orphans` + `docker image prune -f`. Diretório VPS: `~/projects/nations-flow`.

Script manual `deploy-nginx.sh` (raiz): rebuild nginx + collectstatic + health checks.
