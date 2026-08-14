/**
 * Script para gerenciar filtros com modal e seleção múltipla
 * Usado no Dashboard e na Lista de Transações
 */

class FiltersForm {
    constructor() {
        this.form = document.getElementById('chartFilterForm');
        this.hiddenContainer = document.getElementById('advancedFiltersHidden');
        this.sourceContainer = document.getElementById('filtersSourceData');

        this.modal = document.getElementById('filtersModal');
        this.typeSelect = document.getElementById('filtersModalType');
        this.searchInput = document.getElementById('filtersModalSearch');
        this.tableBody = document.getElementById('filtersModalTableBody');
        this.clearButton = document.getElementById('filtersModalClear');
        this.applyButton = document.getElementById('filtersModalApply');

        if (!this.form || !this.modal || !this.typeSelect || !this.tableBody) {
            return;
        }

        this.sourceData = this.readSourceData();
        this.selected = this.readSelections();
        this.bindEvents();
        this.setupMobileSync();
        this.renderTable();
    }

    getAvailableKeys() {
        return Array.from(this.typeSelect.options).map(option => option.value);
    }

    readSelections() {
        const selections = {};
        const keys = this.getAvailableKeys();
        keys.forEach(key => {
            const inputs = document.querySelectorAll(`input[name="${key}"]`);
            selections[key] = new Set(
                Array.from(inputs)
                    .map(input => String(input.value))
                    .filter(value => value)
            );
        });
        return selections;
    }

