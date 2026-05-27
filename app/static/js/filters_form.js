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
            console.error('Erro ao ler filtersSourceJson:', error);
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
    }

    applySelections() {
        this.syncAllHiddenInputs();
        this.form.dispatchEvent(new CustomEvent('filters:applied', { bubbles: true }));
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

    setupMobileSync() {
        this.syncDateFields();
        this.syncNonSelect2Fields();
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
        console.log('Filtros inicializados com modal');
    }
});

// Exportar para uso global
window.FiltersForm = FiltersForm;
