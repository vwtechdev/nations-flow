// Variáveis globais para paginação
let currentPage = 1;
let currentPerPage = 20;
const PER_PAGE_STORAGE_KEY = 'per_page_transaction_list';
let currentFilters = {};
const FILTER_STORAGE_KEY = 'filters_transaction_list';
let datesExplicit = new URLSearchParams(window.location.search).has('date_from') || new URLSearchParams(window.location.search).has('date_to');

function saveFiltersToStorage() {
    const hasFilters = Object.entries(currentFilters).some(([k, v]) => {
        if (k === 'page') return false;
        if (!datesExplicit && (k === 'date_from' || k === 'date_to')) return false;
        if (Array.isArray(v)) return v.length > 0;
        return v && v !== '';
    });
    if (hasFilters) {
        localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(currentFilters));
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // --- Handlers de modais (sempre registrados primeiro) ---
    
    // Captura os dados da transação quando o modal de comprovante é aberto
    const proofModal = document.getElementById('proofModal');
    if (proofModal) {
        proofModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            if (!button) return;
            const proofUrl = button.getAttribute('data-proof-url');
            if (!proofUrl) return;
        
        const downloadProofLink = document.getElementById('downloadProofLink');
        const fileName = getProofFileName(proofUrl);

        downloadProofLink.href = proofUrl;
        downloadProofLink.download = fileName;
        
        loadProofContent(proofUrl);
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
    
    // Força download do comprovante usando Blob para evitar abrir PDF/imagem no navegador
    const downloadProofLink = document.getElementById('downloadProofLink');
    if (downloadProofLink) {
        downloadProofLink.addEventListener('click', async function(event) {
            event.preventDefault();

            const fileUrl = this.href;
            const fileName = this.download || getProofFileName(fileUrl);

            try {
                const response = await fetch(fileUrl, {
                    credentials: 'same-origin',
                });

                if (!response.ok) {
                    throw new Error('Erro ao baixar arquivo');
                }

                const blob = await response.blob();
                const objectUrl = URL.createObjectURL(blob);

                const temporaryLink = document.createElement('a');
                temporaryLink.href = objectUrl;
                temporaryLink.download = fileName;
                document.body.appendChild(temporaryLink);
                temporaryLink.click();
                temporaryLink.remove();

                URL.revokeObjectURL(objectUrl);
            } catch (error) {
                const temporaryLink = document.createElement('a');
                temporaryLink.href = fileUrl;
                temporaryLink.download = fileName;
                document.body.appendChild(temporaryLink);
                temporaryLink.click();
                temporaryLink.remove();
            }
        });
    }
    
    // Restaurar filtros salvos ao voltar para a página (URL limpa) OU inicializar de URL params
    const urlParams = new URLSearchParams(window.location.search);
    const hasUrlFilters = urlParams.toString().length > 0;
    
    if (!hasUrlFilters) {
        // URL limpa: restaurar de localStorage se houver
        const saved = localStorage.getItem(FILTER_STORAGE_KEY);
        if (saved) {
            try {
                const restored = JSON.parse(saved);
                const params = new URLSearchParams();
                for (const [k, v] of Object.entries(restored)) {
                    if (k === 'page') continue;
                    if (Array.isArray(v)) v.forEach(x => { if (x) params.append(k, x); });
                    else if (v) params.set(k, v);
                }
                if (params.toString()) {
                    window.location.search = params.toString();
                    return;
                }
            } catch (e) {
                localStorage.removeItem(FILTER_STORAGE_KEY);
            }
        }
    } else {
        // URL tem filtros: inicializar estado a partir da URL
        if (urlParams.get('search')) {
            const searchInput = document.getElementById('searchFilter') || document.getElementById('searchFilter_mobile');
            if (searchInput) searchInput.value = urlParams.get('search');
        }
        if (urlParams.get('type')) {
            const typeFilter = document.getElementById('typeFilter') || document.getElementById('typeFilter_mobile');
            if (typeFilter) typeFilter.value = urlParams.get('type');
        }
        if (urlParams.get('date_from')) {
            const dateFrom = document.getElementById('date_from') || document.getElementById('date_from_mobile');
            if (dateFrom) dateFrom.value = urlParams.get('date_from');
        }
        if (urlParams.get('date_to')) {
            const dateTo = document.getElementById('date_to') || document.getElementById('date_to_mobile');
            if (dateTo) dateTo.value = urlParams.get('date_to');
        }
        // Sincronizar seletor de mês com date_from/date_to
        if (urlParams.get('date_from') || urlParams.get('date_to')) {
            datesExplicit = true;
        }
    }

    // Inicializar itens por página (URL > localStorage > 50)
    function initPerPage() {
        const select = document.getElementById('perPageSelect');
        let value = 20;
        const urlValue = new URLSearchParams(window.location.search).get('per_page');
        if (urlValue && [10, 20, 50].includes(Number(urlValue))) {
            value = Number(urlValue);
        } else {
            const saved = localStorage.getItem(PER_PAGE_STORAGE_KEY);
            if (saved && [10, 20, 50].includes(Number(saved))) {
                value = Number(saved);
            }
        }
        currentPerPage = value;
        if (select) select.value = String(value);
    }
    initPerPage();

    // Handler para mudança de itens por página
    const perPageSelect = document.getElementById('perPageSelect');
    if (perPageSelect) {
        perPageSelect.addEventListener('change', function() {
            currentPerPage = Number(this.value);
            try {
                localStorage.setItem(PER_PAGE_STORAGE_KEY, String(currentPerPage));
            } catch (e) {}
            currentPage = 1;
            loadTransactions();
        });
    }

    loadTransactions();
    updateExportButton();
    updateMaisFiltrosBadge();
    
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
            collapseMobileFilters();
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
                collapseMobileFilters();
            });
        }

        // Auto-aplicar ao mudar o tipo (desktop)
        const typeDesktop = document.getElementById('typeFilter');
        if (typeDesktop) {
            typeDesktop.addEventListener('change', function() {
                currentPage = 1;
                loadTransactions();
                updateExportButton();
            });
        }
        
        // Atualizar quando o modal aplicar filtros
        filterForm.addEventListener('filters:applied', function(e) {
            if (e.detail && e.detail.month) datesExplicit = true;
            currentPage = 1;
            loadTransactions();
            updateExportButton();
            updateMaisFiltrosBadge();
            collapseMobileFilters();
        });

        // Adicionar listeners para mudanças nos campos básicos (para atualizar export em tempo real)
        const filterFields = filterForm.querySelectorAll('select, input[type=\"date\"], input[type=\"text\"]');
        filterFields.forEach(field => {
            field.addEventListener('change', function() {
                if (field.type === 'date') datesExplicit = true;
                updateExportButton();
            });
        });
    }

    // --- Bulk actions (desktop, apenas admin) ---
    const isAdmin = document.body.dataset.isAdmin === 'true';
    const bulkActions = document.getElementById('bulkActions');
    if (isAdmin && bulkActions) {
        const transactionsTable = document.getElementById('transactionsTable');

        transactionsTable.addEventListener('change', function(event) {
            if (event.target.id === 'selectAll') {
                document.querySelectorAll('.transaction-checkbox').forEach(cb => cb.checked = event.target.checked);
            }
            updateBulkActions();
        });

        // Atualiza contador ao abrir o modal de confirmação
        document.getElementById('bulkDeleteModal').addEventListener('show.bs.modal', function() {
            const count = document.querySelectorAll('.transaction-checkbox:checked').length;
            document.getElementById('bulkDeleteCount').textContent = count;
        });

        // Excluir em lote via AJAX
        document.getElementById('confirmBulkDelete').addEventListener('click', async function() {
            const checked = [...document.querySelectorAll('.transaction-checkbox:checked')];
            const ids = checked.map(cb => cb.value);
            if (ids.length === 0) {
                bootstrap.Modal.getInstance(document.getElementById('bulkDeleteModal')).hide();
                return;
            }

            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
            const confirmBtn = document.getElementById('confirmBulkDelete');
            confirmBtn.disabled = true;

            try {
                const response = await fetch('/transactions/bulk-delete/', {
                    method: 'POST',
                    headers: {'X-CSRFToken': csrfToken, 'Content-Type': 'application/json'},
                    body: JSON.stringify({ids})
                });

                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    throw new Error(data.error || 'Erro ao excluir transações');
                }

                const data = await response.json();
                bootstrap.Modal.getInstance(document.getElementById('bulkDeleteModal')).hide();
                loadTransactions();
                updateBulkActions();
            } catch (error) {
                alert('Erro ao excluir transações: ' + error.message);
            } finally {
                confirmBtn.disabled = false;
            }
        });
    }

});

