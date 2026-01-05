# Views e Controllers

## Visão Geral

O arquivo `app/views.py` contém todas as views (controllers) da aplicação, organizadas por funcionalidade. As views processam requisições HTTP e retornam respostas (HTML, JSON, PDF, XLSX).

## Estrutura das Views

### 1. Views de Autenticação

#### `login_view(request)`
- **Rota**: `/login/`
- **Método**: GET, POST
- **Permissão**: Pública
- **Funcionalidade**: 
  - Autentica usuário usando email e senha
  - Registra login no AccessLog
  - Redireciona conforme role:
    - Admin → Dashboard
    - Tesoureiro/Supervisor → Lista de Transações
  - Força troca de senha se `password_changed=False`

#### `logout_view(request)`
- **Rota**: `/logout/`
- **Método**: GET, POST
- **Permissão**: Autenticado
- **Funcionalidade**:
  - Registra logout no AccessLog
  - Faz logout do usuário
  - Redireciona para login

#### `change_password(request)`
- **Rota**: `/change-password/`
- **Método**: GET, POST
- **Permissão**: Autenticado
- **Decorator**: `@password_changed_required` (mas permite acesso se não trocou)
- **Funcionalidade**:
  - Força troca de senha no primeiro login
  - Valida senha forte
  - Faz logout após trocar senha

---

### 2. Views Principais

#### `index(request)` - Dashboard
- **Rota**: `/`
- **Método**: GET
- **Permissão**: Autenticado, senha alterada
- **Decorators**: `@password_changed_required`
- **Acesso**: Apenas Admin (outros são redirecionados)
- **Funcionalidade**:
  - Dashboard com visão geral das finanças
  - Filtros: data, categoria, tipo, campo, igreja, pastor, usuário
  - Gráficos:
    - Por categoria (entrada/saída)
    - Por campo (entrada/saída)
    - Por igreja individual (entrada/saída)
    - Mensal (linha do tempo)
  - Totais: transações, entradas, saídas, saldo
  - Transações recentes (últimas 10)
  - Logs de acesso recentes (últimos 20, apenas admin)

---

### 3. Views de Transações

#### `transaction_list(request)`
- **Rota**: `/transactions/`
- **Método**: GET
- **Permissão**: Admin, Tesoureiro ou Supervisor
- **Decorators**: `@password_changed_required`, `@admin_or_treasurer_required`
- **Funcionalidade**:
  - Lista transações com paginação AJAX
  - Filtros: busca, categoria, tipo, data, campo, igreja, pastor, usuário
  - Totais calculados
  - Datas padrão: mês atual

#### `transaction_list_api(request)`
- **Rota**: `/transactions/api/`
- **Método**: GET
- **Permissão**: Admin, Tesoureiro ou Supervisor
- **Retorno**: JSON
- **Funcionalidade**:
  - API AJAX para paginação de transações
  - Retorna dados paginados (50 por página)
  - Inclui totais e informações de paginação

#### `transaction_summary_api(request)`
- **Rota**: `/transactions/summary/`
- **Método**: GET, POST
- **Permissão**: Admin, Tesoureiro ou Supervisor
- **Retorno**: JSON
- **Funcionalidade**:
  - API para resumo do dashboard
  - Retorna agregados e séries temporais
  - Aceita filtros via POST (JSON) ou GET
  - Dados: totais, por categoria, por campo, por igreja, mensal

#### `transaction_create(request)`
- **Rota**: `/transactions/create/`
- **Método**: GET, POST
- **Permissão**: Admin, Tesoureiro ou Supervisor
- **Funcionalidade**:
  - Cria nova transação
  - Valida comprovante obrigatório
  - Opção de criar lembrete (apenas admin)
  - Restringe campos/igrejas conforme permissões

#### `transaction_view(request, pk)`
- **Rota**: `/transactions/<pk>/view/`
- **Método**: GET
- **Permissão**: Admin, Tesoureiro ou Supervisor
- **Funcionalidade**:
  - Visualização somente leitura
  - Verifica acesso baseado em role
  - Supervisor pode ver transações de tesoureiros dos mesmos campos

#### `transaction_edit(request, pk)`
- **Rota**: `/transactions/<pk>/edit/`
- **Método**: GET, POST
- **Permissão**: Apenas Admin
- **Decorator**: `@admin_required`
- **Funcionalidade**:
  - Edita transação existente
  - Valida comprovante obrigatório
  - Opção de criar lembrete

#### `transaction_delete(request, pk)`
- **Rota**: `/transactions/<pk>/delete/`
- **Método**: GET, POST
- **Permissão**: Apenas Admin
- **Funcionalidade**:
  - Exclui transação
  - Confirmação via POST

