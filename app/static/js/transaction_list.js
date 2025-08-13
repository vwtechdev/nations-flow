// Variáveis globais para paginação
let currentPage = 1;
let currentFilters = {};

document.addEventListener('DOMContentLoaded', function() {
    const fieldSelect = document.getElementById('field');
    const churchSelect = document.getElementById('church');
    
    if (fieldSelect && churchSelect) {
        fieldSelect.addEventListener('change', function() {
            const selectedField = this.value;
            
            // Limpar opções de igreja
            churchSelect.innerHTML = '<option value="">Todas as igrejas</option>';
            
            if (selectedField) {
                // Fazer requisição AJAX para buscar igrejas do campo selecionado
                fetch(`/get_churches/?field=${selectedField}`)
                    .then(response => response.json())
                    .then(data => {
                        data.churches.forEach(church => {
                            const option = document.createElement('option');
                            option.value = church.id;
                            option.textContent = church.name;
                            churchSelect.appendChild(option);
                        });
                    })
                    .catch(error => {
                        console.error('Erro ao carregar igrejas:', error);
                    });
            }
        });
    }
    
    // Captura os dados da transação quando o modal de exclusão é aberto
    const deleteModal = document.getElementById('deleteModal');
    deleteModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const transactionId = button.getAttribute('data-transaction-id');
        const transactionDate = button.getAttribute('data-transaction-date');
        const transactionType = button.getAttribute('data-transaction-type');
        const transactionCategory = button.getAttribute('data-transaction-category');
        const transactionChurch = button.getAttribute('data-transaction-church');
        const transactionDesc = button.getAttribute('data-transaction-desc');
        const transactionValue = button.getAttribute('data-transaction-value');
        const transactionUser = button.getAttribute('data-transaction-user');
        
        // Preenche os dados no modal
        document.getElementById('transactionId').textContent = transactionId;
        document.getElementById('transactionDate').textContent = transactionDate;
        document.getElementById('transactionType').textContent = transactionType;
        document.getElementById('transactionCategory').textContent = transactionCategory;
        document.getElementById('transactionChurch').textContent = transactionChurch;
        document.getElementById('transactionDesc').textContent = transactionDesc || '-';
        document.getElementById('transactionValue').textContent = transactionValue ? `R$ ${transactionValue}` : 'R$ 0,00';
        if (transactionUser) {
            document.getElementById('transactionUser').textContent = transactionUser;
        }
        
        // Atualiza a action do formulário
        document.getElementById('deleteForm').action = `/transactions/${transactionId}/delete/`;
    });
    
    // Carregar transações iniciais
    loadTransactions();
    
    // Atualizar botão de exportação com filtros iniciais
    updateExportButton();
    
    // Adicionar listener para o formulário de filtros
    const filterForm = document.getElementById('chartFilterForm');
    if (filterForm) {
        // Remover qualquer listener de submit existente para evitar conflitos
        filterForm.removeEventListener('submit', filterForm._submitHandler);
        
        // Criar um novo handler e armazenar referência
        filterForm._submitHandler = function(e) {
            e.preventDefault();
            e.stopPropagation();
            currentPage = 1; // Reset para primeira página
            loadTransactions();
        };
        
        filterForm.addEventListener('submit', filterForm._submitHandler);
        
        // Também adicionar listener para o botão de filtro especificamente
        const filterButton = filterForm.querySelector('button[type="submit"]');
        if (filterButton) {
            filterButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                currentPage = 1;
                loadTransactions();
            });
        }
    }
    
    // Adicionar listener para limpar filtros
    const clearButton = document.querySelector('a[href*="transaction_list"]');
    if (clearButton) {
        clearButton.addEventListener('click', function(e) {
            e.preventDefault();
            currentPage = 1;
            clearFilters();
            loadTransactions();
        });
    }
});