    syncHiddenInputs(key) {
        if (!this.hiddenContainer) return;

        const existing = this.hiddenContainer.querySelectorAll(`input[name="${key}"]`);
        existing.forEach(input => input.remove());

        const values = Array.from(this.selected[key] || []);
        values.forEach(value => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = value;
            input.setAttribute('data-filter', key);
            this.hiddenContainer.appendChild(input);
        });
    }

    syncAllHiddenInputs() {
        const keys = this.getAvailableKeys();
        keys.forEach(key => this.syncHiddenInputs(key));
    }

    readSourceData() {
        const jsonNode = document.getElementById('filtersSourceJson');
        if (!jsonNode) return {};

        try {
            return JSON.parse(jsonNode.textContent || '{}') || {};
        } catch (error) {
            return {};
        }
    }

    getSourceOptions(key) {
        const jsonOptions = Array.isArray(this.sourceData?.[key]) ? this.sourceData[key] : [];
        if (jsonOptions.length > 0) {
            return jsonOptions.map(item => ({
                id: String(item.id),
                text: item.text
            }));
        }

        let source = null;

        if (this.sourceContainer) {
            source = this.sourceContainer.querySelector(`[data-filter-source="${key}"]`);
        }

        if (!source) {
            source = document.getElementById(`${key}FilterSource`);
        }

        if (!source) return [];

        return Array.from(source.options).map(option => ({
            id: String(option.value),
            text: option.textContent
        }));
    }

    renderTable() {
        if (!this.tableBody) return;

        const currentKey = this.typeSelect.value;
        const options = this.getSourceOptions(currentKey);
        const selectedSet = this.selected[currentKey] || new Set();

        this.tableBody.innerHTML = '';

        if (!options.length) {
            this.tableBody.innerHTML = '<tr><td colspan="2" class="text-muted">Nenhum item disponível.</td></tr>';
            return;
        }

        options.forEach(option => {
            const row = document.createElement('tr');
            const isChecked = selectedSet.has(option.id);

            row.innerHTML = `
                <td>
                    <input type="checkbox" class="form-check-input filters-modal-checkbox" data-filter-key="${currentKey}" value="${option.id}" ${isChecked ? 'checked' : ''}>
                </td>
                <td>${option.text}</td>
            `;

            this.tableBody.appendChild(row);
        });

        this.applySearchFilter();
    }

    applySearchFilter() {
        if (!this.searchInput) return;

        const query = this.searchInput.value.trim().toLowerCase();
        const rows = Array.from(this.tableBody.querySelectorAll('tr'));

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
        });
    }

    clearSelections() {
        const keys = this.getAvailableKeys();
        keys.forEach(key => {
            this.selected[key] = new Set();
        });
        this.syncAllHiddenInputs();
        this.renderTable();
        this.form.dispatchEvent(new CustomEvent('filters:applied', { bubbles: true }));
        const modalInstance = bootstrap.Modal.getInstance(this.modal);
        if (modalInstance) modalInstance.hide();
    }

    applySelections() {
        this.syncAllHiddenInputs();
        if (typeof window.loadTransactions === 'function') {
            this.form.dispatchEvent(new CustomEvent('filters:applied', { bubbles: true }));
        } else {
            this.form.submit();
        }
    }

    bindEvents() {
        if (this.typeSelect) {
            this.typeSelect.addEventListener('change', () => {
                this.searchInput.value = '';
                this.renderTable();
            });
        }

        if (this.searchInput) {
            this.searchInput.addEventListener('input', () => this.applySearchFilter());
        }

        if (this.tableBody) {
            this.tableBody.addEventListener('change', event => {
                const target = event.target;
                if (!target.classList.contains('filters-modal-checkbox')) return;

                const key = target.getAttribute('data-filter-key');
                const value = target.value;

                if (!this.selected[key]) {
                    this.selected[key] = new Set();
                }

                if (target.checked) {
                    this.selected[key].add(value);
                } else {
                    this.selected[key].delete(value);
                }
            });
        }

        if (this.clearButton) {
            this.clearButton.addEventListener('click', () => this.clearSelections());
        }

        if (this.applyButton) {
            this.applyButton.addEventListener('click', () => {
                this.applySelections();
                const modalInstance = bootstrap.Modal.getInstance(this.modal);
                if (modalInstance) modalInstance.hide();
            });
        }

        if (this.modal) {
            this.modal.addEventListener('show.bs.modal', () => {
                this.sourceData = this.readSourceData();
                this.selected = this.readSelections();
                this.searchInput.value = '';
                this.renderTable();
            });
        }

        if (this.form) {
            this.form.addEventListener('submit', () => {
                this.showFormLoading();
            });
        }
    }

    showFormLoading() {
        const submitButtons = this.form.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(button => {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Aplicando...';
            button.disabled = true;

            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 3000);
        });
    }

    getStorageKey() {
        const form = document.getElementById('chartFilterForm');
        const page = (form && form.dataset.filterPage) || 'transaction_list';
        return `filters_${page}`;
    }

    static saveFromUrl() {
        if (!window.location.search) return;
        const form = document.getElementById('chartFilterForm');
        if (!form) return;
        const page = form.dataset.filterPage || 'transaction_list';
        const key = `filters_${page}`;
        const params = new URLSearchParams(window.location.search);
        const state = {};
        for (const [name, value] of params.entries()) {
            if (!state[name]) state[name] = [];
            state[name].push(value);
        }
        localStorage.setItem(key, JSON.stringify(state));
    }

    static restoreFromLocalStorage() {
        const form = document.getElementById('chartFilterForm');
        if (!form) return;
        const page = form.dataset.filterPage || 'transaction_list';
        const key = `filters_${page}`;
        const saved = localStorage.getItem(key);
        if (!saved) return;
        if (window.location.search) return;
        try {
            const state = JSON.parse(saved);
            const params = new URLSearchParams();
            for (const [k, v] of Object.entries(state)) {
                if (Array.isArray(v)) v.forEach(x => { if (x) params.append(k, x); });
                else if (v) params.set(k, v);
            }
            if (params.toString()) window.location.search = params.toString();
        } catch (e) { localStorage.removeItem(key); }
    }

    static clearLocalStorage() {
        const form = document.getElementById('chartFilterForm');
        const page = (form && form.dataset.filterPage) || 'transaction_list';
        localStorage.removeItem(`filters_${page}`);
    }

    setupMobileSync() {
        this.syncDateFields();
        this.syncNonSelect2Fields();
        this.setupMonthFilter();
    }

    setupMonthFilter() {
        const desktopMonth = document.getElementById('month_filter');
        const mobileMonth = document.getElementById('month_filter_mobile');

        if (!desktopMonth && !mobileMonth) return;

        const form = this.form;
        const page = (form && form.dataset.filterPage) || 'transaction_list';
        const storageKey = `selected_month_${page}`;

        function getDateFields() {
            const fromDesktop = document.getElementById('date_from') || document.getElementById('startDateFilter');
            const toDesktop = document.getElementById('date_to') || document.getElementById('endDateFilter');
            const fromMobile = document.getElementById('date_from_mobile') || document.getElementById('startDateFilter_mobile');
            const toMobile = document.getElementById('date_to_mobile') || document.getElementById('endDateFilter_mobile');
            return { fromDesktop, toDesktop, fromMobile, toMobile };
        }

        function setDates(monthValue) {
            if (!monthValue) return;
            const month = Number(monthValue);
            const year = new Date().getFullYear();
            const lastDay = new Date(year, month, 0).getDate();
            const firstDay = `${year}-${String(month).padStart(2, '0')}-01`;
            const lastDayStr = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
            const fields = getDateFields();
            if (fields.fromDesktop) fields.fromDesktop.value = firstDay;
            if (fields.toDesktop) fields.toDesktop.value = lastDayStr;
            if (fields.fromMobile) fields.fromMobile.value = firstDay;
            if (fields.toMobile) fields.toMobile.value = lastDayStr;
        }

        function hasUrlDateFilter() {
            const params = new URLSearchParams(window.location.search);
            return params.has('date_from') || params.has('date_to') ||
                   params.has('start_date') || params.has('end_date');
        }

        function getInitialMonth() {
            // 1) Range inicial completo na URL → mês do range
            const fields = getDateFields();
            const from = fields.fromDesktop?.value || fields.fromMobile?.value;
            const to = fields.toDesktop?.value || fields.toMobile?.value;
            if (from && to) {
                const parts = from.split('-').map(Number);
                if (parts.length === 3) {
                    const [year, month, day] = parts;
                    const lastDay = new Date(year, month, 0).getDate();
                    const toParts = to.split('-').map(Number);
                    if (day === 1 && toParts[0] === year && toParts[1] === month && toParts[2] === lastDay) {
                        return { value: String(month), source: 'range' };
                    }
                }
            }
            // 2) Mês salvo em localStorage
            try {
                const saved = localStorage.getItem(storageKey);
                const num = Number(saved);
                if (saved && num >= 1 && num <= 12) {
                    return { value: String(num), source: 'saved' };
                }
            } catch (e) {}
            // 3) Mês atual
            return { value: String(new Date().getMonth() + 1), source: 'current' };
        }

        function setSelectValues(value) {
            if (desktopMonth) desktopMonth.value = value;
            if (mobileMonth) mobileMonth.value = value;
        }

        function handleMonthChange(el) {
            if (!el.value) return;
            setDates(el.value);
            if (desktopMonth && mobileMonth) {
                if (el === desktopMonth) mobileMonth.value = desktopMonth.value;
                else if (el === mobileMonth) desktopMonth.value = mobileMonth.value;
            }
            try {
                localStorage.setItem(storageKey, el.value);
            } catch (e) {}
            if (form) {
                form.dispatchEvent(new CustomEvent('filters:applied', { bubbles: true, detail: { month: true } }));
            }
        }

        [desktopMonth, mobileMonth].forEach(el => {
            if (!el) return;
            el.addEventListener('change', () => handleMonthChange(el));
        });

        const fields = getDateFields();
        const dateInputs = [fields.fromDesktop, fields.toDesktop, fields.fromMobile, fields.toMobile].filter(Boolean);
        dateInputs.forEach(input => {
            input.addEventListener('change', () => {
                const currentMonth = String(new Date().getMonth() + 1);
                if (desktopMonth) desktopMonth.value = currentMonth;
                if (mobileMonth) mobileMonth.value = currentMonth;
            });
        });

        const { value: initialMonth, source } = getInitialMonth();
        setSelectValues(initialMonth);

        // Aplicar mês salvo na carga (sem filtro de datas na URL)
        if (source === 'saved' && !hasUrlDateFilter() && form) {
            setDates(initialMonth);
            setTimeout(() => {
                form.dispatchEvent(new CustomEvent('filters:applied', { bubbles: true, detail: { month: true } }));
            }, 0);
        }
    }

    syncDateFields() {
        const dateFields = [
            { desktop: 'date_from', mobile: 'date_from_mobile' },
            { desktop: 'date_to', mobile: 'date_to_mobile' },
            { desktop: 'startDateFilter', mobile: 'startDateFilter_mobile' },
            { desktop: 'endDateFilter', mobile: 'endDateFilter_mobile' }
        ];

        dateFields.forEach(({ desktop, mobile }) => {
            const desktopField = document.getElementById(desktop);
            const mobileField = document.getElementById(mobile);

            if (desktopField && mobileField) {
                desktopField.addEventListener('change', () => {
                    mobileField.value = desktopField.value;
                });

                mobileField.addEventListener('change', () => {
                    desktopField.value = mobileField.value;
                });
            }
        });
    }

    syncNonSelect2Fields() {
        const nonSelect2Fields = [
            { desktop: 'typeFilter', mobile: 'typeFilter_mobile' }
        ];

        nonSelect2Fields.forEach(({ desktop, mobile }) => {
            const desktopField = document.getElementById(desktop);
            const mobileField = document.getElementById(mobile);

            if (desktopField && mobileField) {
                desktopField.addEventListener('change', () => {
                    mobileField.value = desktopField.value;
                });

                mobileField.addEventListener('change', () => {
                    desktopField.value = mobileField.value;
                });
            }
        });
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    const hasFilters = document.querySelector('#chartFilterForm');
    if (hasFilters) {
        window.filtersForm = new FiltersForm();
    }
    if (window.location.search) {
        // Página carregou com filtros → salvar estado
        FiltersForm.saveFromUrl();
    } else if (typeof window.loadTransactions === 'undefined') {
        // Página limpa → restaurar apenas se não for AJAX (transaction_list.js cuida do próprio restore)
        FiltersForm.restoreFromLocalStorage();
    }
});

// Salvar filtros antes de navegar para criar/editar
document.addEventListener('click', function(e) {
    const link = e.target.closest('a');
    if (!link || !link.href) return;
    if (link.href.includes('/create/') || link.href.includes('/edit/') || link.href.includes('/delete/')) {
        const form = document.getElementById('chartFilterForm');
        if (form && window.location.search) {
            FiltersForm.saveFromUrl();
        }
    }
});

// Interceptar clicks em links "Limpar" para também limpar localStorage
document.addEventListener('click', function(e) {
    const link = e.target.closest('a[href="?clear"]');
    if (link) {
        e.preventDefault();
        FiltersForm.clearLocalStorage();
        // Limpar meses salvos do seletor de mês
        try {
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith('selected_month_')) localStorage.removeItem(key);
            });
        } catch (err) {}
        const url = new URL(window.location.href);
        url.search = '';
        window.location.href = url.toString();
    }
});

// Exportar para uso global
window.FiltersForm = FiltersForm;
