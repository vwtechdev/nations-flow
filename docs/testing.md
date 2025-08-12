# Guia de Testes - Nations Flow

Este documento descreve a estrutura e execução dos testes unitários e de integração do projeto Nations Flow.

## Visão Geral

O projeto utiliza **pytest** como framework de testes principal, com suporte a:
- Testes unitários
- Testes de integração
- Cobertura de código
- Fixtures reutilizáveis
- Marcadores para categorização

## Estrutura dos Testes

```
tests/
├── __init__.py              # Inicialização do módulo
├── conftest.py              # Configurações e fixtures globais
├── test_models.py           # Testes dos modelos Django
├── test_forms.py            # Testes dos formulários
├── test_views.py            # Testes das views HTTP
├── test_decorators.py       # Testes dos decorators de permissão
└── test_integration.py      # Testes de integração e workflows
```

## Configuração

### pytest.ini
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = core.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
    --verbose
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Dependências
```txt
pytest==8.4.1
pytest-django==4.8.0
pytest-cov==4.1.0
```

## Fixtures Disponíveis

### Usuários
- `admin_user`: Usuário com role 'admin'
- `treasurer_user`: Usuário com role 'treasurer'

### Objetos de Dados
- `state`: Estado brasileiro
- `city`: Cidade vinculada a um estado
- `field`: Campo missionário
- `church`: Igreja vinculada a cidade e campo
- `category`: Categoria de transação
- `transaction`: Transação de exemplo

### Requests
- `request_factory`: Factory para criar requests de teste
- `authenticated_request`: Request autenticado como admin
- `authenticated_treasurer_request`: Request autenticado como tesoureiro

## Tipos de Testes

### 1. Testes de Modelos (`test_models.py`)

Testam a criação, validação e métodos dos modelos Django.

**Exemplo:**
```python
def test_transaction_creation(self, admin_user, church, category):
    """Testa a criação de uma transação"""
    transaction = Transaction.objects.create(
        type='income',
        desc='Dízimo mensal',
        category=category,
        value=Decimal('100.00'),
        date='2024-01-15',
        user=admin_user,
        church=church
    )
    assert transaction.type == 'income'
    assert transaction.value == Decimal('100.00')
```

**Cobertura:**
- Criação de objetos
- Validação de campos
- Métodos personalizados
- Relacionamentos
- Ordenação
- Representação string

### 2. Testes de Formulários (`test_forms.py`)

Testam a validação e comportamento dos formulários Django.

**Exemplo:**
```python
def test_transaction_form_valid(self, admin_user, church, category):
    """Testa formulário válido"""
    form_data = {
        'type': 'income',
        'desc': 'Dízimo mensal',
        'category': category.id,
        'value': '100.00',
        'date': '2024-01-15',
        'church': church.id
    }
    form = TransactionForm(data=form_data, user=admin_user)
    assert form.is_valid()
```

**Cobertura:**
- Validação de dados
- Widgets e atributos
- Comportamento específico por usuário
- Mensagens de erro

### 3. Testes de Views (`test_views.py`)

Testam as views HTTP, autenticação e respostas.

**Exemplo:**
```python
def test_transaction_create_post_valid(self, client, admin_user, church, category):
    """Testa POST válido para criação de transação"""
    client.force_login(admin_user)
    response = client.post(reverse('transaction_create'), {
        'type': 'income',
        'desc': 'Dízimo mensal',
        'category': category.id,
        'value': '100.00',
        'date': '2024-01-15',
        'church': church.id
    })
    assert response.status_code == 302
    assert Transaction.objects.count() == 1
```

**Cobertura:**
- Autenticação e autorização
- Métodos GET e POST
- Redirecionamentos
- Contexto das views
- Validação de formulários

### 4. Testes de Decorators (`test_decorators.py`)

Testam os decorators de controle de acesso.

**Exemplo:**
```python
def test_admin_required_with_admin_user(self, authenticated_request, admin_user):
    """Testa se admin pode acessar view protegida"""
    @admin_required
    def test_view(request):
        return "success"
    
    result = test_view(authenticated_request)
    assert result == "success"
```

