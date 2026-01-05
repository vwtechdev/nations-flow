# Deploy e Configuração

## Visão Geral

O Nations Flow suporta múltiplos ambientes de deploy: Docker (produção), PythonAnywhere (testes) e desenvolvimento local.

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
cp .env.example .env
# Edite .env com suas configurações
```

3. **Inicialize o banco de dados (primeira vez)**
```bash
./init-db.sh
```

4. **Inicie os containers**
```bash
docker-compose up -d
```

### Serviços Docker

- **nginx**: Servidor web e proxy reverso (porta 8081)
- **web**: Aplicação Django com Gunicorn (porta 8000)
- **db**: PostgreSQL 15
- **redis**: Redis 7 para cache e sessões
- **cron**: Tarefas agendadas

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
```

## Deploy no PythonAnywhere

### Configuração

1. Execute o script de setup:
```bash
python pythonanywhere_setup.py
```

2. Configure o WSGI file com conteúdo de `pythonanywhere_wsgi.py`

3. Recarregue o web app

### Banco de Dados

- SQLite configurado automaticamente
- Migrações executadas pelo script

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
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser

# Executar servidor
python manage.py runserver
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

## Configuração do Nginx

O Nginx atua como proxy reverso e serve arquivos estáticos.

### Configuração Traefik

Labels para integração com Traefik:
- `traefik.enable=true`
- `traefik.http.routers.nations-flow.rule=Host(...)`
- `traefik.http.routers.nations-flow.entrypoints=websecure`
- `traefik.http.routers.nations-flow.tls.certresolver=myresolver`

## Tarefas Agendadas (Cron)

### Processamento de Notificações

Comando executado periodicamente:
```bash
python manage.py process_repeat_notifications
```

Configurado em `cron/` para execução automática.

## Backup

### Banco de Dados

```bash
# Backup PostgreSQL
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

Endpoint: `/health/`

Verifica:
- Conexão com banco de dados
- Status da aplicação

### Logs

- Django: `/app/logs/django.log`
- Nginx: Volume Docker `nginx_logs`
- Gunicorn: Console

## Troubleshooting

### Problemas Comuns

1. **Banco de dados não conecta**
   - Verifique variáveis de ambiente
   - Verifique se container db está rodando

2. **Arquivos estáticos não carregam**
   - Execute `collectstatic`
   - Verifique permissões do diretório static

3. **Redis não conecta**
   - Verifique variáveis de ambiente
   - Verifique se container redis está rodando

4. **Notificações não processam**
   - Verifique se container cron está rodando
   - Execute comando manualmente para testar
