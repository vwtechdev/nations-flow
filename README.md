# Nations Flow

Sistema de gestão financeira para igrejas.

## 🚀 Deploy

### Opção 1: Docker (Recomendado para Produção)
Veja as instruções abaixo para deploy com Docker.

### Opção 2: PythonAnywhere (Para Testes)
Para fazer deploy no PythonAnywhere usando SQLite, consulte o [guia completo](README_PYTHONANYWHERE.md).

**Resumo rápido para PythonAnywhere:**
```bash
# Clone o projeto
git clone <url-do-repositorio>
cd nations-flow

# Execute o script de setup
python pythonanywhere_setup.py

# Configure o WSGI file com o conteúdo de pythonanywhere_wsgi.py
# Ajuste o caminho para seu usuário
# Recarregue o web app
```

### Opção 3: Desenvolvimento Local (SQLite)
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

# Execute o script de desenvolvimento
python run_local.py
```

**Ou manualmente:**
```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
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
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Inicialize o banco de dados (PRIMEIRA VEZ APENAS)**
```bash
# Inicializar com dados padrão
./init-db.sh
```

4. **Inicie os containers**
```bash
docker-compose up -d
```

### Execuções Subsequentes

Para iniciar o sistema após a primeira configuração:

```bash
docker-compose up -d
```

### Acessos Padrão

Após a primeira inicialização:

- **URL**: http://localhost:8000
- **Admin**: `admin` / `nations123456`
- **Tesoureiro**: `tesoureiro` / `nations123456`

**IMPORTANTE**: Troque as senhas no primeiro login!

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
```

### Estrutura do Projeto

```
nations-flow/
├── app/                    # Aplicação principal
│   ├── models.py          # Modelos do banco
│   ├── views.py           # Views do sistema
│   ├── templates/         # Templates HTML
│   └── static/           # Arquivos estáticos
├── core/                  # Configurações Django
│   ├── settings.py        # Configurações principais
│   ├── settings_local.py  # Configurações para desenvolvimento local
│   └── settings_pythonanywhere.py  # Configurações para PythonAnywhere
├── docker-compose.yml     # Configuração Docker
├── Dockerfile            # Imagem Docker
├── init-db.sh           # Script de inicialização Docker
├── pythonanywhere_setup.py  # Script para PythonAnywhere
├── pythonanywhere_wsgi.py   # WSGI para PythonAnywhere
├── run_local.py          # Script para desenvolvimento local
├── migrate_to_sqlite.py  # Script de migração para SQLite
├── env_example.txt       # Exemplo de variáveis de ambiente
├── README_PYTHONANYWHERE.md # Guia PythonAnywhere
└── README.md            # Este arquivo
```

### Funcionalidades

- **Dashboard**: Visão geral das finanças (apenas admin)
- **Transações**: Gestão de entradas e saídas
- **Categorias**: Organização das transações
- **Campos**: Divisão geográfica
- **Igrejas**: Unidades locais
- **Usuários**: Gestão de acessos

### Permissões

- **Administrador**: Acesso completo ao sistema
- **Tesoureiro**: Acesso apenas às transações

### Banco de Dados

- **Desenvolvimento/Docker**: PostgreSQL
- **PythonAnywhere**: SQLite (configurado automaticamente)
- **Produção**: Configurável (PostgreSQL recomendado)