// Função para carregar transações via AJAX
function loadTransactions() {
    const transactionsTable = document.getElementById('transactionsTable');
    const paginationContainer = document.getElementById('paginationContainer');
    
    // Mostrar loading
    transactionsTable.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2 text-muted">Carregando transações...</p>
        </div>
    `;
    
    // Coletar filtros atuais
    currentFilters = {
        category: document.getElementById('categoryFilter')?.value || '',
        type: document.getElementById('typeFilter')?.value || '',
        date_from: document.getElementById('date_from')?.value || '',
        date_to: document.getElementById('date_to')?.value || '',
        field: document.getElementById('fieldFilter')?.value || '',
        church: document.getElementById('churchFilter')?.value || '',
        page: currentPage
    };
    
    // Atualizar botão de exportação PDF com os filtros atuais
    updateExportButton();
    
    // Construir query string
    const queryString = Object.entries(currentFilters)
        .filter(([key, value]) => value && key !== 'page')
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join('&');
    
    // Fazer requisição AJAX
    fetch(`/transactions/api/?${queryString}&page=${currentPage}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            renderTransactions(data.transactions);
            renderPagination(data.pagination);
            updateTotals(data.totals);
            
            // Mostrar paginação se houver mais de uma página
            if (data.pagination.total_pages > 1) {
                paginationContainer.style.display = 'block';
            } else {
                paginationContainer.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Erro ao carregar transações:', error);
            transactionsTable.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="bi bi-exclamation-triangle"></i>
                    Erro ao carregar transações: ${error.message}
                </div>
            `;
        });
}

// Função para atualizar o botão de exportação PDF com os filtros atuais
function updateExportButton() {
    const exportButton = document.getElementById('exportPdfButton');
    if (exportButton) {
        // Construir query string com os filtros atuais
        const queryString = Object.entries(currentFilters)
            .filter(([key, value]) => value && key !== 'page')
            .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
            .join('&');
        
        // Atualizar o href do botão
        exportButton.href = `/transactions/export-pdf/?${queryString}`;
    }
}

// Função para renderizar transações
function renderTransactions(transactions) {
    const transactionsTable = document.getElementById('transactionsTable');
    
    if (!transactions || transactions.length === 0) {
        transactionsTable.innerHTML = '<p class="text-muted text-center py-4">Nenhuma transação encontrada.</p>';
        return;
    }
    
    const isAdmin = document.body.dataset.isAdmin === 'true';
    
    let tableHTML = `
        <div class="table-responsive">
            <table class="table table-bordered" width="100%" cellspacing="0">
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Tipo</th>
                        <th>Categoria</th>
                        <th>Campo</th>
                        <th>Igreja</th>
                        <th>Descrição</th>
                        <th>Valor</th>
                        ${isAdmin ? '<th>Usuário</th>' : ''}
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    transactions.forEach(transaction => {
        const typeClass = transaction.type === 'income' ? 'success' : 'danger';
        const typeText = transaction.type === 'income' ? 'Entrada' : 'Saída';
        const valueClass = transaction.type === 'income' ? 'success' : 'danger';
        
        tableHTML += `
            <tr>
                <td>${transaction.date}</td>
                <td>
                    <span class="badge bg-${typeClass}">
                        ${typeText}
                    </span>
                </td>
                <td>${transaction.category_name}</td>
                <td>
                    <span class="badge bg-info">
                        <i class="bi bi-geo-alt"></i> ${transaction.field_name}
                    </span>
                </td>
                <td>${transaction.church_name}</td>
                <td>${transaction.desc.length > 50 ? transaction.desc.substring(0, 50) + '...' : transaction.desc}</td>
                <td class="text-${valueClass}">
                    R$ ${transaction.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </td>
                ${isAdmin ? `<td>${transaction.user_name}</td>` : ''}
                <td>
                    ${transaction.can_edit ? `
                        <a href="/transactions/${transaction.id}/edit/" class="btn btn-sm btn-outline-primary" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                data-bs-toggle="modal" 
                                data-bs-target="#deleteModal" 
                                data-transaction-id="${transaction.id}"
                                data-transaction-date="${transaction.date}"
                                data-transaction-type="${typeText}"
                                data-transaction-category="${transaction.category_name}"
                                data-transaction-church="${transaction.church_name}"
                                data-transaction-desc="${transaction.desc}"
                                data-transaction-value="${transaction.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}"
                                data-transaction-user="${transaction.user_name || ''}"
                                title="Excluir">
                            <i class="bi bi-trash"></i>
                        </button>
                    ` : `
                        <a href="/transactions/${transaction.id}/view/" class="btn btn-sm btn-outline-info" title="Visualizar">
                            <i class="bi bi-eye"></i>
                        </button>
                    `}
                </td>   
            </tr>
        `;
    });
    
    tableHTML += `
                </tbody>
            </table>
        </div>
    `;
    
    transactionsTable.innerHTML = tableHTML;
}

// Função para renderizar paginação
function renderPagination(pagination) {
    const paginationList = document.getElementById('paginationList');
    
    if (!pagination || pagination.total_pages <= 1) {
        paginationList.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Botão Primeira
    if (pagination.has_previous) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(1); return false;">
                    Primeira
                </a>
            </li>
        `;
    }
    
    // Botão Anterior
    if (pagination.has_previous) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(${pagination.previous_page}); return false;">
                    Anterior
                </a>
            </li>
        `;
    }
    
    // Página atual
    paginationHTML += `
        <li class="page-item active">
            <span class="page-link">
                Página ${pagination.current_page} de ${pagination.total_pages}
            </span>
        </li>
    `;
    
    // Botão Próxima
    if (pagination.has_next) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(${pagination.next_page}); return false;">
                    Próxima
                </a>
            </li>
        `;
    }
    
    // Botão Última
    if (pagination.has_next) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="goToPage(${pagination.total_pages}); return false;">
                    Última
                </a>
            </li>
        `;
    }
    
    paginationList.innerHTML = paginationHTML;
}

// Função para ir para uma página específica
function goToPage(page) {
    currentPage = page;
    loadTransactions();
}

// Função para atualizar totais
function updateTotals(totals) {
    // Atualizar os cards de totais se existirem
    const totalTransactionsEl = document.querySelector('.card-body .h5.mb-0.font-weight-bold.text-gray-800');
    const totalIncomeEl = document.querySelector('.card-body .h5.mb-0.font-weight-bold[style*="color: #28a745"]');
    const totalExpenseEl = document.querySelector('.card-body .h5.mb-0.font-weight-bold[style*="color: #ff6b6b"]');
    const balanceEl = document.querySelector('.card-body .h5.mb-0.font-weight-bold[style*="color: #673ab7"]');
    
    if (totalTransactionsEl) totalTransactionsEl.textContent = totals.total_transactions;
    if (totalIncomeEl) totalIncomeEl.textContent = `R$ ${totals.total_income.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    if (totalExpenseEl) totalExpenseEl.textContent = `R$ ${totals.total_expense.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    if (balanceEl) balanceEl.textContent = `R$ ${totals.balance.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Função para limpar filtros
function clearFilters() {
    const filterForm = document.getElementById('chartFilterForm');
    if (filterForm) {
        filterForm.reset();
    }
    
    // Limpar filtros específicos
    currentFilters = {
        category: '',
        type: '',
        date_from: '',
        date_to: '',
        field: '',
        church: '',
        page: 1
    };
}
