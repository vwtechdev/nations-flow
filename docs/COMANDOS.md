# Comandos de Gerenciamento

## Comandos Django Padrão

### Migrações

```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Ver status das migrações
python manage.py showmigrations
```

### Usuários

```bash
# Criar superusuário
python manage.py createsuperuser

# Alterar senha de usuário
python manage.py changepassword <username>
```

### Arquivos Estáticos

```bash
# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### Shell Django

```bash
# Abrir shell interativo
python manage.py shell

# Exemplo de uso
python manage.py shell
>>> from app.models import User, Transaction
>>> User.objects.count()
```

## Comandos Customizados

### process_repeat_notifications

Processa notificações repetitivas e atualiza o mesmo objeto.

**Uso:**
```bash
python manage.py process_repeat_notifications
```

**Opções:**
- `--dry-run`: Executa sem processar, apenas mostra o que seria feito

**Exemplo:**
```bash
# Modo dry-run
python manage.py process_repeat_notifications --dry-run

# Processar notificações
python manage.py process_repeat_notifications
```

**Funcionalidade:**
- Busca notificações com `repeat=True` e `is_read=True`
- Reagenda baseado em `repeat_frequency`
- Reseta `is_read=False`

### test_cache

Testa conexão com Redis.

**Uso:**
```bash
python manage.py test_cache
```

**Funcionalidade:**
- Testa conexão com Redis
- Testa escrita e leitura
- Mostra informações de conexão

### backup_postgres

Realiza backup do PostgreSQL via pg_dump.

**Uso:**
```bash
python manage.py backup_postgres
```

**Funcionalidade:**
- Executa pg_dump via rede Docker
- Salva em `/backups/` com timestamp
- Usa variáveis de ambiente do container

### cleanup_orphan_proofs

Remove comprovantes órfãos em `media/proofs/`.

**Uso:**
```bash
python manage.py cleanup_orphan_proofs
```

**Funcionalidade:**
- Varre `media/proofs/` e remove arquivos não referenciados por nenhuma `Transaction`

### random_data_dev

Popula o banco com dados aleatórios (apenas desenvolvimento).

**Uso:**
```bash
python manage.py random_data_dev
```

**Funcionalidade:**
- Cria campos, igrejas, pastores, categorias, usuários, transações, notificações aleatórios
- **Gitignored** — não existe em produção

## Comandos Docker

### Iniciar/Parar

```bash
# Iniciar em background
docker-compose up -d

# Parar
docker-compose down

# Reiniciar
docker-compose restart
```

### Logs

```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Logs de um serviço específico
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis
```

### Executar Comandos

```bash
# Executar comando no container web
docker-compose exec web python manage.py <comando>

# Acessar shell do container
docker-compose exec web bash

# Executar shell Django
docker-compose exec web python manage.py shell
```

### Backup e Restore

```bash
# Backup do banco
docker-compose exec db pg_dump -U postgres nationsflow > backup.sql

# Restore do banco
docker-compose exec -T db psql -U postgres nationsflow < backup.sql
```

## Exemplos de Uso

### Setup Inicial

```bash
# 1. Clone e configure
git clone <repo>
cd nations-flow

# 2. Crie o arquivo .env com as variáveis obrigatórias (não existe .env.example)
# SECRET_KEY, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST,
# POSTGRES_PORT, REDIS_HOST, REDIS_PORT, REDIS_DB, ALLOWED_HOSTS, DEBUG,
# DEFAULT_USER_PASSWORD, SYSTEM_HIDDEN_EMAIL, BACKUP_RETENTION_DAYS,
# RECAPTCHA_PUBLIC_KEY, RECAPTCHA_PRIVATE_KEY, RECAPTCHA_DOMAIN, RECAPTCHA_REQUIRED_SCORE
# Opcionais: DOMAIN, WHATSAPP_GROUP_URL

# 3. Inicie containers (banco inicializado automaticamente via wait-for-database.sh + migrações)
docker-compose up -d

# 4. Verifique logs
docker-compose logs -f web
```

### Manutenção Diária

```bash
# Verificar status
docker-compose ps

# Ver logs recentes
docker-compose logs --tail=100 web

# Processar notificações
docker-compose exec web python manage.py process_repeat_notifications
```

### Troubleshooting

```bash
# Verificar conexão com banco
docker-compose exec web python manage.py dbshell

# Testar cache
docker-compose exec web python manage.py test_cache

# Verificar migrações pendentes
docker-compose exec web python manage.py showmigrations
```
