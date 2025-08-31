// Variáveis globais para paginação
let currentPage = 1;
let currentFilters = {};

document.addEventListener('DOMContentLoaded', function() {
    const fieldSelect = document.getElementById('field');
    const churchSelect = document.getElementById('church');
    const shepherdSelect = document.getElementById('shepherd');
    
    if (fieldSelect && churchSelect) {
        fieldSelect.addEventListener('change', function() {
            updateChurches();
        });
    }
    
    if (shepherdSelect && churchSelect) {
        shepherdSelect.addEventListener('change', function() {
            updateChurches();
        });
    }
    
    function updateChurches() {
        const selectedField = fieldSelect ? fieldSelect.value : '';
        const selectedShepherd = shepherdSelect ? shepherdSelect.value : '';
        
        // Limpar opções de igreja
        churchSelect.innerHTML = '<option value="">Todas as igrejas</option>';
        
        // Construir parâmetros da requisição
        const params = new URLSearchParams();
        if (selectedField) params.append('field', selectedField);
        if (selectedShepherd && shepherdSelect) params.append('shepherd', selectedShepherd);
        
        if (selectedField || (selectedShepherd && shepherdSelect)) {
            // Fazer requisição AJAX para buscar igrejas filtradas
            fetch(`/get_churches/?${params.toString()}`)
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
    }
    
    // Captura os dados da transação quando o modal de comprovante é aberto
    const proofModal = document.getElementById('proofModal');
    proofModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const proofUrl = button.getAttribute('data-proof-url');
        const transactionId = button.getAttribute('data-transaction-id');
        const transactionDate = button.getAttribute('data-transaction-date');
        const transactionType = button.getAttribute('data-transaction-type');
        const transactionCategory = button.getAttribute('data-transaction-category');
        const transactionChurch = button.getAttribute('data-transaction-church');
        const transactionDesc = button.getAttribute('data-transaction-desc');
        const transactionValue = button.getAttribute('data-transaction-value');
        
        // Preenche os dados da transação no modal
        document.getElementById('proofTransactionId').textContent = transactionId;
        document.getElementById('proofTransactionDate').textContent = transactionDate;
        document.getElementById('proofTransactionType').textContent = transactionType;
        document.getElementById('proofTransactionCategory').textContent = transactionCategory;
        document.getElementById('proofTransactionChurch').textContent = transactionChurch;
        document.getElementById('proofTransactionDesc').textContent = transactionDesc || '-';
        document.getElementById('proofTransactionValue').textContent = transactionValue;
        
        // Atualiza o link de download
        document.getElementById('downloadProofLink').href = proofUrl;
        
        // Carregar e exibir o comprovante
        loadProofContent(proofUrl);
    });
    
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
        user: document.getElementById('userFilter')?.value || '',
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
        const emptyMessage = '<p class="text-muted text-center py-4">Nenhuma transação encontrada.</p>';
        transactionsTable.innerHTML = emptyMessage;
        mobileTransactionsTable.innerHTML = `
            <div class="mobile-card-empty">
                <i class="bi bi-inbox text-muted" style="font-size: 3rem;"></i>
                <p class="mt-2 text-muted">Nenhuma transação encontrada.</p>
            </div>
        `;
        return;
    }
    
    const isAdmin = document.body.dataset.isAdmin === 'true';
    
    // Renderizar tabela desktop
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
    
    // Renderizar cards mobile
    let mobileCardsHTML = '<div class="mobile-cards-container">';
    
    transactions.forEach(transaction => {
        const typeClass = transaction.type === 'income' ? 'success' : 'danger';
        const typeText = transaction.type === 'income' ? 'Entrada' : 'Saída';
        const valueClass = transaction.type === 'income' ? 'success' : 'danger';
        
        // HTML da tabela
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
                    <span class="badge bg-secondary me-1 mb-1">
                        <i class="bi bi-geo-alt"></i>
                        ${transaction.field_name}
                    </span>
                </td>
                <td>${transaction.church_name}</td>
                <td>${truncateText(transaction.desc)}</td>
                <td class="text-${valueClass}">
                    R$ ${transaction.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </td>
                ${isAdmin ? `<td>${transaction.user_name}</td>` : ''}
                <td>
                    ${transaction.proof ? 
                        `                        <button type="button" class="btn btn-sm btn-outline-success me-1" 
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
                        <button type="button" class="btn btn-sm btn-outline-danger" 
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
                        <span class="mobile-card-label">Descrição:</span>
                        <span class="mobile-card-value description">${truncateText(transaction.desc)}</span>
                    </div>
                    <div class="mobile-card-row">
                        <span class="mobile-card-label">Valor:</span>
                        <span class="mobile-card-value money ${transaction.type}">
                            R$ ${transaction.value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </span>
                    </div>
                    ${isAdmin ? `
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">Usuário:</span>
                            <span class="mobile-card-value">${transaction.user_name}</span>
                        </div>
                    ` : ''}
                </div>
                <div class="mobile-card-footer">
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
                                title="Visualizar Comprovante">
                            <i class="bi bi-file-earmark-check"></i> Comprovante
                        </button>` : 
                        `<span class="mobile-card-btn btn-outline-secondary" title="Sem comprovante" style="cursor: not-allowed; opacity: 0.6;">
                            <i class="bi bi-file-earmark-x"></i> Sem comprovante
                        </span>`
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

// Função para carregar e exibir o conteúdo do comprovante
function loadProofContent(proofUrl) {
    const proofContent = document.getElementById('proofContent');
    
    // Mostrar loading
    proofContent.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2 text-muted">Carregando comprovante...</p>
        </div>
    `;
    
    // Extrair informações do arquivo da URL
    const fileName = proofUrl.split('/').pop();
    const fileExtension = fileName.split('.').pop().toLowerCase();
    
    // Preencher informações do arquivo
    document.getElementById('proofFileName').textContent = fileName;
    document.getElementById('proofFileType').textContent = fileExtension.toUpperCase();
    
    // Determinar o tipo de arquivo e exibir adequadamente
    if (['jpg', 'jpeg', 'png'].includes(fileExtension)) {
        // Imagem - exibir diretamente
        const img = document.createElement('img');
        img.src = proofUrl;
        img.className = 'img-fluid';
        img.style.maxHeight = '500px';
        img.style.maxWidth = '100%';
        img.alt = 'Comprovante';
        
        img.onload = function() {
            proofContent.innerHTML = '';
            proofContent.appendChild(img);
            
            // Adicionar informações de tamanho se disponível
            if (this.naturalWidth && this.naturalHeight) {
                const sizeInfo = document.createElement('p');
                sizeInfo.className = 'text-muted mt-2';
                sizeInfo.innerHTML = `<small>Dimensões: ${this.naturalWidth} × ${this.naturalHeight} pixels</small>`;
                proofContent.appendChild(sizeInfo);
            }
        };
        
        img.onerror = function() {
            showProofError('Erro ao carregar a imagem');
        };
        
    } else if (fileExtension === 'pdf') {
        // PDF - mostrar mensagem e botão para abrir em nova aba
        proofContent.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-file-pdf text-danger" style="font-size: 4rem;"></i>
                <p class="mt-2 text-muted">Este é um arquivo PDF</p>
                <p class="text-muted mb-3">Para melhor visualização, abra o arquivo em uma nova aba</p>
                <a href="${proofUrl}" target="_blank" class="btn btn-primary">
                    <i class="bi bi-box-arrow-up-right"></i> Abrir PDF em Nova Aba
                </a>
            </div>
        `;
        
    } else {
        // Outros tipos de arquivo - mostrar mensagem
        proofContent.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-file-earmark-text text-muted" style="font-size: 4rem;"></i>
                <p class="mt-2 text-muted">Visualização não disponível para este tipo de arquivo</p>
                <p class="text-muted"><small>Use o botão de download para abrir o arquivo</small></p>
            </div>
        `;
    }
    
    // Tentar obter informações de tamanho do arquivo (se disponível)
    fetch(proofUrl, { method: 'HEAD' })
        .then(response => {
            const contentLength = response.headers.get('content-length');
            if (contentLength) {
                const sizeInBytes = parseInt(contentLength);
                const sizeInKB = (sizeInBytes / 1024).toFixed(2);
                const sizeInMB = (sizeInBytes / (1024 * 1024)).toFixed(2);
                
                let sizeText;
                if (sizeInBytes < 1024) {
                    sizeText = `${sizeInBytes} bytes`;
                } else if (sizeInBytes < 1024 * 1024) {
                    sizeText = `${sizeInKB} KB`;
                } else {
                    sizeText = `${sizeInMB} MB`;
                }
                
                document.getElementById('proofFileSize').textContent = sizeText;
            }
        })
        .catch(() => {
            document.getElementById('proofFileSize').textContent = 'N/A';
        });
    
    // Adicionar data atual (já que não temos a data real do arquivo)
    const currentDate = new Date().toLocaleDateString('pt-BR');
    document.getElementById('proofFileDate').textContent = currentDate;
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