// Salvar filtros antes de navegar para criar/editar/visualizar
document.addEventListener('click', function(e) {
    const link = e.target.closest('a');
    if (!link || !link.href) return;
    if (link.href.includes('/create/') || link.href.includes('/edit/') || link.href.includes('/delete/')
        || link.href.includes('/view/')) {
        saveFiltersToStorage();
    }
});

function getProofFileName(fileUrl) {
    const url = new URL(fileUrl, window.location.origin);
    const parts = url.pathname.split('/');
    return decodeURIComponent(parts[parts.length - 1]);
}

// Função para carregar transações via AJAX
// Tornar a função global para ser chamada por outros scripts
window.loadTransactions = function() {
    const transactionsTable = document.getElementById('transactionsTable');
    
    // Mostrar loading
    transactionsTable.innerHTML = `
        <div class="text-center py-4 d-none d-md-block">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2 text-muted">Carregando transações...</p>
        </div>
    `;
    
    // Coletar filtros atuais (inputs hidden do modal)
    const getHiddenArray = name => {
        const inputs = document.querySelectorAll(`input[name="${name}"]`);
        return Array.from(inputs)
            .map(input => input.value)
            .filter(value => value !== null && value !== undefined && value !== '');
    };
    
    currentFilters = {
        search: document.getElementById('searchFilter')?.value || document.getElementById('searchFilter_mobile')?.value || '',
        category: getHiddenArray('category'),
        type: document.getElementById('typeFilter')?.value || document.getElementById('typeFilter_mobile')?.value || '',
        date_from: document.getElementById('date_from')?.value || document.getElementById('date_from_mobile')?.value || '',
        date_to: document.getElementById('date_to')?.value || document.getElementById('date_to_mobile')?.value || '',
        field: getHiddenArray('field'),
        church: getHiddenArray('church'),
        shepherd: getHiddenArray('shepherd'),
        user: getHiddenArray('user'),
        page: currentPage,
        per_page: currentPerPage
    };
    
    updateUrl(currentFilters);
    updateFilterAlert(currentFilters);
    
    // Atualizar botão de exportação PDF com os filtros atuais
    updateExportButton();
    
    // Construir query string - arrays vazios não são incluídos
    const queryParams = [];
    for (const [key, value] of Object.entries(currentFilters)) {
        if (key === 'page') continue;
        if (Array.isArray(value)) {
            // Para arrays, adicionar múltiplos parâmetros
            if (value.length > 0) {
                value.forEach(v => {
                    queryParams.push(`${key}=${encodeURIComponent(v)}`);
                });
            }
        } else if (value) {
            // Para valores únicos, adicionar apenas se não vazio
            queryParams.push(`${key}=${encodeURIComponent(value)}`);
        }
    }
    
    const queryString = queryParams.join('&');
    
    // Fazer requisição AJAX
    fetch(`/transactions/api/?${queryString}&page=${currentPage}&per_page=${currentPerPage}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            renderTransactions(data.transactions);
            renderPagination(data.pagination);
            updateTotals(data.totals);
            saveFiltersToStorage();
        })
        .catch(error => {
            transactionsTable.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="bi bi-exclamation-triangle"></i>
                    Erro ao carregar transações: ${error.message}
                </div>
            `;
        });
}

