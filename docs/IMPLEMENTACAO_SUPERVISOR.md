# Implementação do Supervisor - Guia Rápido

## 🎯 Resumo da Solução

Adicionar um novo role **Supervisor** que:
- ✅ Vê transações de **Tesoureiros** que compartilham os mesmos campos
- ✅ Apenas transações de **igrejas dos seus campos**
- ❌ NÃO vê transações de Admins ou outros Supervisores

## 📋 Checklist de Implementação

### 1. Modelo User
- [ ] Adicionar `'supervisor'` em `ROLE_CHOICES`
- [ ] Adicionar método `is_supervisor()`
- [ ] Criar migration

### 2. Helper Function
- [ ] Criar `get_transactions_for_user(user)` em `app/utils.py` ou `app/views.py`

### 3. Views a Atualizar
- [ ] `index()` - Dashboard
- [ ] `transaction_list()` - Lista de transações
- [ ] `transaction_list_api()` - API JSON
- [ ] `transaction_summary_api()` - Resumo para dashboard
- [ ] `transaction_export_pdf()` - Exportação PDF
- [ ] `transaction_export_xlsx()` - Exportação Excel
- [ ] `login_view()` - Redirecionamento após login

### 4. Decorators
- [ ] Atualizar `admin_or_treasurer_required` para incluir supervisor
- [ ] (Opcional) Criar `supervisor_required`
- [ ] (Opcional) Criar `admin_or_supervisor_required`

### 5. Formulários
- [ ] Atualizar `UserForm` para validar campos do Supervisor

### 6. Templates
- [ ] Verificar se templates exibem corretamente o role Supervisor

## 🔍 Lógica do Supervisor

```
Supervisor (Campos: [A, B])
    ↓
Pode ver transações de:
    - Tesoureiros que têm Campo A OU Campo B
    - Em igrejas do Campo A OU Campo B
    - Criadas por esses Tesoureiros
```

## 📊 Comparação de Permissões

| Funcionalidade | Admin | Supervisor | Tesoureiro |
|----------------|-------|------------|------------|
| Dashboard | ✅ | ✅ | ❌ |
| Ver todas transações | ✅ | ❌ | ❌ |
| Ver transações próprias | ✅ | ✅ | ✅ |
| Ver transações de tesoureiros (mesmos campos) | ✅ | ✅ | ❌ |
| Criar transações | ✅ | ✅ | ✅ |
| Editar transações | ✅ | ❌ | ❌ |
| Excluir transações | ✅ | ❌ | ❌ |
| Gestão de recursos | ✅ | ❌ | ❌ |

## 🚀 Próximos Passos

1. Revisar a proposta completa em `PROPOSAL_SUPERVISOR.md`
2. Implementar as mudanças seguindo o checklist
3. Testar com diferentes cenários
4. Atualizar documentação

---
**Documento de referência**: `PROPOSAL_SUPERVISOR.md`
