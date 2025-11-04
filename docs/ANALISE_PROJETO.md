# Análise do Projeto Nations Flow

## 📋 Visão Geral

**Nations Flow** é um sistema de gestão financeira desenvolvido especificamente para igrejas, construído com Django 5.2.4 e Python 3.12. O sistema permite controle de transações financeiras (entradas e saídas), organização por categorias, campos geográficos, igrejas e usuários com diferentes níveis de permissão.

## 🏗️ Arquitetura e Tecnologias

### Stack Tecnológico
- **Backend**: Django 5.2.4 (Python 3.12)
- **Banco de Dados**: PostgreSQL 15 (produção) / SQLite (desenvolvimento/testes)
- **Cache/Sessões**: Redis 7
- **Servidor Web**: Gunicorn com 3 workers
- **Proxy Reverso**: Nginx
- **Orquestração**: Docker Compose
- **TLS/SSL**: Traefik (proxy reverso externo)

### Dependências Principais
- `django==5.2.4` - Framework web
- `psycopg2-binary==2.9.10` - Driver PostgreSQL
- `gunicorn==23.0.0` - Servidor WSGI
- `django-redis==5.4.0` - Cache Redis
- `reportlab==4.1.0` - Geração de PDFs
- `Pillow==11.3.0` - Processamento de imagens
- `openpyxl==3.1.0` - Exportação Excel
- `python-dotenv==1.1.1` - Gerenciamento de variáveis de ambiente

## 📁 Estrutura do Projeto

```
nations-flow/
├── app/                    # Aplicação principal Django
│   ├── models.py          # 8 modelos de dados
│   ├── views.py           # Views do sistema (2500+ linhas)
│   ├── forms.py           # Formulários Django
│   ├── urls.py            # Rotas da aplicação
│   ├── admin.py           # Configuração do admin Django
│   ├── decorators.py      # Decorators de permissão
│   ├── middleware.py      # Middleware customizado
│   ├── backends.py        # Backend de autenticação por email
│   ├── templates/         # Templates HTML
│   ├── static/            # Arquivos estáticos (CSS, JS, imagens)
│   └── management/        # Comandos Django customizados
│       └── commands/
│           ├── create_initial_data.py
│           ├── process_repeat_notifications.py
│           └── test_cache.py
├── core/                  # Configurações Django
│   ├── settings.py        # Configurações principais
│   ├── urls.py            # URLs raiz
│   ├── wsgi.py            # WSGI application
│   └── asgi.py            # ASGI application
├── nginx/                 # Configuração Nginx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── nginx-production.conf
├── database/              # Scripts de backup
├── cron/                  # Tarefas agendadas
├── docker-compose.yml     # Orquestração Docker
├── Dockerfile             # Imagem da aplicação
├── requirements.txt       # Dependências produção
└── requirements-dev.txt  # Dependências desenvolvimento
```

## 🗄️ Modelos de Dados

### 1. **Field** (Campo)
- Representa divisões geográficas
- Campos: `name`, `created_at`, `updated_at`

### 2. **Shepherd** (Pastor)
- Representa pastores responsáveis
- Campos: `name`, `created_at`, `updated_at`

### 3. **Church** (Igreja)
- Representa unidades locais
- Relacionamentos: `shepherd` (FK), `field` (FK)
- Campos: `name`, `address`, `created_at`, `updated_at`

### 4. **User** (Usuário)
- Estende `AbstractUser` do Django
- **Roles**: `admin`, `treasurer`
- Campos customizados:
  - `role`: Função do usuário
  - `fields`: ManyToMany com Field (campos acessíveis)
  - `password_changed`: Flag de senha alterada
  - `email`: Campo único (USERNAME_FIELD)
- Métodos: `is_admin()`, `is_treasurer()`, `get_fields()`, `has_field()`

### 5. **Category** (Categoria)
- Categorias de transações
- Campos: `name`, `mandatory_proof` (obriga comprovante), `created_at`, `updated_at`