**Cobertura:**
- Controle de acesso por role
- Redirecionamentos
- Mensagens de erro
- Usuários anônimos

### 5. Testes de Integração (`test_integration.py`)

Testam workflows completos e cenários reais.

**Exemplo:**
```python
def test_complete_transaction_workflow(self, client, admin_user, church, category):
    """Testa workflow completo: criar, editar, excluir transação"""
    client.force_login(admin_user)
    
    # 1. Criar transação
    response = client.post(reverse('transaction_create'), {...})
    assert response.status_code == 302
    
    # 2. Editar transação
    transaction = Transaction.objects.first()
    response = client.post(reverse('transaction_edit', kwargs={'pk': transaction.pk}), {...})
    assert response.status_code == 302
    
    # 3. Excluir transação
    response = client.post(reverse('transaction_delete', kwargs={'pk': transaction.pk}))
    assert response.status_code == 302
    assert not Transaction.objects.filter(pk=transaction.pk).exists()
```

**Cobertura:**
- Workflows completos
- Permissões de usuários
- Cálculos de dados
- Filtros e busca
- APIs AJAX

## Executando os Testes

### Comandos Básicos

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=app --cov-report=html

# Executar testes específicos
pytest tests/test_models.py
pytest tests/test_views.py::TestTransactionViews

# Executar com marcadores
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

### Script de Execução

```bash
# Usar o script automatizado
./run_tests.sh
```

### Opções de Cobertura

```bash
# Cobertura detalhada
pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml

# Cobertura mínima
pytest --cov=app --cov-fail-under=80
```

## Marcadores de Testes

### @pytest.mark.unit
Testes unitários que testam componentes isolados.

### @pytest.mark.integration
Testes de integração que testam workflows completos.

### @pytest.mark.slow
Testes que podem demorar mais para executar.

**Exemplo:**
```python
@pytest.mark.integration
def test_dashboard_with_transactions(self, client, admin_user, church, category):
    """Testa dashboard com transações existentes"""
    # ... teste de integração
```

## Boas Práticas

### 1. Nomenclatura
- Classes de teste: `TestModelName`
- Métodos de teste: `test_action_scenario`
- Fixtures: `noun_description`

### 2. Organização
- Um arquivo por tipo de componente
- Testes relacionados agrupados em classes
- Fixtures reutilizáveis no `conftest.py`

### 3. Assertions
- Use assertions específicas
- Teste um comportamento por teste
- Verifique tanto casos de sucesso quanto de erro

### 4. Dados de Teste
- Use fixtures para dados reutilizáveis
- Crie dados mínimos necessários
- Limpe dados após cada teste

## Debugging de Testes

### Executar Teste Específico
```bash
pytest tests/test_models.py::TestTransaction::test_transaction_creation -v -s
```

### Executar com Debug
```bash
pytest --pdb
```

### Verificar Cobertura
```bash
pytest --cov=app --cov-report=html
# Abrir htmlcov/index.html no navegador
```

## Cobertura de Código

### Relatórios de Cobertura
- **HTML**: `htmlcov/index.html`
- **XML**: `.coverage`
- **Terminal**: Resumo durante execução

### Relatórios de Teste
- **JUnit XML**: `--junitxml=test-results.xml`
- **HTML**: `--html=test-report.html`

## CI/CD

### GitHub Actions
```yaml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=app --cov-report=xml
```

### GitLab CI
```yaml
test:
  script:
    - pip install -r requirements.txt
    - pytest --cov=app
```

## Troubleshooting

### Problemas Comuns

1. **Erro de migração**
   ```bash
   python manage.py migrate
   ```

2. **Fixtures não encontradas**
   ```bash
   pytest --setup-show
   ```

3. **Testes lentos**
   ```bash
   pytest -m "not slow"
   ```

4. **Cobertura baixa**
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```

### Logs de Debug
```bash
pytest -v -s --tb=long
```

## Contribuição

Ao adicionar novos testes:

1. Siga a nomenclatura existente
2. Use fixtures quando possível
3. Adicione marcadores apropriados
4. Mantenha cobertura alta
5. Documente casos complexos

## Recursos Adicionais

- [Documentação pytest](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/) 