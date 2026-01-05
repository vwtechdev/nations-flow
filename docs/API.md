# APIs e Endpoints

## Visão Geral

O Nations Flow expõe várias APIs para comunicação AJAX e integração. As APIs retornam dados em formato JSON e seguem padrões RESTful quando possível.

## Endpoints de API

### 1. Transações

#### `GET /transactions/api/`

**Descrição**: API para listar transações com paginação AJAX

**Permissão**: Admin, Tesoureiro ou Supervisor

**Parâmetros de Query:**
- `category` (int, opcional): ID da categoria
- `type` (string, opcional): `'income'` ou `'expense'`
- `date_from` (string, opcional): Data inicial (YYYY-MM-DD)
- `date_to` (string, opcional): Data final (YYYY-MM-DD)
- `field` (int, opcional): ID do campo
- `church` (int, opcional): ID da igreja
- `shepherd` (int, opcional): ID do pastor
- `user` (int, opcional): ID do usuário (apenas admin)
- `page` (int, opcional): Número da página (padrão: 1)

**Resposta JSON:**
```json
{
  "transactions": [
    {
      "id": 1,
      "date": "15/01/2024",
      "type": "income",
      "type_display": "Entrada",
      "category_name": "Dízimos",
      "field_name": "Campo Sul",
      "church_name": "Igreja Central",
      "shepherd_name": "Pastor João",
      "desc": "Descrição da transação",
      "value": 1000.00,
      "proof": "/media/proofs/2024/01/15/comprovante.pdf",
      "user_name": "João Silva",
      "can_edit": true,
      "can_view": true
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "per_page": 50,
    "total_items": 250,
    "has_previous": false,
    "has_next": true,
    "previous_page": null,
    "next_page": 2
  },
  "totals": {
    "total_transactions": 250,
    "total_income": 50000.00,
    "total_expense": 30000.00,
    "balance": 20000.00
  }
}
```

**Exemplo de Uso:**
```javascript
fetch('/transactions/api/?page=1&category=1&type=income')
  .then(response => response.json())
  .then(data => {
    console.log(data.transactions);
    console.log(data.pagination);
    console.log(data.totals);
  });
```

---

#### `GET /transactions/summary/` ou `POST /transactions/summary/`

**Descrição**: API de resumo para dashboard

**Permissão**: Admin, Tesoureiro ou Supervisor

**Parâmetros (GET ou POST JSON):**
```json
{
  "category": "1",
  "type": "income",
  "field": "2",
  "church": "5",
  "shepherd": "3",
  "user": "10",
  "date_from": "2024-01-01",
  "date_to": "2024-12-31",
  "monthly_use_current_year": false
}
```

**Resposta JSON:**
```json
{
  "totals": {
    "total_transactions": 500,
    "total_income": 100000.00,
    "total_expense": 60000.00,
    "balance": 40000.00
  },
  "categories_data": [
    {
      "category": "Dízimos",
      "income": 50000.00,
      "expense": 0.00
    }
  ],
  "churches_data": [
    {
      "name": "Campo Sul",
      "income": 30000.00,
      "expense": 20000.00
    }
  ],
  "churches_individual_data": [
    {
      "name": "Igreja Central",
      "field": "Campo Sul",
      "income": 15000.00,
      "expense": 10000.00
    }
  ],
  "monthly_data": [
    {
      "month": "Janeiro/2024",
      "month_number": 1,
      "year": 2024,
      "income": 10000.00,
      "expense": 5000.00,
      "balance": 5000.00
    }
  ],
  "filters_applied": {
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "category": "1",
    "type": "income",
    "field": "2",
    "church": "5",
    "shepherd": "3",
    "user": "10"
  }
}
```

---

### 2. Igrejas

#### `GET /api/churches/`

**Descrição**: Retorna igrejas filtradas por campo e/ou pastor

**Permissão**: Autenticado

**Parâmetros de Query:**
- `field` (int, opcional): ID do campo
- `shepherd` (int, opcional): ID do pastor

**Resposta JSON:**
```json
{
  "churches": [
    {
      "id": 1,
      "name": "Igreja Central"
    },
    {
      "id": 2,
      "name": "Igreja Norte"
    }
  ]
}
```

**Exemplo de Uso:**
```javascript
fetch('/api/churches/?field=1')
  .then(response => response.json())
  .then(data => {
    data.churches.forEach(church => {
      console.log(church.name);
    });
  });
```

---

#### `GET /api/churches-by-field/<field_id>/`

