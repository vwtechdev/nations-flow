# Docker

Esta página contém informações detalhadas sobre como usar o Nations Flow com Docker.

## 🐳 Visão Geral

O Nations Flow foi configurado para rodar completamente em containers Docker, oferecendo:

- **Isolamento**: Cada serviço roda em seu próprio container
- **Portabilidade**: Funciona em qualquer sistema com Docker
- **Facilidade de Deploy**: Um comando para iniciar todo o ambiente
- **Consistência**: Mesmo ambiente em desenvolvimento e produção

## 📋 Pré-requisitos

### Instalação do Docker

#### Linux (Ubuntu/Debian)

```bash
# Atualizar pacotes
sudo apt-get update

# Instalar dependências
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
```

#### Arch Linux

```bash
sudo pacman -S docker docker-compose
sudo systemctl enable docker
sudo systemctl start docker
```

#### macOS

```bash
# Instalar Docker Desktop
brew install --cask docker
```

#### Windows

Baixe e instale o [Docker Desktop](https://www.docker.com/products/docker-desktop).

### Verificação da Instalação

```bash
# Verificar versão do Docker
docker --version

# Verificar versão do Docker Compose
docker-compose --version

# Testar instalação
docker run hello-world
```

## 🚀 Início Rápido

### 1. Clone o Repositório

```bash
git clone https://github.com/your-username/nations-flow.git
cd nations-flow
```

### 2. Execute o Script de Inicialização

```bash
./docker-start.sh
```

### 3. Acesse a Aplicação

- **URL**: http://localhost:8000
- **Login**: admin / admin123

## 📁 Estrutura dos Arquivos Docker

```
nations-flow/
├── docker-compose.yml      # Configuração dos serviços
├── Dockerfile             # Imagem do Django
├── .env                   # Variáveis de ambiente
├── docker-start.sh        # Script de inicialização
├── docker-stop.sh         # Script de parada
└── README-Docker.md       # Documentação Docker
```

## 🔧 Configuração Detalhada

### docker-compose.yml

```yaml
version: '3.8'

services:
  # Banco de dados PostgreSQL
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
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nations"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Aplicação Django
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
      db:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
```

### Dockerfile

```dockerfile
# Imagem base Python 3.11
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /usr/src/nations-flow

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Atualizar sistema e instalar dependências
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Atualizar pip e instalar dependências Python
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### .env

```env
# Django Settings
SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1] 0.0.0.0

# Database Configuration for PostgreSQL (Docker)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=nationsflow
DATABASE_USER=nations
DATABASE_PASSWORD=91Jgy0q8a5BnV
DATABASE_HOST=db
DATABASE_PORT=5432
```

## 🛠️ Scripts de Automação

### docker-start.sh

```bash
#!/bin/bash

echo "🚀 Iniciando Nations Flow com Docker Compose..."

# Verificar se o Docker está rodando
if ! sudo docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Parar containers existentes se houver
echo "🛑 Parando containers existentes..."
sudo docker-compose down

# Construir e iniciar os containers
echo "🔨 Construindo e iniciando containers..."
sudo docker-compose up --build -d

# Aguardar um pouco para o banco inicializar
echo "⏳ Aguardando inicialização do banco de dados..."
sleep 10

# Verificar status dos containers
echo "📊 Status dos containers:"
sudo docker-compose ps

echo ""
echo "✅ Nations Flow está rodando!"
echo "🌐 Acesse: http://localhost:8000"
echo ""
echo "👤 Usuários de teste:"
echo "   - Admin: admin / admin123"
echo "   - Tesoureiro: tesoureiro / tesoureiro123"
echo ""
echo "📝 Comandos úteis:"
echo "   - Ver logs: sudo docker-compose logs -f"
echo "   - Parar: ./docker-stop.sh"
echo "   - Reiniciar: sudo docker-compose restart"
```

### docker-stop.sh

```bash
#!/bin/bash

echo "🛑 Parando Nations Flow..."

# Parar containers
sudo docker-compose down

echo "✅ Containers parados com sucesso!"
echo ""
echo "📝 Para iniciar novamente:"
echo "   ./docker-start.sh"
echo "   ou"
echo "   sudo docker-compose up -d"
```

## 📊 Comandos Úteis

### Gerenciamento de Containers

```bash
# Iniciar containers
sudo docker-compose up -d