// Função para atualizar os botões de exportação com os filtros atuais
function updateExportButton() {
    const exportPdfButton = document.getElementById('exportPdfButton');
    const exportPdfButtonMobile = document.getElementById('exportPdfButton_mobile');
    const exportXlsxButton = document.getElementById('exportXlsxButton');
    const exportXlsxButtonMobile = document.getElementById('exportXlsxButton_mobile');
    
    // Construir query string - arrays vazios não são incluídos
    const queryParams = [];
    for (const [key, value] of Object.entries(currentFilters)) {
        if (key === 'page') continue;
        if (Array.isArray(value)) {
            // Para arrays, adicionar múltiplos parâmetros
            if (value.length > 0) {
                value.forEach(v => {
                    queryParams.push(`${key}=${encodeURIComponent(v)}`);
                });
            }
        } else if (value) {
            // Para valores únicos, adicionar apenas se não vazio
            queryParams.push(`${key}=${encodeURIComponent(value)}`);
        }
    }
    
    const queryString = queryParams.join('&');
    
    const pdfExportUrl = `/transactions/export-pdf/?${queryString}`;
    const xlsxExportUrl = `/transactions/export-xlsx/?${queryString}`;
    
    // Atualizar o href dos botões PDF
    if (exportPdfButton) {
        exportPdfButton.href = pdfExportUrl;
    }
    
    if (exportPdfButtonMobile) {
        exportPdfButtonMobile.href = pdfExportUrl;
    }
    
    // Atualizar o href dos botões XLSX
    if (exportXlsxButton) {
        exportXlsxButton.href = xlsxExportUrl;
    }
    
    if (exportXlsxButtonMobile) {
        exportXlsxButtonMobile.href = xlsxExportUrl;
    }
}

