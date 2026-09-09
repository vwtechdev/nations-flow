# Nations Flow - Documentação

Sistema de gestão financeira para igrejas desenvolvido em Django.

## Índice da Documentação

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](ARQUITETURA.md)
3. [Modelos de Dados](MODELS.md)
4. [Views e Controllers](VIEWS.md)
5. [Formulários](FORMS.md)
6. [Sistema de Permissões](PERMISSOES.md)
7. [APIs e Endpoints](API.md)
8. [Deploy e Configuração](DEPLOY.md)
9. [Comandos de Gerenciamento](COMANDOS.md)

## Visão Geral

O Nations Flow é um sistema web desenvolvido em Django para gerenciar as finanças de igrejas. O sistema permite:

- **Gestão de Transações**: Registro de entradas e saídas financeiras
- **Organização Hierárquica**: Campos → Igrejas → Transações
- **Controle de Acesso**: Sistema de permissões baseado em roles (Admin, Tesoureiro, Supervisor)
- **Dashboard Analítico**: Visualizações gráficas e relatórios financeiros
- **Notificações**: Sistema de lembretes e notificações repetitivas
- **Exportação**: Geração de relatórios em PDF e Excel

## Tecnologias Utilizadas

- **Backend**: Django 5.2.4
- **Banco de Dados**: PostgreSQL 15
- **Cache**: Redis 7
- **Servidor Web**: Gunicorn + Nginx
- **Containerização**: Docker + Docker Compose
- **Frontend**: HTML, CSS, JavaScript (Bootstrap)

## Estrutura do Projeto

```
nations-flow/
├── app/                    # Aplicação principal Django
│   ├── models.py          # Modelos de dados
│   ├── views.py           # Views e lógica de negócio
│   ├── forms.py           # Formulários
│   ├── urls.py            # Rotas da aplicação
│   ├── decorators.py      # Decorators de permissão
│   ├── middleware.py      # Middlewares customizados
│   ├── backends.py        # Backend de autenticação
│   ├── search.py          # Busca case/acento-insensível
│   ├── templatetags/      # Template tags customizadas
│   ├── migrations/        # Migrações do banco de dados
│   └── management/        # Comandos de gerenciamento
├── core/                  # Configurações do projeto Django
│   ├── models.py          # BaseModel abstrato
│   ├── settings.py        # Configurações principais
│   ├── urls.py            # URLs raiz
│   ├── wsgi.py            # WSGI application
│   └── asgi.py            # ASGI application
├── templates/             # Templates HTML (pages/, registration/, includes/, pwa/)
├── static/                # Arquivos estáticos (css/, js/, img/)
├── docs/                  # Documentação do projeto
├── nginx/                 # Configuração do Nginx
├── cron/                  # Tarefas agendadas
├── docker-compose.yml     # Orquestração Docker
├── Dockerfile            # Imagem Docker da aplicação
├── .env.example          # Exemplo de variáveis de ambiente
└── requirements.txt      # Dependências Python
```

## Funcionalidades Principais

### 1. Gestão de Transações
- Criação, edição e visualização de transações financeiras
- Categorização de transações
- Anexo de comprovantes (PDF, JPG, PNG)
- Validação de comprovantes obrigatórios por categoria
- Filtros avançados (data, categoria, tipo, status, campo, igreja, pastor, usuário)
- Conferência de caixa: marcação em lote como Conferido/Pendente (apenas admin)

### 2. Dashboard
- Visão geral das finanças
- Saldos separados em Caixa e PIX (categorias marcadas como PIX)
- Gráficos por categoria, campo e igreja
- Análise mensal de entradas e saídas
- Transações recentes
- Logs de acesso

### 3. Organização Hierárquica
- **Campos**: Divisão geográfica/administrativa
- **Igrejas**: Unidades locais vinculadas a campos, com contrato (upload)
- **Pastores**: Responsáveis pelas igrejas, com contrato (upload) e histórico por igreja
- **Categorias**: Classificação das transações, com flags de comprovante obrigatório e PIX

### 4. Sistema de Usuários
- Três níveis de acesso: Admin, Tesoureiro, Supervisor
- Controle de campos por usuário
- Força troca de senha no primeiro login
- Logs de acesso ao sistema

### 5. Notificações
- Criação de notificações personalizadas
- Sistema de repetição (diária, semanal, mensal, anual)
- Processamento automático via cron job

### 6. Exportação
- Relatórios em PDF com formatação profissional
- Exportação para Excel (XLSX)
- Aplicação de filtros nas exportações

## Próximos Passos

Consulte os documentos específicos para informações detalhadas:

- [Arquitetura do Sistema](ARQUITETURA.md) - Estrutura técnica e padrões
- [Modelos de Dados](MODELS.md) - Estrutura do banco de dados
- [Views e Controllers](VIEWS.md) - Lógica de negócio e rotas
- [Sistema de Permissões](PERMISSOES.md) - Controle de acesso
- [APIs e Endpoints](API.md) - Endpoints AJAX e APIs
- [Deploy e Configuração](DEPLOY.md) - Guia de instalação e deploy
