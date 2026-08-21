'use strict';

/**
 * ListPagination - JS genérico para paginação AJAX de listas.
 * Configurado via data-* attributes no elemento root.
 *
 * Uso:
 * <div id="listPagination"
 *      data-api-url="/categories/api/"
 *      data-list-type="category"
 *      data-search-id="categorySearch">
 * </div>
 */

class ListPagination {
    constructor(rootEl) {
        this.root = rootEl;
        this.apiUrl = rootEl.dataset.apiUrl;
        this.listType = rootEl.dataset.listType;
        this.searchId = rootEl.dataset.searchId || '';
        this.extraFilters = rootEl.dataset.extraFilters ? JSON.parse(rootEl.dataset.extraFilters) : {};

        this.currentPage = 1;
        this.perPage = parseInt(localStorage.getItem(`per_page_${this.listType}`)) || 20;
        if (![10, 20, 50].includes(this.perPage)) this.perPage = 20;

        this.searchTimeout = null;
        this.currentSearch = '';

        this.init();
    }

    init() {
        this.setupSearch();
        this.setupPerPage();
        this.loadFromUrl();
        this.loadData();
    }

    loadFromUrl() {
        const params = new URLSearchParams(window.location.search);
        if (params.get('search')) {
            this.currentSearch = params.get('search');
            const searchInput = document.getElementById(this.searchId);
            if (searchInput) searchInput.value = this.currentSearch;
        }
        if (params.get('page')) this.currentPage = parseInt(params.get('page'));
        if (params.get('per_page')) {
            this.perPage = parseInt(params.get('per_page'));
            if (![10, 20, 50].includes(this.perPage)) this.perPage = 20;
        }
        for (const [key, selector] of Object.entries(this.extraFilters)) {
            const val = params.get(key);
            if (val) {
                const el = document.querySelector(selector);
                if (el) el.value = val;
            }
        }
    }

