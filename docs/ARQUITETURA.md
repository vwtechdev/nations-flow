# Arquitetura do Sistema

## Visão Geral da Arquitetura

O Nations Flow segue uma arquitetura **MVC (Model-View-Controller)** adaptada ao padrão Django, utilizando:

- **Models**: Definição dos dados e regras de negócio
- **Views**: Lógica de processamento de requisições
- **Templates**: Apresentação visual (HTML)
- **Forms**: Validação e processamento de dados de entrada

## Estrutura de Camadas

### 1. Camada de Apresentação (Frontend)

- **Templates HTML**: Localizados em `app/templates/`
- **Arquivos Estáticos**: CSS, JavaScript e imagens em `app/static/`
- **Framework CSS**: Bootstrap para responsividade
- **JavaScript**: Vanilla JS para interações AJAX

### 2. Camada de Aplicação (Backend)

#### Views (`app/views.py`)
- Processamento de requisições HTTP
- Lógica de negócio
- Integração com modelos
- Geração de respostas (HTML, JSON, PDF, XLSX)

#### Forms (`app/forms.py`)
- Validação de dados de entrada
- Widgets customizados
- Regras de negócio de formulários

### 3. Camada de Dados

#### Models (`app/models.py`)
- Definição de entidades do banco de dados
- Relacionamentos entre entidades
- Métodos de modelo
- Validações de dados

#### Database
- **PostgreSQL 15**: Banco de dados principal
- **Redis 7**: Cache e sessões

## Padrões de Design Utilizados

### 1. Decorators de Permissão

Sistema de decorators para controle de acesso:

```python
@admin_required          # Apenas administradores
@treasurer_required      # Apenas tesoureiros
@admin_or_treasurer_required  # Admin, tesoureiro ou supervisor
@password_changed_required     # Requer troca de senha
```

**Localização**: `app/decorators.py`

### 2. Middleware Customizado

#### AdminAccessMiddleware
- Restringe acesso ao painel `/admin/` apenas para superusuários
- Todos os outros usuários são redirecionados

**Localização**: `app/middleware.py`

### 3. Backend de Autenticação Customizado

#### EmailBackend
- Permite autenticação usando email em vez de username
- Integrado com o modelo User customizado

**Localização**: `app/backends.py`

### 4. Template Tags Customizados

#### Dashboard Filters
- Filtros personalizados para templates
- Formatação de dados no dashboard

**Localização**: `app/templatetags/dashboard_filters.py`

## Fluxo de Requisições

### 1. Requisição HTTP
```
Cliente → Nginx → Gunicorn → Django
```

### 2. Processamento Django
```
URL Routing → Middleware → View → Form/Model → Template → Response
```

### 3. Autenticação
```
Request → EmailBackend → User Model → Session → Decorator → View
```

## Estrutura de Dados

### Hierarquia de Entidades

```
Field (Campo)
  └── Church (Igreja)
       └── Transaction (Transação)
            ├── Category (Categoria)
            └── User (Usuário)
```

### Relacionamentos Principais

- **Field ↔ Church**: One-to-Many
- **Church ↔ Transaction**: One-to-Many
- **Category ↔ Transaction**: One-to-Many
- **User ↔ Transaction**: One-to-Many
- **User ↔ Field**: Many-to-Many
- **Shepherd ↔ Church**: One-to-Many

## Sistema de Cache

### Configuração Redis
- **Cache de Sessões**: Armazenamento de sessões de usuário
- **Cache de Dados**: Cache de queries frequentes
- **Timeout Padrão**: 5 minutos

### Estratégia de Cache
- Sessões armazenadas em Redis
- Cache de templates (desabilitado atualmente)
- Cache de queries otimizado com `select_related` e `prefetch_related`

## Segurança

### 1. Autenticação
- Login obrigatório para todas as rotas (exceto login e health check)
- Força troca de senha no primeiro login
- Validação de senha forte (mínimo 8 caracteres, maiúsculas, minúsculas, números, símbolos)

### 2. Autorização
- Sistema de roles (Admin, Tesoureiro, Supervisor)
- Controle de acesso por campo
- Filtros de dados baseados em permissões

### 3. Proteção CSRF
- Tokens CSRF em todos os formulários
- Validação automática pelo Django

### 4. Headers de Segurança
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- XSS Protection habilitado

## Performance

### Otimizações de Query

1. **select_related**: Para ForeignKey (reduz queries)
2. **prefetch_related**: Para ManyToMany e relacionamentos reversos
3. **only()** e **defer()**: Carregamento seletivo de campos
4. **Paginação**: Limitação de resultados (50 por página)

### Cache Strategy
- Redis para sessões
- Cache de queries frequentes
- Compressão de dados no Redis

## Deploy e Infraestrutura

### Arquitetura de Containers

```
┌─────────────┐
│   Nginx     │ (Porta 80, Proxy Reverso)
└──────┬──────┘
       │
┌──────▼──────┐
│   Web      │ (Gunicorn, Porta 8000)
│  (Django)  │
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌─▼───┐
│ DB  │ │Redis│
│(PG) │ │     │
└─────┘ └─────┘
```

### Serviços Docker

1. **nginx**: Servidor web e proxy reverso
2. **web**: Aplicação Django (Gunicorn)
3. **db**: PostgreSQL 15
4. **redis**: Redis 7 para cache
5. **cron**: Tarefas agendadas

## Logging

### Configuração
- **Console**: Logs em tempo real
- **Arquivo**: `/app/logs/django.log`
- **Níveis**: INFO (geral), WARNING (requests)

### Loggers
- `django`: Logs gerais do Django
- `django.request`: Requisições com erros
- `gunicorn`: Logs do servidor Gunicorn

## Monitoramento

### Health Check
- Endpoint: `/health/`
- Verifica conexão com banco de dados
- Retorna status JSON

### Métricas
- Logs de acesso (AccessLog)
- Timestamps de criação/atualização
- Logs de erro do Django

## Escalabilidade

### Horizontal Scaling
- Múltiplos workers Gunicorn (3 workers)
- Redis compartilhado para sessões
- PostgreSQL com connection pooling

### Vertical Scaling
- Limites de memória configurados no Docker
- CPU limits por container
- Timeout configurável

## Manutenção

### Tarefas Agendadas (Cron)
- Processamento de notificações repetitivas
- Limpeza de logs antigos (futuro)
- Backup de banco de dados (futuro)

### Comandos de Gerenciamento
- `process_repeat_notifications`: Processa notificações
- `create_initial_data`: Cria dados iniciais
- `test_cache`: Testa conexão com Redis