#### `transaction_export_pdf(request)`
- **Rota**: `/transactions/export-pdf/`
- **Método**: GET
- **Permissão**: Admin, Tesoureiro ou Supervisor
- **Retorno**: PDF
- **Funcionalidade**:
  - Exporta transações filtradas para PDF
  - Usa ReportLab
  - Inclui logo, filtros aplicados, totais e tabela de transações
  - Formatação profissional

#### `transaction_export_xlsx(request)`
- **Rota**: `/transactions/export-xlsx/`
- **Método**: GET
- **Permissão**: Admin, Tesoureiro ou Supervisor
- **Retorno**: XLSX
- **Funcionalidade**:
  - Exporta transações filtradas para Excel
  - Usa openpyxl
  - Inclui todas as colunas relevantes
  - Formatação de cabeçalho

---

### 4. Views de Categorias

Todas requerem `@admin_required`.

#### `category_list(request)`
- **Rota**: `/categories/`
- **Funcionalidade**: Lista categorias com busca

#### `category_create(request)`
- **Rota**: `/categories/create/`
- **Funcionalidade**: Cria nova categoria

#### `category_edit(request, pk)`
- **Rota**: `/categories/<pk>/edit/`
- **Funcionalidade**: Edita categoria

#### `category_delete(request, pk)`
- **Rota**: `/categories/<pk>/delete/`
- **Funcionalidade**: Exclui categoria

---

### 5. Views de Igrejas

Todas requerem `@admin_required`.

#### `church_list(request)`
- **Rota**: `/churches/`
- **Funcionalidade**: Lista igrejas com busca e filtro por campo

#### `church_create(request)`
- **Rota**: `/churches/create/`
- **Funcionalidade**: Cria nova igreja

#### `church_edit(request, pk)`
- **Rota**: `/churches/<pk>/edit/`
- **Funcionalidade**: Edita igreja

#### `church_delete(request, pk)`
- **Rota**: `/churches/<pk>/delete/`
- **Funcionalidade**: Exclui igreja

---

### 6. Views de Usuários

Todas requerem `@admin_required`.

#### `user_list(request)`
- **Rota**: `/users/`
- **Funcionalidade**: 
  - Lista usuários
  - Exclui `vwtechdev@gmail.com`
  - Busca por nome, email ou função

#### `user_create(request)`
- **Rota**: `/users/create/`
- **Funcionalidade**: 
  - Cria novo usuário
  - Senha padrão: `nations123456`
  - Força troca de senha

#### `user_edit(request, pk)`
- **Rota**: `/users/<pk>/edit/`
- **Funcionalidade**: 
  - Edita usuário
  - Bloqueia edição de `vwtechdev@gmail.com`

#### `user_delete(request, pk)`
- **Rota**: `/users/<pk>/delete/`
- **Funcionalidade**: 
  - Desativa usuário (não exclui)
  - Bloqueia desativação de `vwtechdev@gmail.com`

#### `user_activate(request, pk)`
- **Rota**: `/users/<pk>/activate/`
- **Funcionalidade**: Reativa usuário desativado

#### `user_reset_password(request, pk)`
- **Rota**: `/users/<pk>/reset-password/`
- **Método**: POST
- **Retorno**: JSON
- **Funcionalidade**: 
  - Reseta senha para padrão
  - Força troca de senha
  - Bloqueia reset de `vwtechdev@gmail.com`

---

### 7. Views de Campos

Todas requerem `@admin_required`.

#### `field_list(request)`
- **Rota**: `/fields/`
- **Funcionalidade**: 
  - Lista campos
  - Anota contagem de igrejas

#### `field_create(request)`
- **Rota**: `/fields/create/`
- **Funcionalidade**: Cria novo campo

#### `field_edit(request, pk)`
- **Rota**: `/fields/<pk>/edit/`
- **Funcionalidade**: Edita campo

#### `field_delete(request, pk)`
- **Rota**: `/fields/<pk>/delete/`
- **Funcionalidade**: Exclui campo

---

### 8. Views de Pastores

Todas requerem `@admin_required`.

#### `shepherd_list(request)`
- **Rota**: `/shepherds/`
- **Funcionalidade**: 
  - Lista pastores
  - Inclui igrejas vinculadas

#### `shepherd_create(request)`
- **Rota**: `/shepherds/create/`
- **Funcionalidade**: Cria novo pastor

#### `shepherd_edit(request, pk)`
- **Rota**: `/shepherds/<pk>/edit/`
- **Funcionalidade**: 
  - Edita pastor
  - Mostra estatísticas (igrejas, campos únicos)

#### `shepherd_delete(request, pk)`
- **Rota**: `/shepherds/<pk>/delete/`
- **Funcionalidade**: Exclui pastor