    setupSearch() {
        const searchInput = document.getElementById(this.searchId);
        if (!searchInput) return;
        searchInput.addEventListener('input', () => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.currentSearch = searchInput.value.trim();
                this.currentPage = 1;
                this.loadData();
            }, 300);
        });
        searchInput.closest('form')?.addEventListener('submit', (e) => e.preventDefault());
    }

    setupPerPage() {
        const select = document.querySelector('.per-page-select');
        if (!select) return;
        select.value = this.perPage;
        select.addEventListener('change', () => {
            this.perPage = parseInt(select.value);
            localStorage.setItem(`per_page_${this.listType}`, this.perPage);
            this.currentPage = 1;
            this.loadData();
        });
    }

    getExtraFilterParams() {
        const params = {};
        for (const [key, selector] of Object.entries(this.extraFilters)) {
            const el = document.querySelector(selector);
            if (el && el.value) params[key] = el.value;
        }
        return params;
    }

    buildQueryString() {
        const params = new URLSearchParams();
        params.set('page', this.currentPage);
        params.set('per_page', this.perPage);
        if (this.currentSearch) params.set('search', this.currentSearch);
        for (const [k, v] of Object.entries(this.getExtraFilterParams())) {
            params.set(k, v);
        }
        return params.toString();
    }

    updateUrl() {
        const qs = this.buildQueryString();
        const newUrl = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
        history.replaceState(null, '', newUrl);
    }

    async loadData() {
        this.showLoading();
        try {
            const qs = this.buildQueryString();
            const resp = await fetch(`${this.apiUrl}?${qs}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();
            this.render(data.items, data.pagination);
            this.updateUrl();
        } catch (err) {
            console.error('ListPagination error:', err);
            this.showError();
        }
    }

    showLoading() {
        const desktop = this.root.querySelector('.list-desktop');
        const mobile = this.root.querySelector('.list-mobile');
        if (desktop) desktop.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-2 text-muted">Carregando...</p></div>';
        if (mobile) mobile.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-2 text-muted">Carregando...</p></div>';
    }

    showError() {
        const desktop = this.root.querySelector('.list-desktop');
        const mobile = this.root.querySelector('.list-mobile');
        const html = '<div class="text-center py-4"><i class="bi bi-exclamation-triangle display-1 text-danger"></i><h5 class="text-muted mt-3">Erro ao carregar dados</h5></div>';
        if (desktop) desktop.innerHTML = html;
        if (mobile) mobile.innerHTML = html;
    }

    render(items, pagination) {
        this.renderDesktop(items);
        this.renderMobile(items);
        this.renderPagination(pagination);
        this.renderEmptyState(items, pagination);
    }

    renderDesktop(items) {
        const container = this.root.querySelector('.list-desktop');
        if (!container) return;
        if (items.length === 0) {
            container.innerHTML = '';
            return;
        }
        const renderer = this[`renderDesktop_${this.listType}`];
        if (renderer) container.innerHTML = renderer.call(this, items);
    }

    renderMobile(items) {
        const container = this.root.querySelector('.list-mobile');
        if (!container) return;
        if (items.length === 0) {
            container.innerHTML = '';
            return;
        }
        const renderer = this[`renderMobile_${this.listType}`];
        if (renderer) container.innerHTML = renderer.call(this, items);
    }

    renderEmptyState(items, pagination) {
        const emptyEl = this.root.querySelector('.list-empty-state');
        if (!emptyEl) return;
        if (items.length === 0 && pagination.total_items === 0) {
            emptyEl.style.display = '';
        } else {
            emptyEl.style.display = 'none';
        }
    }

    renderPagination(p) {
        const container = document.getElementById('paginationList');
        const pageInfo = document.getElementById('pageInfo');
        const pageInfoMobile = document.getElementById('pageInfoMobile');
        const header = document.getElementById('paginationHeader');

        if (!container) return;

        if (p.total_pages <= 1) {
            if (header) header.classList.add('d-none');
            return;
        }
        if (header) header.classList.remove('d-none');

        const info = `Página ${p.current_page} de ${p.total_pages}`;
        if (pageInfo) pageInfo.textContent = info;
        if (pageInfoMobile) pageInfoMobile.textContent = info;

        let html = '';
        html += `<li class="page-item ${p.has_previous ? '' : 'disabled'}"><a class="page-link" href="#" data-page="1"><i class="bi bi-chevron-double-left"></i></a></li>`;
        html += `<li class="page-item ${p.has_previous ? '' : 'disabled'}"><a class="page-link" href="#" data-page="${p.previous_page || 1}"><i class="bi bi-chevron-left"></i></a></li>`;

        let startPage = Math.max(1, p.current_page - 2);
        let endPage = Math.min(p.total_pages, p.current_page + 2);
        if (startPage > 1) html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="page-item ${i === p.current_page ? 'active' : ''}"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
        }
        if (endPage < p.total_pages) html += '<li class="page-item disabled"><span class="page-link">...</span></li>';

        html += `<li class="page-item ${p.has_next ? '' : 'disabled'}"><a class="page-link" href="#" data-page="${p.next_page || p.total_pages}"><i class="bi bi-chevron-right"></i></a></li>`;
        html += `<li class="page-item ${p.has_next ? '' : 'disabled'}"><a class="page-link" href="#" data-page="${p.total_pages}"><i class="bi bi-chevron-double-right"></i></a></li>`;

        container.innerHTML = html;
        container.querySelectorAll('a.page-link').forEach(a => {
            a.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(a.dataset.page);
                if (page && page !== p.current_page) {
                    this.currentPage = page;
                    this.loadData();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });
        });
    }

    // =========================================================================
    // Renderers específicos por tipo de lista
    // =========================================================================

    renderDesktop_category(items) {
        let html = '<table class="table table-bordered" width="100%" cellspacing="0"><thead><tr><th>Nome</th><th>Comprovante Obrigatório</th><th>Data de Criação</th><th>Última Atualização</th><th>Status</th><th class="text-nowrap">Ações</th></tr></thead><tbody>';
        items.forEach(c => {
            html += `<tr>
                <td>${c.name}</td>
                <td>${c.mandatory_proof ? '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Sim</span>' : '<span class="badge bg-secondary"><i class="bi bi-file-earmark-x"></i> Não</span>'}</td>
                <td>${c.created_at}</td>
                <td>${c.updated_at}</td>
                <td>${c.is_active ? '<span class="badge bg-success">Ativo</span>' : '<span class="badge bg-danger">Inativo</span>'}</td>
                <td class="text-nowrap">
                    <a href="/categories/${c.id}/edit/" class="btn btn-sm btn-outline-primary" title="Editar"><i class="bi bi-pencil"></i></a>
                    ${c.is_active
                        ? `<button type="button" class="btn btn-sm btn-outline-warning btn-toggle-item" data-id="${c.id}" data-name="${c.name}" data-created="${c.created_at}" data-updated="${c.updated_at}" data-type="category" data-active="true" title="Inativar"><i class="bi bi-file-earmark-x"></i></button>`
                        : `<button type="button" class="btn btn-sm btn-outline-success btn-toggle-item" data-id="${c.id}" data-name="${c.name}" data-created="${c.created_at}" data-updated="${c.updated_at}" data-type="category" data-active="false" title="Ativar"><i class="bi bi-file-earmark"></i></button>`
                    }
                </td></tr>`;
        });
        html += '</tbody></table>';
        return html;
    }

    renderMobile_category(items) {
        let html = '<div class="mobile-cards-container">';
        items.forEach(c => {
            html += `<div class="mobile-card">
                <div class="mobile-card-header">
                    <div class="mobile-card-row"><span class="mobile-card-label">Nome:</span><span class="mobile-card-value">${c.name}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Comprovante:</span><span class="mobile-card-value">${c.mandatory_proof ? '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Sim</span>' : '<span class="badge bg-secondary"><i class="bi bi-file-earmark-x"></i> Não</span>'}</span></div>
                </div>
                <div class="mobile-card-body">
                    <div class="mobile-card-row"><span class="mobile-card-label">Criado em:</span><span class="mobile-card-value">${c.created_at}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Atualizado em:</span><span class="mobile-card-value">${c.updated_at}</span></div>
                </div>
                <div class="mobile-card-footer">
                    <a href="/categories/${c.id}/edit/" class="mobile-card-btn btn-outline-primary" title="Editar"><i class="bi bi-pencil"></i> Editar</a>
                    ${c.is_active
                        ? `<button type="button" class="mobile-card-btn btn-outline-warning btn-toggle-item" data-id="${c.id}" data-name="${c.name}" data-created="${c.created_at}" data-updated="${c.updated_at}" data-type="category" data-active="true" title="Inativar"><i class="bi bi-file-earmark-x"></i> Inativar</button>`
                        : `<button type="button" class="mobile-card-btn btn-outline-success btn-toggle-item" data-id="${c.id}" data-name="${c.name}" data-created="${c.created_at}" data-updated="${c.updated_at}" data-type="category" data-active="false" title="Ativar"><i class="bi bi-file-earmark"></i> Ativar</button>`
                    }
                </div></div>`;
        });
        html += '</div>';
        return html;
    }

    renderDesktop_field(items) {
        let html = '<table class="table table-bordered" width="100%" cellspacing="0"><thead><tr><th>Nome</th><th>Igrejas</th><th>Data de Criação</th><th>Última Atualização</th><th>Status</th><th class="text-nowrap">Ações</th></tr></thead><tbody>';
        items.forEach(f => {
            html += `<tr>
                <td>${f.name}</td>
                <td><span class="badge ${f.church_count === 0 ? 'bg-secondary' : 'bg-primary'}">${f.church_count}</span></td>
                <td>${f.created_at}</td>
                <td>${f.updated_at}</td>
                <td>${f.is_active ? '<span class="badge bg-success">Ativo</span>' : '<span class="badge bg-danger">Inativo</span>'}</td>
                <td class="text-nowrap">
                    <a href="/fields/${f.id}/edit/" class="btn btn-sm btn-outline-primary" title="Editar"><i class="bi bi-pencil"></i></a>
                    ${f.is_active
                        ? `<button type="button" class="btn btn-sm btn-outline-warning btn-toggle-item" data-id="${f.id}" data-name="${f.name}" data-created="${f.created_at}" data-updated="${f.updated_at}" data-type="field" data-active="true" title="Inativar"><i class="bi bi-file-earmark-x"></i></button>`
                        : `<button type="button" class="btn btn-sm btn-outline-success btn-toggle-item" data-id="${f.id}" data-name="${f.name}" data-created="${f.created_at}" data-updated="${f.updated_at}" data-type="field" data-active="false" title="Ativar"><i class="bi bi-file-earmark"></i></button>`
                    }
                </td></tr>`;
        });
        html += '</tbody></table>';
        return html;
    }

    renderMobile_field(items) {
        let html = '<div class="mobile-cards-container">';
        items.forEach(f => {
            html += `<div class="mobile-card">
                <div class="mobile-card-header">
                    <div class="mobile-card-row"><span class="mobile-card-label">Nome:</span><span class="mobile-card-value">${f.name}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Igrejas:</span><span class="mobile-card-badge ${f.church_count === 0 ? 'secondary' : 'primary'}">${f.church_count}</span></div>
                </div>
                <div class="mobile-card-body">
                    <div class="mobile-card-row"><span class="mobile-card-label">Criado em:</span><span class="mobile-card-value">${f.created_at}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Atualizado em:</span><span class="mobile-card-value">${f.updated_at}</span></div>
                </div>
                <div class="mobile-card-footer">
                    <a href="/fields/${f.id}/edit/" class="mobile-card-btn btn-outline-primary" title="Editar"><i class="bi bi-pencil"></i> Editar</a>
                    ${f.is_active
                        ? `<button type="button" class="mobile-card-btn btn-outline-warning btn-toggle-item" data-id="${f.id}" data-name="${f.name}" data-created="${f.created_at}" data-updated="${f.updated_at}" data-type="field" data-active="true" title="Inativar"><i class="bi bi-file-earmark-x"></i> Inativar</button>`
                        : `<button type="button" class="mobile-card-btn btn-outline-success btn-toggle-item" data-id="${f.id}" data-name="${f.name}" data-created="${f.created_at}" data-updated="${f.updated_at}" data-type="field" data-active="false" title="Ativar"><i class="bi bi-file-earmark"></i> Ativar</button>`
                    }
                </div></div>`;
        });
        html += '</div>';
        return html;
    }

    renderDesktop_shepherd(items) {
        let html = '<table class="table table-bordered" width="100%" cellspacing="0"><thead><tr><th>Nome</th><th>Igrejas</th><th>Data de Entrada</th><th>Data de Saída</th><th>Status</th><th class="text-nowrap">Ações</th></tr></thead><tbody>';
        items.forEach(s => {
            html += `<tr>
                <td>${s.name}</td>
                <td><span class="badge bg-primary">${s.church_count}</span></td>
                <td>${s.first_start_date || '—'}</td>
                <td>${s.last_end_date || 'Atual'}</td>
                <td>${s.is_active ? '<span class="badge bg-success">Ativo</span>' : '<span class="badge bg-danger">Inativo</span>'}</td>
                <td class="text-nowrap">
                    ${s.has_contract ? `<button type="button" class="btn btn-sm btn-outline-info btn-contract-item" data-id="${s.id}" data-name="${s.name}" title="Visualizar Contrato"><i class="bi bi-file-earmark-pdf"></i></button>` : ''}
                    <a href="/shepherds/${s.id}/history/" class="btn btn-sm btn-outline-info" title="Histórico"><i class="bi bi-clock-history"></i></a>
                    <a href="/shepherds/${s.id}/edit/" class="btn btn-sm btn-outline-primary" title="Editar"><i class="bi bi-pencil"></i></a>
                    ${s.is_active
                        ? `<button type="button" class="btn btn-sm btn-outline-warning btn-toggle-item" data-id="${s.id}" data-name="${s.name}" data-created="" data-updated="" data-type="shepherd" data-active="true" title="Inativar"><i class="bi bi-file-earmark-x"></i></button>`
                        : `<button type="button" class="btn btn-sm btn-outline-success btn-toggle-item" data-id="${s.id}" data-name="${s.name}" data-created="" data-updated="" data-type="shepherd" data-active="false" title="Ativar"><i class="bi bi-file-earmark"></i></button>`
                    }
                </td></tr>`;
        });
        html += '</tbody></table>';
        return html;
    }

    renderMobile_shepherd(items) {
        let html = '<div class="mobile-cards-container">';
        items.forEach(s => {
            html += `<div class="mobile-card">
                <div class="mobile-card-header">
                    <div class="mobile-card-row"><span class="mobile-card-label">Nome:</span><span class="mobile-card-value">${s.name}</span></div>
                </div>
                <div class="mobile-card-body">
                    <div class="mobile-card-row"><span class="mobile-card-label">Igrejas:</span><span class="mobile-card-badge primary">${s.church_count}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Entrada:</span><span class="mobile-card-value">${s.first_start_date || '—'}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Saída:</span><span class="mobile-card-value">${s.last_end_date || 'Atual'}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Status:</span>${s.is_active ? '<span class="badge bg-success">Ativo</span>' : '<span class="badge bg-danger">Inativo</span>'}</div>
                </div>
                <div class="mobile-card-footer">
                    ${s.has_contract ? `<button type="button" class="mobile-card-btn btn-outline-info btn-contract-item" data-id="${s.id}" data-name="${s.name}" title="Contrato"><i class="bi bi-file-earmark-pdf"></i> Contrato</button>` : ''}
                    <a href="/shepherds/${s.id}/history/" class="mobile-card-btn btn-outline-info"><i class="bi bi-clock-history"></i> Histórico</a>
                    <a href="/shepherds/${s.id}/edit/" class="mobile-card-btn btn-outline-primary"><i class="bi bi-pencil"></i> Editar</a>
                    ${s.is_active
                        ? `<button type="button" class="mobile-card-btn btn-outline-warning btn-toggle-item" data-id="${s.id}" data-name="${s.name}" data-created="" data-updated="" data-type="shepherd" data-active="true"><i class="bi bi-file-earmark-x"></i> Inativar</button>`
                        : `<button type="button" class="mobile-card-btn btn-outline-success btn-toggle-item" data-id="${s.id}" data-name="${s.name}" data-created="" data-updated="" data-type="shepherd" data-active="false"><i class="bi bi-file-earmark"></i> Ativar</button>`
                    }
                </div></div>`;
        });
        html += '</div>';
        return html;
    }

    renderDesktop_church(items) {
        let html = '<table class="table table-bordered" width="100%" cellspacing="0"><thead><tr><th>Nome</th><th>Pastor Responsável</th><th>Campo</th><th>Endereço</th><th>Status</th><th class="text-nowrap">Ações</th></tr></thead><tbody>';
        items.forEach(c => {
            html += `<tr>
                <td>${c.name}</td>
                <td>${c.shepherd_name || '-'}</td>
                <td><span class="badge bg-secondary"><i class="bi bi-geo-alt"></i> ${c.field_name || '-'}</span></td>
                <td>${c.address || '-'}</td>
                <td>${c.is_active ? '<span class="badge bg-success">Ativo</span>' : '<span class="badge bg-danger">Inativo</span>'}</td>
                <td class="text-nowrap">
                    <a href="/churches/${c.id}/shepherd-history/" class="btn btn-sm btn-outline-info" title="Histórico de Pastores"><i class="bi bi-clock-history"></i></a>
                    <a href="/churches/${c.id}/edit/" class="btn btn-sm btn-outline-primary" title="Editar"><i class="bi bi-pencil"></i></a>
                    ${c.is_active
                        ? `<button type="button" class="btn btn-sm btn-outline-warning btn-toggle-item" data-id="${c.id}" data-name="${c.name}" data-shepherd="${c.shepherd_name || ''}" data-field="${c.field_name || ''}" data-address="${c.address || 'Não informado'}" data-type="church" data-active="true" title="Inativar"><i class="bi bi-file-earmark-x"></i></button>`
                        : `<button type="button" class="btn btn-sm btn-outline-success btn-toggle-item" data-id="${c.id}" data-name="${c.name}" data-shepherd="${c.shepherd_name || ''}" data-field="${c.field_name || ''}" data-address="${c.address || 'Não informado'}" data-type="church" data-active="false" title="Ativar"><i class="bi bi-file-earmark"></i></button>`
                    }
                </td></tr>`;
        });
        html += '</tbody></table>';
        return html;
    }

    renderMobile_church(items) {
        let html = '<div class="mobile-cards-container">';
        items.forEach(c => {
            html += `<div class="mobile-card">
                <div class="mobile-card-header">
                    <div class="mobile-card-row"><span class="mobile-card-label">Nome:</span><span class="mobile-card-value">${c.name}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Pastor:</span><span class="mobile-card-value">${c.shepherd_name || '-'}</span></div>
                </div>
                <div class="mobile-card-body">
                    <div class="mobile-card-row"><span class="mobile-card-label">Campo:</span><span class="mobile-card-badge secondary"><i class="bi bi-geo-alt"></i> ${c.field_name || '-'}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Endereço:</span><span class="mobile-card-value">${c.address || '-'}</span></div>
                </div>
                <div class="mobile-card-footer">
                    <a href="/churches/${c.id}/shepherd-history/" class="mobile-card-btn btn-outline-info"><i class="bi bi-clock-history"></i> Histórico</a>
                    <a href="/churches/${c.id}/edit/" class="mobile-card-btn btn-outline-primary"><i class="bi bi-pencil"></i> Editar</a>
                    ${c.is_active
                        ? `<button type="button" class="mobile-card-btn btn-outline-warning btn-toggle-item" data-id="${c.id}" data-name="${c.name}" data-shepherd="${c.shepherd_name || ''}" data-field="${c.field_name || ''}" data-address="${c.address || 'Não informado'}" data-type="church" data-active="true"><i class="bi bi-file-earmark-x"></i> Inativar</button>`
                        : `<button type="button" class="mobile-card-btn btn-outline-success btn-toggle-item" data-id="${c.id}" data-name="${c.name}" data-shepherd="${c.shepherd_name || ''}" data-field="${c.field_name || ''}" data-address="${c.address || 'Não informado'}" data-type="church" data-active="false"><i class="bi bi-file-earmark"></i> Ativar</button>`
                    }
                </div></div>`;
        });
        html += '</div>';
        return html;
    }

    renderDesktop_user(items) {
        let html = '<table class="table table-bordered" width="100%" cellspacing="0"><thead><tr><th>Nome</th><th>Email</th><th>Função</th><th>Campos</th><th>Status</th><th class="text-nowrap">Ações</th></tr></thead><tbody>';
        items.forEach(u => {
            const roleBadge = u.role === 'admin' ? 'bg-info' : u.role === 'supervisor' ? 'bg-warning' : 'bg-primary';
            const fieldsHtml = u.fields.length > 0
                ? u.fields.map(f => `<span class="badge bg-secondary me-1 mb-1"><i class="bi bi-geo-alt"></i> ${f.name}</span>`).join('')
                : '<span class="text-muted">-</span>';
            const canEdit = u.can_manage || u.is_self;
            const canToggle = u.can_toggle_active;
            html += `<tr>
                <td>${u.full_name}</td>
                <td>${u.email}</td>
                <td><span class="badge ${roleBadge}">${u.role_display}</span></td>
                <td><div class="user-fields">${fieldsHtml}</div></td>
                <td><span class="badge bg-${u.is_active ? 'success' : 'danger'}">${u.is_active ? 'Ativo' : 'Inativo'}</span></td>
                <td class="text-nowrap">
                    ${canEdit
                        ? `<a href="/users/${u.id}/edit/" class="btn btn-sm btn-outline-primary" title="Editar"><i class="bi bi-pencil"></i></a>`
                        : `<a class="btn btn-sm btn-outline-primary disabled" style="cursor:not-allowed;" tabindex="-1" title="Editar"><i class="bi bi-pencil"></i></a>`
                    }
                    ${u.is_active
                        ? `<button type="button" class="btn btn-sm btn-outline-warning btn-toggle-user ${!canToggle ? 'disabled' : ''}" ${!canToggle ? 'disabled style="cursor:not-allowed;"' : ''} data-id="${u.id}" data-name="${u.full_name}" data-email="${u.email}" data-role="${u.role_display}" data-fields="${u.fields.map(f => f.name).join(', ')}" data-status="Ativo" data-action="deactivate" title="Inativar"><i class="bi bi-file-earmark-x"></i></button>`
                        : `<button type="button" class="btn btn-sm btn-outline-success btn-toggle-user ${!canToggle ? 'disabled' : ''}" ${!canToggle ? 'disabled style="cursor:not-allowed;"' : ''} data-id="${u.id}" data-name="${u.full_name}" data-email="${u.email}" data-role="${u.role_display}" data-fields="${u.fields.map(f => f.name).join(', ')}" data-status="Inativo" data-action="activate" title="Ativar"><i class="bi bi-file-earmark"></i></button>`
                    }
                </td></tr>`;
        });
        html += '</tbody></table>';
        return html;
    }

    renderMobile_user(items) {
        let html = '<div class="mobile-cards-container">';
        items.forEach(u => {
            const roleBadge = u.role === 'admin' ? 'info' : u.role === 'supervisor' ? 'warning' : 'primary';
            const fieldsHtml = u.fields.length > 0
                ? u.fields.map(f => `<span class="mobile-card-badge secondary"><i class="bi bi-geo-alt"></i> ${f.name}</span>`).join('')
                : '<span class="mobile-card-value text-muted">-</span>';
            const canEdit = u.can_manage || u.is_self;
            const canToggle = u.can_toggle_active;
            html += `<div class="mobile-card">
                <div class="mobile-card-header">
                    <div class="mobile-card-row"><span class="mobile-card-label">Nome:</span><span class="mobile-card-value">${u.full_name}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Email:</span><span class="mobile-card-value">${u.email}</span></div>
                </div>
                <div class="mobile-card-body">
                    <div class="mobile-card-row"><span class="mobile-card-label">Função:</span><span class="mobile-card-badge ${roleBadge}">${u.role_display}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Campos:</span><div class="mobile-card-fields">${fieldsHtml}</div></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Status:</span><span class="mobile-card-badge ${u.is_active ? 'success' : 'danger'}">${u.is_active ? 'Ativo' : 'Inativo'}</span></div>
                </div>
                <div class="mobile-card-footer">
                    ${canEdit
                        ? `<a href="/users/${u.id}/edit/" class="mobile-card-btn btn-outline-primary"><i class="bi bi-pencil"></i> Editar</a>`
                        : `<a class="mobile-card-btn btn-outline-primary disabled" style="cursor:not-allowed;" tabindex="-1"><i class="bi bi-pencil"></i> Editar</a>`
                    }
                    ${u.is_active
                        ? `<button type="button" class="mobile-card-btn btn-outline-warning btn-toggle-user ${!canToggle ? 'disabled' : ''}" ${!canToggle ? 'disabled style="cursor:not-allowed;"' : ''} data-id="${u.id}" data-name="${u.full_name}" data-email="${u.email}" data-role="${u.role_display}" data-fields="${u.fields.map(f => f.name).join(', ')}" data-status="Ativo" data-action="deactivate"><i class="bi bi-file-earmark-x"></i> Inativar</button>`
                        : `<button type="button" class="mobile-card-btn btn-outline-success btn-toggle-user ${!canToggle ? 'disabled' : ''}" ${!canToggle ? 'disabled style="cursor:not-allowed;"' : ''} data-id="${u.id}" data-name="${u.full_name}" data-email="${u.email}" data-role="${u.role_display}" data-fields="${u.fields.map(f => f.name).join(', ')}" data-status="Inativo" data-action="activate"><i class="bi bi-file-earmark"></i> Ativar</button>`
                    }
                </div></div>`;
        });
        html += '</div>';
        return html;
    }

    renderDesktop_notification(items) {
        let html = '<table class="table table-bordered" width="100%" cellspacing="0"><thead><tr><th>Título</th><th>Mensagem</th><th>Data e Hora</th><th>Status</th><th>Repetir</th><th>Criado por</th><th>Data de Criação</th><th class="text-nowrap">Ações</th></tr></thead><tbody>';
        items.forEach(n => {
            html += `<tr>
                <td>${n.title}</td>
                <td><div class="text-truncate" style="max-width:200px;" title="${n.body}">${n.body}</div></td>
                <td>${n.date}</td>
                <td>${n.is_read ? '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Lida</span>' : '<span class="badge bg-warning"><i class="bi bi-exclamation-circle"></i> Não lida</span>'}</td>
                <td>${n.repeat ? `<span class="badge bg-info"><i class="bi bi-arrow-repeat"></i> ${n.repeat_frequency_display}</span>` : '<span class="text-muted">-</span>'}</td>
                <td>${n.created_by_name || '-'}</td>
                <td>${n.created_at}</td>
                <td class="text-nowrap">
                    <button type="button" class="btn btn-sm btn-outline-info btn-view-notification" data-id="${n.id}" data-title="${n.title}" data-body="${n.body}" data-date="${n.date}" data-status="${n.is_read ? 'Lida' : 'Não lida'}" data-repeat="${n.repeat ? n.repeat_frequency_display : 'Não'}" data-created-by="${n.created_by_name || ''}" data-created-at="${n.created_at}" title="Visualizar"><i class="bi bi-eye"></i></button>
                    <a href="/notifications/${n.id}/edit/" class="btn btn-sm btn-outline-primary" title="Editar"><i class="bi bi-pencil"></i></a>
                    <button type="button" class="btn btn-sm btn-outline-danger btn-delete-notification" data-id="${n.id}" data-title="${n.title}" data-date="${n.date}" data-body="${n.body}" title="Excluir"><i class="bi bi-trash"></i></button>
                </td></tr>`;
        });
        html += '</tbody></table>';
        return html;
    }

    renderMobile_notification(items) {
        let html = '<div class="mobile-cards-container">';
        items.forEach(n => {
            html += `<div class="mobile-card">
                <div class="mobile-card-header">
                    <div class="mobile-card-row"><span class="mobile-card-label">Título:</span><span class="mobile-card-value">${n.title}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Mensagem:</span><span class="mobile-card-value">${n.body}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Data:</span><span class="mobile-card-value">${n.date}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Status:</span><span class="mobile-card-value">${n.is_read ? '<span class="badge bg-success">Lida</span>' : '<span class="badge bg-warning">Não lida</span>'}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Repetir:</span><span class="mobile-card-value">${n.repeat ? `<span class="badge bg-info"><i class="bi bi-arrow-repeat"></i> ${n.repeat_frequency_display}</span>` : '<span class="text-muted">-</span>'}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Criado por:</span><span class="mobile-card-value">${n.created_by_name || '-'}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Criação:</span><span class="mobile-card-value">${n.created_at}</span></div>
                </div>
                <div class="mobile-card-footer">
                    <button type="button" class="mobile-card-btn btn-outline-info btn-view-notification" data-id="${n.id}" data-title="${n.title}" data-body="${n.body}" data-date="${n.date}" data-status="${n.is_read ? 'Lida' : 'Não lida'}" data-repeat="${n.repeat ? n.repeat_frequency_display : 'Não'}" data-created-by="${n.created_by_name || ''}" data-created-at="${n.created_at}"><i class="bi bi-eye"></i> Visualizar</button>
                    <a href="/notifications/${n.id}/edit/" class="mobile-card-btn btn-outline-primary"><i class="bi bi-pencil"></i> Editar</a>
                    <button type="button" class="mobile-card-btn btn-outline-danger btn-delete-notification" data-id="${n.id}" data-title="${n.title}" data-date="${n.date}" data-body="${n.body}"><i class="bi bi-trash"></i> Excluir</button>
                </div></div>`;
        });
        html += '</div>';
        return html;
    }

    renderDesktop_access_log(items) {
        let html = '<table class="table table-bordered" width="100%" cellspacing="0"><thead><tr><th>Data e Hora</th><th>Usuário</th><th>Descrição</th><th>Ação</th></tr></thead><tbody>';
        items.forEach(log => {
            const actionColors = { login: 'success', logout: 'warning', create: 'primary', update: 'info', delete: 'danger' };
            const actionIcons = { login: 'box-arrow-in-right', logout: 'box-arrow-left', create: 'plus-circle', update: 'pencil', delete: 'trash' };
            html += `<tr>
                <td>${log.created_at}</td>
                <td>${log.user_name}</td>
                <td>${log.description}</td>
                <td><span class="badge bg-${actionColors[log.action] || 'secondary'}"><i class="bi bi-${actionIcons[log.action] || 'question-circle'}"></i> ${log.action_display}</span></td>
            </tr>`;
        });
        html += '</tbody></table>';
        return html;
    }

    renderMobile_access_log(items) {
        let html = '<div class="mobile-cards-container">';
        items.forEach(log => {
            const actionColors = { login: 'success', logout: 'warning', create: 'primary', update: 'info', delete: 'danger' };
            const actionIcons = { login: 'box-arrow-in-right', logout: 'box-arrow-left', create: 'plus-circle', update: 'pencil', delete: 'trash' };
            html += `<div class="mobile-card">
                <div class="mobile-card-header">
                    <div class="mobile-card-row"><span class="mobile-card-label">Data:</span><span class="mobile-card-value">${log.created_at}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Usuário:</span><span class="mobile-card-value">${log.user_name}</span></div>
                </div>
                <div class="mobile-card-body">
                    <div class="mobile-card-row"><span class="mobile-card-label">Descrição:</span><span class="mobile-card-value">${log.description}</span></div>
                    <div class="mobile-card-row"><span class="mobile-card-label">Ação:</span><span class="mobile-card-badge ${actionColors[log.action] || 'secondary'}"><i class="bi bi-${actionIcons[log.action] || 'question-circle'}"></i> ${log.action_display}</span></div>
                </div></div>`;
        });
        html += '</div>';
        return html;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const root = document.getElementById('listPagination');
    if (root) {
        window.listPagination = new ListPagination(root);
    }
});