**Descrição**: Retorna igrejas de um campo específico com detalhes

**Permissão**: Autenticado (verifica permissão do campo)

**Resposta JSON:**
```json
{
  "field": "Campo Sul",
  "churches": [
    {
      "id": 1,
      "name": "Igreja Central",
      "address": "Rua Principal, 123",
      "shepherd": "Pastor João"
    }
  ]
}
```

**Erros:**
- `403`: Sem permissão para este campo
- `404`: Campo não encontrado
- `500`: Erro interno

---

### 3. Pastores

#### `GET /api/shepherds-by-field/<field_id>/`

**Descrição**: Retorna pastores de um campo específico

**Permissão**: Autenticado (verifica permissão do campo)

**Resposta JSON:**
```json
{
  "field": "Campo Sul",
  "shepherds": [
    {
      "id": 1,
      "name": "Pastor João"
    },
    {
      "id": 2,
      "name": "Pastor Maria"
    }
  ]
}
```

**Erros:**
- `403`: Sem permissão para este campo
- `404`: Campo não encontrado
- `500`: Erro interno

---

### 4. Categorias

#### `GET /api/category/<category_id>/`

**Descrição**: Retorna informações de uma categoria específica

**Permissão**: Autenticado

**Resposta JSON:**
```json
{
  "id": 1,
  "name": "Dízimos",
  "mandatory_proof": true
}
```

**Erros:**
- `404`: Categoria não encontrada
- `500`: Erro interno

**Exemplo de Uso:**
```javascript
fetch('/api/category/1/')
  .then(response => response.json())
  .then(data => {
    if (data.mandatory_proof) {
      // Comprovante obrigatório
    }
  });
```

---

### 5. Notificações

#### `GET /api/notifications/today/`

**Descrição**: Retorna notificações vencidas ou do dia atual que não foram lidas

**Permissão**: Autenticado

**Resposta JSON:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "title": "Lembrete: Reunião",
      "body": "Reunião de planejamento hoje às 19h",
      "date": "15/01/2024 19:00",
      "created_by": "Admin",
      "repeat": true,
      "repeat_frequency": "Semanalmente"
    }
  ],
  "count": 1
}
```

**Erros:**
- `405`: Método não permitido
- `500`: Erro interno

**Exemplo de Uso:**
```javascript
fetch('/api/notifications/today/')
  .then(response => response.json())
  .then(data => {
    if (data.success && data.count > 0) {
      // Mostrar notificações
      data.notifications.forEach(notification => {
        console.log(notification.title);
      });
    }
  });
```

---

#### `POST /notifications/<pk>/mark-read/`

**Descrição**: Marca notificação como lida/não lida

**Permissão**: Admin (apenas notificações criadas pelo usuário)

**Body JSON:**
```json
{
  "is_read": true
}
```

**Resposta JSON:**
```json
{
  "success": true,
  "message": "Status atualizado com sucesso",
  "is_read": true
}
```

**Erros:**
- `400`: Erro na requisição
- `405`: Método não permitido

**Exemplo de Uso:**
```javascript
fetch('/notifications/1/mark-read/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken()
  },
  body: JSON.stringify({ is_read: true })
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('Notificação marcada como lida');
    }
  });
```

---

### 6. Usuários

#### `POST /users/<pk>/reset-password/`

**Descrição**: Reseta senha do usuário para a senha padrão

**Permissão**: Admin

**Resposta JSON:**
```json
{
  "success": true
}
```

**Erros:**
```json
{
  "success": false,
  "error": "Este usuário não pode ter a senha resetada."
}
```

**Exemplo de Uso:**
```javascript
fetch('/users/5/reset-password/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': getCsrfToken()
  }
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('Senha resetada com sucesso');
    } else {
      alert('Erro: ' + data.error);
    }
  });
```

---

### 7. Health Check

#### `GET /health/`

**Descrição**: Endpoint de health check para monitoramento

**Permissão**: Pública (não requer autenticação)

**Resposta JSON (Sucesso):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.123456Z",
  "database": "connected"
}
```

**Resposta JSON (Erro):**
```json
{
  "status": "unhealthy",
  "timestamp": "2024-01-15T10:30:00.123456Z",
  "error": "Connection refused"
}
```

**Status HTTP:**
- `200`: Sistema saudável
- `500`: Sistema com problemas

**Exemplo de Uso:**
```javascript
fetch('/health/')
  .then(response => response.json())
  .then(data => {
    if (data.status === 'healthy') {
      console.log('Sistema operacional');
    } else {
      console.error('Sistema com problemas:', data.error);
    }
  });
```