---

### 9. Views de Logs de Acesso

#### `access_log_list(request)`
- **Rota**: `/access-logs/`
- **Permissão**: Apenas Admin
- **Funcionalidade**:
  - Lista logs do mês atual
  - Busca por usuário
  - Filtro por data (limitado ao mês atual)
  - Exclui logs de `vwtechdev@gmail.com`

---

### 10. Views de Notificações

Todas requerem `@admin_required`.

#### `notification_list(request)`
- **Rota**: `/notifications/`
- **Funcionalidade**: 
  - Lista notificações criadas pelo usuário logado
  - Busca por título ou mensagem

#### `notification_create(request)`
- **Rota**: `/notifications/create/`
- **Funcionalidade**: Cria nova notificação

#### `notification_edit(request, pk)`
- **Rota**: `/notifications/<pk>/edit/`
- **Funcionalidade**: 
  - Edita notificação
  - Apenas notificações criadas pelo usuário

#### `notification_delete(request, pk)`
- **Rota**: `/notifications/<pk>/delete/`
- **Funcionalidade**: 
  - Exclui notificação
  - Apenas notificações criadas pelo usuário

#### `notification_mark_read(request, pk)`
- **Rota**: `/notifications/<pk>/mark-read/`
- **Método**: POST
- **Retorno**: JSON
- **Funcionalidade**: 
  - Marca notificação como lida/não lida
  - Via AJAX

#### `get_today_notifications(request)`
- **Rota**: `/api/notifications/today/`
- **Método**: GET
- **Retorno**: JSON
- **Permissão**: Autenticado
- **Funcionalidade**: 
  - Retorna notificações vencidas ou do dia atual
  - Apenas não lidas
  - Apenas do usuário logado
  - Limite: 10 notificações

---

### 11. APIs AJAX

#### `get_churches(request)`
- **Rota**: `/api/churches/`
- **Método**: GET
- **Retorno**: JSON
- **Funcionalidade**: 
  - Retorna igrejas filtradas por campo e/ou pastor
  - Respeita permissões do usuário

#### `churches_by_field_api(request, field_id)`
- **Rota**: `/api/churches-by-field/<field_id>/`
- **Método**: GET
- **Retorno**: JSON
- **Funcionalidade**: Retorna igrejas de um campo específico

#### `shepherds_by_field_api(request, field_id)`
- **Rota**: `/api/shepherds-by-field/<field_id>/`
- **Método**: GET
- **Retorno**: JSON
- **Funcionalidade**: Retorna pastores de um campo específico

#### `category_info_api(request, category_id)`
- **Rota**: `/api/category/<category_id>/`
- **Método**: GET
- **Retorno**: JSON
- **Funcionalidade**: Retorna informações da categoria (incluindo `mandatory_proof`)

---

### 12. Health Check

#### `health_check(request)`
- **Rota**: `/health/`
- **Método**: GET
- **Permissão**: Pública
- **Retorno**: JSON
- **Funcionalidade**: 
  - Verifica saúde da aplicação
  - Testa conexão com banco de dados
  - Retorna status e timestamp

---

## Funções Auxiliares

### `get_transactions_for_user(user)`
- **Localização**: `app/views.py`
- **Funcionalidade**: 
  - Retorna QuerySet de transações baseado no role
  - **Admin**: Todas as transações
  - **Tesoureiro**: Apenas suas próprias transações
  - **Supervisor**: Suas transações + transações de tesoureiros dos mesmos campos
  - **Outros**: QuerySet vazio

---

## Padrões de Resposta

### HTML (Templates)
- Views principais retornam HTML renderizado
- Contexto inclui dados necessários para o template
- Mensagens via Django Messages Framework

### JSON (APIs)
- Respostas JSON para requisições AJAX
- Formato padronizado:
  ```json
  {
    "success": true/false,
    "data": {...},
    "error": "mensagem de erro"
  }
  ```

### PDF
- Usa ReportLab
- Formato A4
- Inclui logo, filtros, totais e tabela

### XLSX
- Usa openpyxl
- Formatação de cabeçalho
- Colunas ajustadas automaticamente

---

## Tratamento de Erros

- Validações de formulário retornam erros no contexto
- Erros de permissão redirecionam com mensagem
- APIs retornam JSON com status HTTP apropriado
- Logs de erro via Django logging

---

## Performance

### Otimizações Aplicadas
- `select_related()` para ForeignKeys
- `prefetch_related()` para ManyToMany
- Paginação (50 itens por página)
- Cache de queries frequentes
- Limite de resultados em listagens

### Queries Otimizadas
- Dashboard usa agregações do banco
- Listagens usam índices de ForeignKeys
- Filtros aplicados no banco de dados