# Parar containers
sudo docker-compose down

# Ver logs
sudo docker-compose logs -f

# Ver logs de um serviço específico
sudo docker-compose logs -f web
sudo docker-compose logs -f db

# Reiniciar containers
sudo docker-compose restart

# Reconstruir containers
sudo docker-compose up --build -d

# Ver status
sudo docker-compose ps
```

### Comandos Django

```bash
# Executar comandos Django no container
sudo docker-compose exec web python manage.py shell
sudo docker-compose exec web python manage.py createsuperuser
sudo docker-compose exec web python manage.py collectstatic
sudo docker-compose exec web python manage.py migrate
```

### Banco de Dados

```bash
# Acessar PostgreSQL
sudo docker-compose exec db psql -U nations -d nationsflow

# Backup do banco
sudo docker-compose exec db pg_dump -U nations nationsflow > backup.sql

# Restaurar backup
sudo docker-compose exec -T db psql -U nations -d nationsflow < backup.sql

# Ver logs do banco
sudo docker-compose logs db
```

### Debugging

```bash
# Entrar no container
sudo docker-compose exec web bash

# Ver processos
sudo docker-compose top

# Ver uso de recursos
sudo docker stats

# Ver informações do container
sudo docker inspect django-container
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Porta 8000 já em uso

```bash
# Verificar o que está usando a porta
sudo lsof -ti:8000

# Parar o processo
sudo kill -9 $(sudo lsof -ti:8000)

# Ou usar uma porta diferente
sudo docker-compose up -d -p 8001:8000
```

#### 2. Erro de permissão do Docker

```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Fazer logout e login novamente
# Ou usar sudo temporariamente
sudo docker-compose up -d
```

#### 3. Container não inicia

```bash
# Ver logs detalhados
sudo docker-compose logs web

# Reconstruir sem cache
sudo docker-compose build --no-cache

# Verificar espaço em disco
df -h
```

#### 4. Banco de dados não conecta

```bash
# Verificar se o PostgreSQL está rodando
sudo docker-compose ps db

# Ver logs do banco
sudo docker-compose logs db

# Reiniciar apenas o banco
sudo docker-compose restart db
```

#### 5. Migrações não aplicadas

```bash
# Executar migrações manualmente
sudo docker-compose exec web python manage.py migrate

# Verificar status das migrações
sudo docker-compose exec web python manage.py showmigrations
```

### Logs Detalhados

```bash
# Ver todos os logs
sudo docker-compose logs

# Ver logs em tempo real
sudo docker-compose logs -f

# Ver logs de um serviço específico
sudo docker-compose logs -f web
sudo docker-compose logs -f db

# Ver logs com timestamps
sudo docker-compose logs -f -t
```

## 🔧 Configuração de Produção

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: nations-flow-db-prod
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=nations_prod
      - POSTGRES_PASSWORD=senha_forte_aqui
      - POSTGRES_DB=nationsflow_prod
    restart: unless-stopped
    networks:
      - nations-flow-network

  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: nations-flow-web-prod
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - static_volume:/usr/src/nations-flow/static
      - media_volume:/usr/src/nations-flow/media
    ports:
      - "8000:8000"
    env_file:
      - ./.env.prod
    depends_on:
      - db
    restart: unless-stopped
    networks:
      - nations-flow-network

  nginx:
    image: nginx:alpine
    container_name: nations-flow-nginx-prod
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/usr/src/nations-flow/static
      - media_volume:/usr/src/nations-flow/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - nations-flow-network

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  nations-flow-network:
    driver: bridge
```

### Dockerfile.prod

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

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 📋 Checklist Docker

- [ ] Docker instalado e funcionando
- [ ] Docker Compose instalado
- [ ] Repositório clonado
- [ ] Arquivo .env configurado
- [ ] Containers construídos
- [ ] Banco de dados inicializado
- [ ] Migrações aplicadas
- [ ] Dados iniciais criados
- [ ] Aplicação acessível
- [ ] Logs funcionando
- [ ] Backup configurado (produção)

## 📞 Suporte

Se você encontrar problemas com Docker:

1. Verifique a seção [Troubleshooting](troubleshooting.md)
2. Consulte os logs dos containers
3. Verifique a documentação oficial do Docker
4. Abra uma issue no GitHub 