---

## Padrões de Resposta

### Sucesso
```json
{
  "success": true,
  "data": {...}
}
```

### Erro
```json
{
  "success": false,
  "error": "Mensagem de erro"
}
```

### Status HTTP
- `200`: Sucesso
- `400`: Bad Request (dados inválidos)
- `403`: Forbidden (sem permissão)
- `404`: Not Found (recurso não encontrado)
- `405`: Method Not Allowed (método HTTP incorreto)
- `500`: Internal Server Error (erro interno)

---

## Autenticação

### CSRF Token

Todas as requisições POST requerem token CSRF:

```javascript
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

fetch('/api/endpoint/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': getCsrfToken()
  }
});
```

### Sessão

APIs que requerem autenticação verificam a sessão do usuário automaticamente via decorators Django.

---

## Filtros e Permissões

### Filtros Automáticos

As APIs aplicam filtros automaticamente baseados no role do usuário:

- **Admin**: Todos os dados
- **Tesoureiro**: Apenas seus dados
- **Supervisor**: Seus dados + dados de tesoureiros dos mesmos campos

### Verificação de Permissões

APIs que acessam recursos específicos verificam permissões:

```python
# Exemplo: churches_by_field_api
if not request.user.fields.filter(pk=field.pk).exists():
    return JsonResponse({'error': 'Sem permissão'}, status=403)
```

---

## Exemplos de Integração

### Exemplo 1: Carregar Igrejas Dinamicamente

```javascript
// Quando campo é selecionado
document.getElementById('id_field').addEventListener('change', function() {
  const fieldId = this.value;
  
  fetch(`/api/churches/?field=${fieldId}`)
    .then(response => response.json())
    .then(data => {
      const churchSelect = document.getElementById('id_church');
      churchSelect.innerHTML = '<option value="">Selecione uma igreja</option>';
      
      data.churches.forEach(church => {
        const option = document.createElement('option');
        option.value = church.id;
        option.textContent = church.name;
        churchSelect.appendChild(option);
      });
    });
});
```

### Exemplo 2: Verificar Comprovante Obrigatório

```javascript
document.getElementById('id_category').addEventListener('change', function() {
  const categoryId = this.value;
  
  fetch(`/api/category/${categoryId}/`)
    .then(response => response.json())
    .then(data => {
      const proofField = document.getElementById('id_proof');
      
      if (data.mandatory_proof) {
        proofField.required = true;
        proofField.setAttribute('aria-required', 'true');
      } else {
        proofField.required = false;
        proofField.removeAttribute('aria-required');
      }
    });
});
```

### Exemplo 3: Paginação AJAX

```javascript
function loadTransactions(page = 1) {
  const params = new URLSearchParams({
    page: page,
    category: document.getElementById('id_category').value,
    type: document.getElementById('id_type').value
  });
  
  fetch(`/transactions/api/?${params}`)
    .then(response => response.json())
    .then(data => {
      // Renderizar transações
      renderTransactions(data.transactions);
      
      // Atualizar paginação
      updatePagination(data.pagination);
      
      // Atualizar totais
      updateTotals(data.totals);
    });
}
```

---

## Boas Práticas

### 1. Tratamento de Erros
Sempre trate erros nas requisições:

```javascript
fetch('/api/endpoint/')
  .then(response => {
    if (!response.ok) {
      throw new Error('Erro na requisição');
    }
    return response.json();
  })
  .then(data => {
    // Processar dados
  })
  .catch(error => {
    console.error('Erro:', error);
    // Mostrar mensagem ao usuário
  });
```

### 2. Validação de Dados
Valide dados antes de enviar:

```javascript
if (!fieldId || !churchId) {
  alert('Selecione campo e igreja');
  return;
}
```

### 3. Loading States
Mostre indicadores de carregamento:

```javascript
const button = document.getElementById('submit-btn');
button.disabled = true;
button.textContent = 'Carregando...';

fetch('/api/endpoint/')
  .then(response => response.json())
  .then(data => {
    // Processar
  })
  .finally(() => {
    button.disabled = false;
    button.textContent = 'Enviar';
  });
```

### 4. Cache de Requisições
Cache requisições frequentes quando apropriado:

```javascript
const cache = {};

function getCachedData(key, fetchFn) {
  if (cache[key]) {
    return Promise.resolve(cache[key]);
  }
  
  return fetchFn().then(data => {
    cache[key] = data;
    return data;
  });
}
```