### 6. **Transaction** (Transação)
- **Tipo**: `income` (entrada) ou `expense` (saída)
- Relacionamentos: `category` (FK), `user` (FK), `church` (FK)
- Campos: `type`, `desc`, `value`, `date`, `proof` (arquivo), `created_at`, `updated_at`
- Validação: Verifica se comprovante é obrigatório baseado na categoria

### 7. **AccessLog** (Log de Acesso)
- Registra login/logout dos usuários
- Campos: `user` (FK), `action`, `timestamp`, `ip_address`
- **Exceção**: Não salva logs do superuser `vwtechdev@gmail.com`

### 8. **Notification** (Notificação)
- Sistema de notificações com repetição
- Campos: `title`, `body`, `date`, `is_read`
- **Repetição**: `repeat`, `repeat_frequency` (daily/weekly/monthly/annually)
- Relacionamento: `original_notification` (FK self) para rastrear notificações repetidas
- Método: `calculate_next_repeat_date()` para calcular próxima repetição

## 🔐 Sistema de Autenticação e Permissões

### Autenticação
- **Backend customizado**: `EmailBackend` - permite login com email
- **Campo único**: Email é usado como USERNAME_FIELD
- **Força troca de senha**: Usuários devem trocar senha no primeiro login

### Níveis de Permissão

1. **Superuser**
   - Acesso total ao Django Admin
   - Usuário especial: `vwtechdev@gmail.com` (sem logs de acesso)

2. **Administrador** (`admin`)
   - Acesso completo ao sistema
   - Dashboard completo
   - Gestão de todos os recursos (campos, igrejas, usuários, transações, etc.)
   - Visualização de logs de acesso

3. **Tesoureiro** (`treasurer`)
   - Acesso restrito às transações
   - Visualização apenas de transações próprias
   - Filtros limitados aos campos atribuídos ao usuário
   - Redirecionado automaticamente para lista de transações após login

### Decorators de Permissão
- `@admin_required`: Apenas administradores
- `@treasurer_required`: Apenas tesoureiros
- `@admin_or_treasurer_required`: Admin ou tesoureiro
- `@password_changed_required`: Força troca de senha

### Middleware
- `AdminAccessMiddleware`: Restringe acesso ao Django Admin apenas para superusers

## 📊 Funcionalidades Principais

### 1. Dashboard (Admin)
- Visão geral financeira
- Filtros avançados:
  - Período (data início/fim)
  - Categoria
  - Tipo (entrada/saída)
  - Campo, Igreja, Pastor, Usuário
- Métricas:
  - Total de entradas
  - Total de saídas
  - Saldo
  - Gráficos e estatísticas

### 2. Gestão de Transações
- CRUD completo (Create, Read, Update, Delete)
- Validação de comprovante obrigatório por categoria
- Upload de comprovantes (PDF, imagens)
- Filtros avançados
- Exportação:
  - **PDF** (ReportLab)
  - **Excel/XLSX** (openpyxl)

### 3. Gestão de Categorias
- CRUD completo
- Configuração de comprovante obrigatório

### 4. Gestão de Igrejas
- CRUD completo
- Relacionamento com Campo e Pastor

### 5. Gestão de Usuários
- CRUD completo
- Atribuição de campos (ManyToMany)
- Ativação/desativação de usuários
- Reset de senha
- Exclusão do superuser `vwtechdev@gmail.com` das listagens

### 6. Gestão de Campos
- CRUD completo
- Divisão geográfica

### 7. Gestão de Pastores
- CRUD completo

### 8. Sistema de Notificações
- CRUD completo
- Marcação de leitura
- **Repetição automática**:
  - Diária
  - Semanal
  - Mensal
  - Anual
- Comando Django: `process_repeat_notifications` para processar repetições

### 9. Logs de Acesso
- Visualização de histórico de login/logout
- Filtro por usuário e período
- Exclusão automática de logs do superuser `vwtechdev@gmail.com`

## 🐳 Infraestrutura Docker

### Serviços

1. **web** (Aplicação Django)
   - Gunicorn com 3 workers
   - Timeout: 120s
   - Memory: 512M-1G
   - CPU: 0.5-1.0
   - Health check: `/health/`

