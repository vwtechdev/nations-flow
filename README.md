## Nations Flow

Sistema de gestão financeira para a Igreja Pentecostal Nações para Cristo

## 🚀 Deploy

### Opção 1: Docker (Recomendado para Produção)

Veja as instruções abaixo para deploy com Docker.

### Opção 2: Desenvolvimento Local (SQLite)

Para desenvolvimento local sem Docker:

```plaintext
# Clone o projeto
git clone <url-do-repositorio>
cd nations-flow

# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure o banco de dados
python manage.py makemigrations
python manage.py migrate

# Colete arquivos estáticos
python manage.py collectstatic --noinput

# Execute o servidor
python manage.py runserver
```

## 📋 Instalação e Configuração (Docker)

### Pré-requisitos

*   Docker
*   Docker Compose

### Primeira Execução

**Clone o repositório**

**Configure as variáveis de ambiente**

**Inicie os containers**

**Inicialize o banco de dados (PRIMEIRA VEZ APENAS)**

## Colete arquivos estáticos

docker-compose exec web python manage.py collectstatic --noinput

````plaintext

### Execuções Subsequentes

Para iniciar o sistema após a primeira configuração:

```bash
docker-compose up -d
````

**IMPORTANTE**:

*   O sistema usa e-mail para login (não username)
*   Troque as senhas no primeiro login!
*   Em produção, certifique-se de que o Traefik esteja configurado corretamente

### Comandos Úteis

```plaintext
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
```

### Estrutura do Projeto

```plaintext
nations-flow/
├── app/                    # Aplicação principal
│   ├── models.py          # Modelos do banco
│   ├── views.py           # Views do sistema
│   ├── urls.py            # URLs da aplicação
│   ├── forms.py           # Formulários Django
│   ├── decorators.py      # Decorators de permissão
│   ├── backends.py        # Backend de autenticação
│   ├── middleware.py      # Middleware customizado
│   ├── templates/         # Templates HTML
│   ├── static/           # Arquivos estáticos (CSS, JS, imagens)
│   ├── management/        # Comandos Django customizados
│   └── migrations/        # Migrações do banco
├── core/                  # Configurações Django
│   ├── settings.py        # Configurações principais
│   ├── urls.py           # URLs principais
│   ├── wsgi.py           # WSGI para produção
│   └── asgi.py           # ASGI para produção
├── backup/                # Scripts de backup
│   ├── backup.sh         # Script de backup
│   ├── Dockerfile        # Imagem para backup
│   └── crontab.txt       # Configuração de cron
├── docker-compose.yml     # Configuração Docker
├── Dockerfile            # Imagem Docker principal
├── wait-for-database.sh  # Script para aguardar banco
├── requirements.txt      # Dependências Python
└── README.md            # Este arquivo
```

### Funcionalidades

*   **Dashboard**: Visão geral das finanças com gráficos e filtros (apenas admin)
*   **Transações**: Gestão de entradas e saídas com anexo de comprovantes
*   **Categorias**: Organização das transações (com validação de comprovante obrigatório)
*   **Campos**: Divisão geográfica das igrejas
*   **Igrejas**: Unidades locais vinculadas a campos e pastores
*   **Pastores**: Gestão de pastores responsáveis pelas igrejas
*   **Usuários**: Gestão de acessos com diferentes níveis de permissão
*   **Notificações**: Sistema de lembretes e notificações
*   **Logs de Acesso**: Auditoria de logins e logouts
*   **Exportação PDF**: Relatórios de transações e gráficos do dashboard

### Permissões

*   **Administrador**: Acesso completo ao sistema, pode gerenciar todos os recursos
*   **Tesoureiro**: Acesso limitado às transações das igrejas dos seus campos

### Banco de Dados

*   **Produção/Docker**: PostgreSQL 15
*   **Desenvolvimento Local**: SQLite (configurado via settings)
*   **Backup**: Sistema automatizado com rclone para nuvem

### Tecnologias

*   **Backend**: Django 5.2, Python 3.12
*   **Banco**: PostgreSQL 15
*   **Servidor**: Gunicorn
*   **Proxy**: Traefik (HTTPS automático)
*   **Containerização**: Docker + Docker Compose
*   **Estáticos**: WhiteNoise
*   **PDF**: ReportLab

## 🔧 Configuração de Desenvolvimento

### Configuração do Banco para Desenvolvimento Local

Se preferir usar SQLite para desenvolvimento, modifique `core/settings.py`:

```python
# Comentar a configuração PostgreSQL e usar SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## 🚨 Troubleshooting

### Problemas Comuns

**Erro de permissão no Docker**:

**Banco não conecta**:

*   Verifique se o PostgreSQL está rodando
*   Confirme as variáveis de ambiente no `.env`
*   Execute `docker-compose logs db` para ver logs do banco

**Arquivos estáticos não carregam**:

**Erro de CSRF**:

*   Verifique se `CSRF_TRUSTED_ORIGINS` está configurado corretamente
*   Em desenvolvimento, use `http://localhost:8000`

**Usuário não consegue fazer login**:

*   Confirme que o e-mail está correto (sistema usa e-mail, não username)
*   Verifique se o usuário foi criado com `create_initial_data`

### Logs e Debug

```plaintext
# Ver logs do container web
docker-compose logs -f web

# Ver logs do banco
docker-compose logs -f db

# Acessar shell do Django
docker-compose exec web python manage.py shell

# Verificar status dos containers
docker-compose ps
```

```plaintext
docker-compose exec web python manage.py collectstatic --noinput
```

```plaintext
sudo chown -R $USER:$USER .
```

```plaintext
# Execute as migrações
docker-compose exec web python manage.py migrate
```

```plaintext
docker-compose up -d
```

```plaintext
git clone <url-do-repositorio>
cd nations-flow
```