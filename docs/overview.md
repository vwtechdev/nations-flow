# Visão Geral

## O que é o Nations Flow?

O **Nations Flow** é um sistema de gestão financeira desenvolvido especificamente para igrejas e organizações religiosas. O projeto nasceu da necessidade de ter um controle financeiro eficiente e transparente, permitindo que líderes e tesoureiros gerenciem receitas e despesas de forma organizada.

## 🎯 Objetivos do Projeto

### Principais Metas

- **Transparência Financeira**: Fornecer visibilidade completa sobre as finanças da igreja
- **Controle de Despesas**: Acompanhar gastos e receitas de forma detalhada

- **Multi-igreja**: Suportar múltiplas igrejas e campos
- **Interface Intuitiva**: Interface simples e fácil de usar
- **Segurança**: Controle de acesso e permissões por usuário

### Público-Alvo

- **Pastores e Líderes**: Visão geral das finanças
- **Tesoureiros**: Gestão detalhada de transações
- **Administradores**: Controle de usuários e configurações
- **Membros**: Transparência sobre o uso dos recursos

## 🏗️ Arquitetura do Sistema

### Backend (Django)

O sistema é construído sobre o framework Django, oferecendo:

- **ORM Robusto**: Gerenciamento de banco de dados com PostgreSQL
- **Sistema de Autenticação**: Controle de usuários e permissões
- **Admin Interface**: Painel administrativo integrado
- **API REST**: Endpoints para integração futura
- **Sistema de Templates**: Renderização dinâmica de páginas

### Frontend

- **Bootstrap 5**: Framework CSS para design responsivo
- **JavaScript Vanilla**: Interatividade e funcionalidades dinâmicas
- **Bootstrap Icons**: Ícones consistentes
- **Chart.js**: Gráficos interativos para o dashboard

### Banco de Dados

- **PostgreSQL**: Banco de dados relacional robusto
- **Migrações**: Controle de versão do esquema
- **Backup Automatizado**: Sistema de backup e restauração

## 📊 Módulos Principais

### 1. Dashboard
- Visão geral das finanças
- Gráficos de receitas e despesas
- Indicadores de performance
- Resumo mensal e anual

### 2. Gestão de Usuários
- Criação e edição de usuários
- Controle de permissões por papel
- Histórico de atividades
- Perfis personalizados

### 3. Gestão de Igrejas
- Cadastro de igrejas
- Organização por campos
- Informações de contato
- Endereços e telefones

### 4. Transações Financeiras
- Registro de receitas e despesas
- Categorização de transações
- Anexos de comprovantes
- Aprovação de transações



## 🔐 Sistema de Segurança

### Controle de Acesso

O sistema implementa um controle de acesso baseado em papéis (RBAC):

- **Admin**: Acesso completo ao sistema
- **Tesoureiro**: Gestão de transações
- **Pastor**: Visualização de dados
- **Membro**: Acesso limitado a informações públicas

### Autenticação

- Login seguro com Django
- Sessões gerenciadas
- Logout automático
- Proteção contra ataques comuns

## 📱 Responsividade

O Nations Flow é totalmente responsivo, funcionando em:

- **Desktop**: Interface completa com sidebar
- **Tablet**: Layout adaptado para telas médias
- **Mobile**: Interface otimizada para smartphones

## 🚀 Tecnologias Utilizadas

### Backend
- **Django 5.2.4**: Framework web principal
- **Python 3.11**: Linguagem de programação
- **PostgreSQL**: Banco de dados
- **psycopg2**: Driver PostgreSQL para Python

### Frontend
- **HTML5**: Estrutura das páginas
- **CSS3**: Estilização e animações
- **JavaScript**: Interatividade
- **Bootstrap 5**: Framework CSS
- **Chart.js**: Gráficos e visualizações

### DevOps
- **Docker**: Containerização
- **Docker Compose**: Orquestração de containers
- **Git**: Controle de versão
- **MkDocs**: Documentação

## 📈 Roadmap

### Versão Atual (1.0)
- ✅ Sistema básico de gestão financeira
- ✅ Dashboard interativo
- ✅ Gestão de usuários
- ✅ Relatórios básicos
- ✅ Interface responsiva

### Próximas Versões
- 🔄 API REST completa
- 🔄 Integração com sistemas bancários
- 🔄 App mobile
- 🔄 Notificações em tempo real
- 🔄 Backup na nuvem
- 🔄 Múltiplos idiomas

## 🤝 Contribuição

O Nations Flow é um projeto open-source e aceita contribuições da comunidade. Veja o [Guia de Contribuição](contributing.md) para mais detalhes sobre como participar do desenvolvimento.

## 📄 Licença

Este projeto está licenciado sob a MIT License, permitindo uso comercial e modificações. 