2. **nginx** (Proxy Reverso)
   - Porta: 8081:80
   - Serve arquivos estáticos e media
   - Integração com Traefik
   - Memory: 256M-512M
   - CPU: 0.25-0.5
   - Health check: `/health`

3. **db** (PostgreSQL 15)
   - Volume persistente: `./db_data`
   - Configuração via `.env`

4. **redis** (Cache/Sessões)
   - Max memory: 256MB
   - Policy: allkeys-lru
   - AOF habilitado
   - Memory: 128M-256M

5. **backup** (Backup Automático)
   - Scripts de backup do PostgreSQL
   - Volume: `./backups`

6. **cron** (Tarefas Agendadas)
   - Processamento de notificações repetidas
   - Outras tarefas agendadas
   - Volume: `./cron_logs`

### Redes Docker
- `nations-flow_net`: Rede interna
- `proxy`: Rede externa (Traefik)

## ⚙️ Configurações Importantes

### Settings.py

#### Cache Redis
- Backend: `django_redis.cache.RedisCache`
- Compressão: zlib
- Serializer: JSON
- Timeout padrão: 300s (5 minutos)
- Prefixo: `nationsflow`

#### Sessões
- Engine: Cache (Redis)
- Cookie age: 3600s (1 hora)

#### Segurança
- `SECURE_BROWSER_XSS_FILTER = True`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `X_FRAME_OPTIONS = 'DENY'`
- Proxy SSL: Configurado para Traefik
- CSRF Trusted Origins: `nationsflow.com.br`

#### Upload
- Max size: 1MB
- Media root: `/app/media`
- Static root: `/app/static`

#### Internacionalização
- Language: `pt-br`
- Timezone: `America/Sao_Paulo`
- Date format: `d/m/Y`

### Traefik Labels (Nginx)
- Domínios: `nationsflow.com.br`, `www.nationsflow.com.br`
- Entrypoint: `websecure`
- TLS: Certificado automático via Let's Encrypt
- Priority: 100

## 📝 Comandos Django Customizados

### 1. `create_initial_data`
- Cria dados iniciais do sistema
- Usuários padrão, categorias, etc.

### 2. `process_repeat_notifications`
- Processa notificações com repetição
- Cria novas notificações baseadas na frequência
- Deve ser executado via cron

### 3. `test_cache`
- Testa funcionalidade do cache Redis

## 🔄 Fluxos Importantes

### Fluxo de Login
1. Usuário acessa `/login/`
2. Autenticação com email/senha
3. Registro no `AccessLog`
4. Verificação de `password_changed`
5. Redirecionamento:
   - Admin → Dashboard
   - Tesoureiro → Lista de Transações

### Fluxo de Troca de Senha
1. Primeiro login força redirecionamento
2. Formulário de troca de senha
3. Após troca: logout automático
4. Login novamente com nova senha

### Fluxo de Notificações Repetidas
1. Admin cria notificação com repetição
2. Sistema calcula `next_repeat_date`
3. Comando cron executa `process_repeat_notifications`
4. Cria nova notificação baseada na original
5. Atualiza `next_repeat_date` da original

## 🎨 Frontend

### Templates
- Bootstrap 5 (assumido pelo uso de classes)
- Templates organizados em:
  - `pages/`: Páginas principais
  - `registration/`: Autenticação

### JavaScript
- Validação de formulários
- Filtros dinâmicos
- AJAX para APIs
- Toggle de senha

### CSS
- Customização de formulários
- Tabelas responsivas
- Estilos específicos por página

## 📈 APIs AJAX

- `/api/churches-by-field/<id>/` - Igrejas por campo
- `/api/shepherds-by-field/<id>/` - Pastores por campo
- `/api/category/<id>/` - Informações da categoria
- `/api/notifications/today/` - Notificações do dia
- `/transactions/api/` - Lista de transações (JSON)
- `/transactions/summary/` - Resumo de transações (JSON)

## 🔒 Segurança