// Função para atualizar contador e visibilidade da barra de bulk actions
function updateBulkActions() {
    const bulkActions = document.getElementById('bulkActions');
    if (!bulkActions) return;
    const count = document.querySelectorAll('.transaction-checkbox:checked').length;
    document.getElementById('selectedCount').textContent = count;
    bulkActions.classList.toggle('d-none', count === 0);

    const selectAll = document.getElementById('selectAll');
    if (selectAll) {
        const checkboxes = document.querySelectorAll('.transaction-checkbox');
        const allChecked = checkboxes.length > 0 && [...checkboxes].every(cb => cb.checked);
        const anyChecked = count > 0;
        selectAll.checked = allChecked;
        selectAll.indeterminate = anyChecked && !allChecked;
    }
}

// Função para truncar texto
function truncateText(text, maxLength = 50) {
    if (!text || text === '-') return text;
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

// Função para renderizar transações
function renderTransactions(transactions) {
    const transactionsTable = document.getElementById('transactionsTable');
    const mobileTransactionsTable = document.getElementById('mobileTransactionsTable');
    
    if (!transactions || transactions.length === 0) {
        const emptyMessage = `
            <div class="table-responsive">
                <div class="text-center py-4">
                    <i class="bi bi-receipt display-1 text-muted"></i>
                    <h5 class="text-muted mt-3">Nenhuma transação encontrada</h5>
                    <p class="text-muted">Não foram encontradas transações para os filtros selecionados.</p>
                </div>
            </div>`;
        transactionsTable.innerHTML = emptyMessage;
        mobileTransactionsTable.innerHTML = `
            <div class="mobile-card-empty">
                <i class="bi bi-receipt" style="font-size: 3rem;"></i>
                <h6 class="mt-3">Nenhuma transação encontrada</h6>
                <p class="mt-2 mb-0">Não foram encontradas transações para os filtros selecionados.</p>
            </div>
        `;
        return;
    }
    
    const isAdmin = document.body.dataset.isAdmin === 'true';
    const isSupervisor = document.body.dataset.isSupervisor === 'true';
    const canSeeUser = isAdmin || isSupervisor;
    
    // Renderizar tabela desktop
    let tableHTML = `
        <div class="table-responsive">
            <table class="table table-bordered" width="100%" cellspacing="0">
                <thead>
                    <tr>
                        ${isAdmin ? '<th style="width:30px"><input type="checkbox" id="selectAll" title="Selecionar todos"></th>' : ''}
                        <th>Data</th>
                        <th>Tipo</th>
                        <th>Categoria</th>
                        <th>Campo</th>
                        <th>Igreja</th>
                        <th>Pastor</th>
                        <th>Valor</th>
                        <th>Descrição</th>
                        ${canSeeUser ? '<th>Usuário</th>' : ''}
                        <th class="text-nowrap">Ações</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    // Renderizar cards mobile
    let mobileCardsHTML = '<div class="mobile-cards-container">';
    
    transactions.forEach(transaction => {
        const typeClass = transaction.type === 'income' ? 'success' : 'danger';
        const typeText = transaction.type === 'income' ? 'Entrada' : 'Saída';
        const valueClass = transaction.type === 'income' ? 'success' : 'danger';
        
        // HTML da tabela
        tableHTML += `
            <tr>
                ${isAdmin ? `<td><input type="checkbox" class="transaction-checkbox" value="${transaction.id}"></td>` : ''}
                <td>${transaction.date}</td>
                <td>
                    <span class="badge bg-${typeClass}">
                        ${typeText}
                    </span>
                </td>
                <td>${transaction.category_name}</td>
                <td>
                    <span class="badge bg-secondary me-1 mb-1">
                        <i class="bi bi-geo-alt"></i>
                        ${transaction.field_name}
                    </span>
                </td>
                <td>${transaction.church_name}</td>
                <td>${transaction.shepherd_name || '-'}</td>
                <td class="text-${valueClass}">
                    R$ ${transaction.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </td>
                <td>${truncateText(transaction.desc)}</td>
                ${canSeeUser ? `<td>${transaction.user_name || '-'}</td>` : ''}
                <td class="text-nowrap">
                    ${transaction.proof ? 
                        `<button type="button" class="btn btn-sm btn-outline-success me-1" 
                                data-bs-toggle="modal" 
                                data-bs-target="#proofModal"
                                data-proof-url="${transaction.proof}"
                                data-transaction-id="${transaction.id}"
                                data-transaction-date="${transaction.date}"
                                data-transaction-type="${typeText}"
                                data-transaction-category="${transaction.category_name}"
                                data-transaction-church="${transaction.church_name}"
                                data-transaction-desc="${truncateText(transaction.desc)}"
                                data-transaction-value="${transaction.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}"
                                title="Visualizar Comprovante">
                            <i class="bi bi-file-earmark-check"></i>
                        </button>` : 
                        `<span class="btn btn-sm btn-outline-secondary me-1" title="Sem comprovante" style="cursor: not-allowed;">
                            <i class="bi bi-file-earmark-x"></i>
                        </span>`
                    }
                    ${transaction.can_edit ? `
                        <a href="/transactions/${transaction.id}/edit/" class="btn btn-sm btn-outline-primary me-1" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <button type="button" class="btn btn-sm btn-outline-danger me-1" 
                                data-bs-toggle="modal" 
                                data-bs-target="#deleteModal" 
                                data-transaction-id="${transaction.id}"
                                data-transaction-date="${transaction.date}"
                                data-transaction-type="${typeText}"
                                data-transaction-category="${transaction.category_name}"
                                data-transaction-church="${transaction.church_name}"
                                data-transaction-desc="${truncateText(transaction.desc)}"
                                data-transaction-value="${transaction.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}"
                                data-transaction-user="${transaction.user_name || ''}"
                                title="Excluir">
                            <i class="bi bi-trash"></i>
                        </button>
                    ` : `
                        <a href="/transactions/${transaction.id}/view/" class="btn btn-sm btn-outline-info" title="Visualizar">
                            <i class="bi bi-eye"></i>
                        </a>
                    `}
                </td>   
            </tr>
        `;
        
        // HTML dos cards mobile
        mobileCardsHTML += `
            <div class="mobile-card">
                <div class="mobile-card-header ${transaction.type}">
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Data:</span>
                        <span class="mobile-card-value">${transaction.date}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Tipo:</span>
                        <span class="mobile-card-badge ${transaction.type}">
                            ${transaction.type === 'income' ? 'Entrada' : 'Saída'}
                        </span>
                    </div>
                </div>
                <div class="mobile-card-body">
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Categoria:</span>
                        <span class="mobile-card-value">${transaction.category_name}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Campo:</span>
                        <span class="mobile-card-badge secondary">
                            <i class="bi bi-geo-alt"></i> ${transaction.field_name}
                        </span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Igreja:</span>
                        <span class="mobile-card-value">${transaction.church_name}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Pastor:</span>
                        <span class="mobile-card-value">${transaction.shepherd_name || '-'}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Descrição:</span>
                        <span class="mobile-card-value description">${truncateText(transaction.desc)}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Valor:</span>
                        <span class="mobile-card-value money ${transaction.type}">
                            R$ ${transaction.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </span>
                    </div>
                    ${canSeeUser ? `
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">Usuário:</span>
                            <span class="mobile-card-value">${transaction.user_name}</span>
                        </div>
                    ` : ''}
                </div>
                <div class="mobile-card-footer" style="flex-wrap: nowrap; justify-content: flex-end; gap: 0.5rem;">
                    ${transaction.proof ? 
                        `<button type="button" class="mobile-card-btn btn-outline-success" 
                                data-bs-toggle="modal" 
                                data-bs-target="#proofModal"
                                data-proof-url="${transaction.proof}"
                                data-transaction-id="${transaction.id}"
                                data-transaction-date="${transaction.date}"
                                data-transaction-type="${typeText}"
                                data-transaction-category="${transaction.category_name}"
                                data-transaction-church="${transaction.church_name}"
                                data-transaction-desc="${truncateText(transaction.desc)}"
                                data-transaction-value="${transaction.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}"
                                title="Visualizar Anexo">
                            <i class="bi bi-file-earmark-check"></i> Anexo
                        </button>` : ''
                    }
                    ${transaction.can_edit ? `
                        <a href="/transactions/${transaction.id}/edit/" class="mobile-card-btn btn-outline-primary" title="Editar">
                            <i class="bi bi-pencil"></i> Editar
                        </a>
                        <button type="button" class="mobile-card-btn btn-outline-danger" 
                                data-bs-toggle="modal" 
                                data-bs-target="#deleteModal" 
                                data-transaction-id="${transaction.id}"
                                data-transaction-date="${transaction.date}"
                                data-transaction-type="${typeText}"
                                data-transaction-category="${transaction.category_name}"
                                data-transaction-church="${transaction.church_name}"
                                data-transaction-desc="${truncateText(transaction.desc)}"
                                data-transaction-value="${transaction.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}"
                                data-transaction-user="${transaction.user_name || ''}"
                                title="Excluir">
                            <i class="bi bi-trash"></i> Excluir
                        </button>
                    ` : `
                        <a href="/transactions/${transaction.id}/view/" class="mobile-card-btn btn-outline-info" title="Visualizar">
                            <i class="bi bi-eye"></i> Visualizar
                        </a>
                    `}
                </div>
            </div>
        `;
    });
    
    tableHTML += `
                </tbody>
            </table>
        </div>
    `;
    
    mobileCardsHTML += '</div>';
    
    transactionsTable.innerHTML = tableHTML;
    mobileTransactionsTable.innerHTML = mobileCardsHTML;
    
    updateBulkActions();
}

// Função para renderizar paginação
function renderPagination(pagination) {
    const paginationList = document.getElementById('paginationList');
    const paginationHeader = document.getElementById('paginationHeader');
    const pageInfo = document.getElementById('pageInfo');
    
    if (!pagination || pagination.total_pages <= 1) {
        if (paginationList) paginationList.innerHTML = '';
        if (paginationHeader) paginationHeader.classList.add('d-none');
        return;
    }
    
    if (paginationHeader) paginationHeader.classList.remove('d-none');
    if (pageInfo) pageInfo.textContent = `Página ${pagination.current_page} de ${pagination.total_pages}`;
    const pageInfoMobile = document.getElementById('pageInfoMobile');
    if (pageInfoMobile) pageInfoMobile.textContent = `Página ${pagination.current_page} de ${pagination.total_pages}`;
    
    const firstDisabled = !pagination.has_previous;
    const prevDisabled = !pagination.has_previous;
    const nextDisabled = !pagination.has_next;
    const lastDisabled = !pagination.has_next;
    
    let paginationHTML = `
        <li class="page-item ${firstDisabled ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(1); return false;" aria-label="Primeira página" ${firstDisabled ? 'tabindex="-1" aria-disabled="true"' : ''}>
                <i class="bi bi-chevron-double-left"></i>
            </a>
        </li>
        <li class="page-item ${prevDisabled ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${pagination.previous_page}); return false;" aria-label="Página anterior" ${prevDisabled ? 'tabindex="-1" aria-disabled="true"' : ''}>
                <i class="bi bi-chevron-left"></i>
            </a>
        </li>
        <li class="page-item ${nextDisabled ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${pagination.next_page}); return false;" aria-label="Próxima página" ${nextDisabled ? 'tabindex="-1" aria-disabled="true"' : ''}>
                <i class="bi bi-chevron-right"></i>
            </a>
        </li>
        <li class="page-item ${lastDisabled ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${pagination.total_pages}); return false;" aria-label="Última página" ${lastDisabled ? 'tabindex="-1" aria-disabled="true"' : ''}>
                <i class="bi bi-chevron-double-right"></i>
            </a>
        </li>
    `;
    
    paginationList.innerHTML = paginationHTML;
}

// Função para ir para uma página específica
function goToPage(page) {
    currentPage = page;
    loadTransactions();
}

// Recolher o card de filtros mobile após aplicar filtros
function collapseMobileFilters() {
    const el = document.getElementById('mobileFiltersCollapse');
    if (!el) return;
    if (window.bootstrap && bootstrap.Collapse) {
        const instance = bootstrap.Collapse.getInstance(el) || bootstrap.Collapse.getOrCreateInstance(el);
        if (el.classList.contains('show')) instance.hide();
    }
}

// Atualizar a contagem de filtros avançados selecionados no botão "Mais Filtros"
function updateMaisFiltrosBadge() {
    const count = document.querySelectorAll('#advancedFiltersHidden input[data-filter]').length;
    document.querySelectorAll('.mais-filtros-count').forEach(function(badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.classList.remove('d-none');
        } else {
            badge.classList.add('d-none');
        }
    });
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
        const hiddenContainer = document.getElementById('advancedFiltersHidden');
        if (hiddenContainer) {
            hiddenContainer.innerHTML = '';
        }
    }
    
    // Limpar filtros específicos
    currentFilters = {
        search: '',
        category: [],
        type: '',
        date_from: '',
        date_to: '',
        field: [],
        church: [],
        shepherd: [],
        user: [],
        page: 1
    };
    localStorage.removeItem(FILTER_STORAGE_KEY);
}

function updateUrl(currentFilters) {
    try {
        var params = new URLSearchParams();
        for (var k in currentFilters) {
            if (!datesExplicit && (k === 'date_from' || k === 'date_to')) continue;
            var v = currentFilters[k];
            if (Array.isArray(v)) {
                v.forEach(function(x) { if (x) params.append(k, x); });
            } else if (v) {
                params.set(k, v);
            }
        }
        var qs = params.toString();
        var newUrl = window.location.pathname + (qs ? '?' + qs : '');
        history.replaceState(null, '', newUrl);
    } catch (e) {}
}

function updateFilterAlert(currentFilters) {
    const container = document.getElementById('filterAlertContainer');
    if (!container) return;

    var sourceData = {};
    try {
        const sourceEl = document.getElementById('filtersSourceJson');
        if (sourceEl) {
            sourceData = JSON.parse(sourceEl.textContent) || {};
        }
    } catch (e) {}

    function resolveNames(key, ids) {
        if (!ids || ids.length === 0) return [];
        return ids.map(function(id) {
            var found = (sourceData[key] || []).find(function(item) { return String(item.id) === String(id); });
            return found ? found.text : id;
        }).filter(Boolean);
    }

    var badges = [];

    if (currentFilters.search) {
        badges.push(['Busca', [currentFilters.search]]);
    }
    if (currentFilters.type) {
        badges.push(['Tipo', [currentFilters.type === 'income' ? 'Entrada' : 'Saída']]);
    }
    if (currentFilters.category && currentFilters.category.length > 0) {
        badges.push(['Categorias', resolveNames('category', currentFilters.category)]);
    }
    if (currentFilters.field && currentFilters.field.length > 0) {
        badges.push(['Campos', resolveNames('field', currentFilters.field)]);
    }
    if (currentFilters.church && currentFilters.church.length > 0) {
        badges.push(['Igrejas', resolveNames('church', currentFilters.church)]);
    }
    if (currentFilters.shepherd && currentFilters.shepherd.length > 0) {
        badges.push(['Pastores', resolveNames('shepherd', currentFilters.shepherd)]);
    }
    if (currentFilters.user && currentFilters.user.length > 0) {
        badges.push(['Usuários', resolveNames('user', currentFilters.user)]);
    }
    if (datesExplicit && (currentFilters.date_from || currentFilters.date_to)) {
        var fromStr = currentFilters.date_from ? currentFilters.date_from.split('-').reverse().join('/') : '';
        var toStr = currentFilters.date_to ? currentFilters.date_to.split('-').reverse().join('/') : '';
        badges.push(['Período', [fromStr + ' a ' + toStr]]);
    }

    if (badges.length === 0) {
        container.style.display = 'none';
        return;
    }

    var badgesHtml = badges.map(function(item) {
        return '<span class="badge bg-primary me-1">' + item[0] + ': ' + item[1].join(', ') + '</span>';
    }).join('');

    var alertEl = container.querySelector('.alert');
    if (!alertEl) return;

    alertEl.innerHTML = '<i class="bi bi-funnel-fill me-2"></i>' +
        '<strong>Filtros ativos:</strong> ' + badgesHtml +
        '<a href="?clear" class="btn btn-outline-secondary btn-sm ms-auto">' +
        '<i class="bi bi-x-circle"></i> Limpar filtros</a>';
    container.style.display = 'flex';

    var badgeEl = document.getElementById('mobileFilterCountBadge');
    if (badgeEl) {
        badgeEl.textContent = badges.length;
        badgeEl.classList.toggle('bg-primary', badges.length > 0);
        badgeEl.classList.toggle('bg-secondary', badges.length === 0);
    }

    var desktopBadgeEl = document.getElementById('desktopFilterCountBadge');
    if (desktopBadgeEl) {
        desktopBadgeEl.textContent = badges.length;
        desktopBadgeEl.classList.toggle('bg-primary', badges.length > 0);
        desktopBadgeEl.classList.toggle('bg-secondary', badges.length === 0);
    }
}

// Função para carregar e exibir o conteúdo do comprovante
function loadProofContent(proofUrl) {
    const proofContent = document.getElementById('proofContent');
    
    proofContent.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2 text-muted">Carregando anexo...</p>
        </div>
    `;
    
    const fileName = getProofFileName(proofUrl);
    const fileExtension = fileName.split('.').pop().toLowerCase();
    
    if (['jpg', 'jpeg', 'png'].includes(fileExtension)) {
        const img = document.createElement('img');
        img.src = proofUrl;
        img.className = 'preview-img';
        img.style.maxHeight = '400px';
        img.alt = 'Anexo';
        
        img.onload = function() {
            proofContent.innerHTML = '';
            proofContent.style.cssText = '';
            proofContent.className = 'd-flex align-items-center justify-content-center';
            proofContent.style.minHeight = '350px';
            proofContent.appendChild(img);
        };
        
        img.onerror = function() {
            showProofError('Erro ao carregar a imagem');
        };
        
    } else if (fileExtension === 'pdf') {
        proofContent.style.cssText = '';
        proofContent.className = '';
        proofContent.innerHTML = `
            <iframe src="${proofUrl}" class="w-100" style="height:400px; border:1px solid #e9ecef; border-radius:6px; box-shadow:0 2px 8px rgba(0,0,0,0.1);"></iframe>
        `;
        
    } else {
        proofContent.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-file-earmark-text text-muted" style="font-size: 4rem;"></i>
                <p class="mt-2 text-muted">Visualização não disponível para este tipo de arquivo</p>
                <p class="text-muted"><small>Use o botão de download para abrir o arquivo</small></p>
            </div>
        `;
    }
}

// Função para mostrar erro ao carregar comprovante
function showProofError(message) {
    const proofContent = document.getElementById('proofContent');
    proofContent.innerHTML = `
        <div class="text-center py-4">
            <i class="bi bi-exclamation-triangle text-danger" style="font-size: 4rem;"></i>
            <p class="mt-2 text-danger">${message}</p>
            <p class="text-muted"><small>Verifique se o arquivo ainda existe ou tente novamente</small></p>
        </div>
    `;
}
