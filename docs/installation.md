# Instalação

Esta página contém guias detalhados para instalar o Nations Flow em diferentes ambientes.

## 🐳 Instalação com Docker (Recomendado)

A forma mais simples e rápida de instalar o Nations Flow é usando Docker Compose.

### Pré-requisitos

- Docker instalado
- Docker Compose instalado
- Git instalado

### Passos

1. **Clone o repositório**
   ```bash
   git clone https://github.com/your-username/nations-flow.git
   cd nations-flow
   ```

2. **Execute o script de inicialização**
   ```bash
   ./docker-start.sh
   ```

3. **Acesse a aplicação**
   - URL: http://localhost:8000
   - Login: admin / admin123

### Comandos Úteis

```bash
# Iniciar
./docker-start.sh

# Parar
./docker-stop.sh

# Ver logs
sudo docker-compose logs -f

# Reconstruir
sudo docker-compose up --build -d
```

## 🖥️ Instalação Manual

### Pré-requisitos

- Python 3.11+
- PostgreSQL 12+
- Git

### Passos Detalhados

#### 1. Clone o Repositório

```bash
git clone https://github.com/your-username/nations-flow.git
cd nations-flow
```

#### 2. Configure o Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

#### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

#### 4. Configure o PostgreSQL

```bash
# Conecte ao PostgreSQL
sudo -u postgres psql

# Crie o banco de dados
CREATE DATABASE nationsflow;

# Crie o usuário
CREATE USER nations_flow_user WITH PASSWORD 'sua_senha_aqui';

# Conceda privilégios
GRANT ALL PRIVILEGES ON DATABASE nationsflow TO nations_flow_user;

# Saia do PostgreSQL
\q
```

#### 5. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Django Settings
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

# Database Configuration
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=nationsflow
DATABASE_USER=nations_flow_user
DATABASE_PASSWORD=sua_senha_aqui
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

#### 6. Execute as Migrações

```bash
python manage.py migrate
```

#### 7. Crie Dados Iniciais

```bash
python manage.py create_initial_data
```

#### 8. Inicie o Servidor

```bash
python manage.py runserver
```

#### 9. Acesse a Aplicação

- URL: http://localhost:8000
- Login: admin / admin123

## 🔧 Configuração de Produção

### Configurações de Segurança

1. **Altere a SECRET_KEY**
   ```python
   # Gere uma nova chave
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Configure DEBUG=False**
   ```env
   DEBUG=0
   ```

3. **Configure ALLOWED_HOSTS**
   ```env
   DJANGO_ALLOWED_HOSTS=seudominio.com www.seudominio.com
   ```

4. **Configure HTTPS**
   - Use um proxy reverso (nginx)
   - Configure SSL/TLS
   - Force HTTPS

### Configuração do Banco de Dados

```env
# Produção
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=nationsflow_prod
DATABASE_USER=nations_flow_prod
DATABASE_PASSWORD=senha_forte_aqui
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### Configuração de Logs

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/nationsflow/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🚀 Deploy com WSGI

### Configuração do Gunicorn

1. **Instale o Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Crie o arquivo de configuração**
   ```python
   # gunicorn.conf.py
   bind = "0.0.0.0:8000"
   workers = 3
   timeout = 120
   ```

3. **Execute com Gunicorn**
   ```bash
   gunicorn core.wsgi:application -c gunicorn.conf.py
   ```

### Configuração do Nginx

```nginx
server {
    listen 80;
    server_name seudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/nations-flow/static/;
    }
}
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão com Banco

```bash
# Verifique se o PostgreSQL está rodando
sudo systemctl status postgresql

# Verifique a conexão
psql -h localhost -U nations_flow_user -d nationsflow
```

#### 2. Erro de Permissões

```bash
# Verifique as permissões do arquivo .env
chmod 600 .env

# Verifique as permissões do diretório
chmod 755 /path/to/nations-flow
```

#### 3. Erro de Dependências

```bash
# Atualize o pip
pip install --upgrade pip

# Reinstale as dependências
pip install -r requirements.txt --force-reinstall
```

#### 4. Erro de Migrações

```bash
# Verifique o status das migrações
python manage.py showmigrations

# Force a aplicação das migrações
python manage.py migrate --fake-initial
```

## 📋 Checklist de Instalação

- [ ] Docker instalado (se usando Docker)
- [ ] Python 3.11+ instalado
- [ ] PostgreSQL instalado e configurado
- [ ] Repositório clonado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] Banco de dados criado
- [ ] Variáveis de ambiente configuradas
- [ ] Migrações executadas
- [ ] Dados iniciais criados
- [ ] Servidor iniciado
- [ ] Aplicação acessível
- [ ] Login funcionando

## 📞 Suporte

Se você encontrar problemas durante a instalação:

1. Verifique a seção [Troubleshooting](troubleshooting.md)
2. Consulte os logs do sistema
3. Abra uma issue no GitHub
4. Entre em contato com a equipe de desenvolvimento 