### Implementações
- ✅ Autenticação obrigatória
- ✅ Troca de senha forçada
- ✅ Controle de acesso por role
- ✅ CSRF protection
- ✅ XSS protection
- ✅ Clickjacking protection
- ✅ Logs de acesso
- ✅ Validação de uploads (tamanho)
- ✅ Restrição de acesso ao Django Admin

### Observações
- ⚠️ Superuser `vwtechdev@gmail.com` tem tratamento especial (sem logs)
- ⚠️ Upload limitado a 1MB (pode ser insuficiente para comprovantes)
- ⚠️ Senhas padrão mencionadas no README (devem ser alteradas)

## 📦 Deploy

### Opções de Deploy

1. **Docker (Produção)** - Recomendado
   - Docker Compose
   - PostgreSQL + Redis
   - Nginx + Traefik
   - Scripts de inicialização

2. **PythonAnywhere** (Testes)
   - SQLite
   - Configuração específica
   - Script de setup

3. **Desenvolvimento Local**
   - SQLite
   - Script `run_local.py`

### Scripts Importantes
- `init-db.sh`: Inicialização do banco (primeira vez)
- `wait-for-database.sh`: Aguarda banco estar pronto
- `wait-for-redis.sh`: Aguarda Redis estar pronto
- `deploy-nginx.sh`: Deploy do Nginx

## 🐛 Pontos de Atenção

1. **Performance**
   - Views muito grandes (2500+ linhas em `views.py`)
   - Considerar refatoração em múltiplos arquivos
   - Cache implementado mas pode ser otimizado

2. **Código**
   - Alguns métodos muito longos
   - Validações de negócio misturadas com views
   - Considerar separação de responsabilidades

3. **Segurança**
   - Senhas padrão documentadas
   - Upload de arquivos limitado mas sem validação de tipo MIME
   - Considerar validação de tipos de arquivo permitidos

4. **Manutenibilidade**
   - Lógica de negócio espalhada
   - Considerar criação de services/helpers
   - Testes unitários não visíveis

5. **Escalabilidade**
   - Gunicorn com workers fixos (3)
   - Redis com memória limitada (256MB)
   - Considerar autoscaling para produção

## ✅ Pontos Fortes

1. ✅ Arquitetura bem estruturada
2. ✅ Separação de ambientes (dev/prod)
3. ✅ Docker bem configurado
4. ✅ Cache e sessões em Redis
5. ✅ Sistema de permissões robusto
6. ✅ Logs de acesso implementados
7. ✅ Exportação PDF e Excel
8. ✅ Sistema de notificações com repetição
9. ✅ Health checks configurados
10. ✅ Backup automático configurado

## 📌 Recomendações

### Curto Prazo
1. Validar tipos MIME de uploads
2. Implementar testes unitários
3. Refatorar views.py em módulos menores
4. Adicionar validação de tamanho de comprovantes por categoria

### Médio Prazo
1. Implementar API REST completa
2. Adicionar documentação de API (Swagger/OpenAPI)
3. Melhorar tratamento de erros
4. Implementar rate limiting
5. Adicionar monitoramento (Sentry, etc.)

### Longo Prazo
1. Migração para Django REST Framework
2. Implementar frontend SPA (React/Vue)
3. Adicionar testes de integração
4. Implementar CI/CD
5. Adicionar métricas e observabilidade

## 📊 Estatísticas do Projeto

- **Modelos**: 8
- **Views**: ~30+ funções
- **Formulários**: 10+
- **Templates**: 20+
- **URLs**: 40+
- **Comandos Django**: 3
- **Serviços Docker**: 6
- **Linhas de código estimadas**: ~15.000+

## 🎯 Conclusão

O **Nations Flow** é um sistema bem estruturado e funcional para gestão financeira de igrejas. Possui uma arquitetura sólida com Docker, implementa boas práticas de segurança e permissões, e oferece funcionalidades completas de CRUD. 

O projeto está pronto para produção, mas se beneficiaria de refatorações para melhorar manutenibilidade e adição de testes para garantir qualidade a longo prazo.

---

**Data da Análise**: 2024
**Versão do Django**: 5.2.4
**Versão do Python**: 3.12
