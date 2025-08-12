# Nations Flow

![Nations Flow Logo](img/icon.svg){ width="200" }

## Sistema de Gestão Financeira para Igrejas

O **Nations Flow** é uma aplicação web desenvolvida em Django para gerenciar as finanças de igrejas e organizações religiosas. O sistema oferece controle completo sobre receitas, despesas e usuários.

## 🚀 Características Principais

- **Dashboard Interativo**: Visualização gráfica das finanças
- **Gestão de Usuários**: Controle de acesso e permissões
- **Gestão de Igrejas**: Múltiplas igrejas e campos
- **Transações Financeiras**: Registro de receitas e despesas

- **Interface Responsiva**: Funciona em desktop e mobile

## 🛠️ Tecnologias

- **Backend**: Django 5.2.4
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Banco de Dados**: PostgreSQL
- **Containerização**: Docker & Docker Compose
- **Documentação**: MkDocs

## 📋 Pré-requisitos

- Python 3.11+
- PostgreSQL
- Docker (opcional)

## 🚀 Início Rápido

### Com Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/your-username/nations-flow.git
cd nations-flow

# Inicie com Docker
./docker-start.sh

# Acesse: http://localhost:8000
# Login: admin / admin123
```

### Instalação Manual

```bash
# Clone o repositório
git clone https://github.com/your-username/nations-flow.git
cd nations-flow

# Configure o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure o banco de dados
# (veja a seção de configuração)

# Execute as migrações
python manage.py migrate

# Crie dados iniciais
python manage.py create_initial_data

# Inicie o servidor
python manage.py runserver
```

## 📖 Documentação

Esta documentação está organizada nas seguintes seções:

- **[Visão Geral](overview.md)**: Entenda o projeto e suas funcionalidades
- **[Instalação](installation.md)**: Guias detalhados de instalação
- **[Docker](docker.md)**: Como usar com containers
- **[Funcionalidades](dashboard.md)**: Detalhes de cada módulo
- **[Administração](backup-restore.md)**: Backup, restauração e troubleshooting

## 🤝 Contribuição

Contribuições são bem-vindas! Veja o [Guia de Contribuição](contributing.md) para mais detalhes.

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](../LICENSE) para detalhes.

---

<div class="grid cards" markdown>

-   :fontawesome-solid-users: __[Visão Geral](overview.md)__
    
    Entenda o projeto Nations Flow e suas principais funcionalidades.

-   :fontawesome-solid-rocket: __[Instalação Rápida](installation.md)__
    
    Configure o Nations Flow em minutos com Docker.

-   :fontawesome-solid-book: __[Documentação Completa](overview.md)__
    
    Explore todos os recursos e funcionalidades do sistema.

-   :fontawesome-solid-code: __[Contribuir](contributing.md)__
    
    Saiba como contribuir para o desenvolvimento do projeto.

</div>
