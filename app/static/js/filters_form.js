/**
 * Script para inicializar e gerenciar os filtros com Select2
 * Usado nos formulários de filtros de transações e dashboard
 */

class FiltersForm {
    constructor() {
        this.select2Instances = new Map();
        this.initializeSelect2();
        this.bindEvents();
        this.setupMobileSync();
    }

    /**
     * Inicializa o Select2 para todos os campos de filtro
     */
    initializeSelect2() {
        // Configuração padrão para Select2 nos filtros
        const select2Config = {
            theme: 'bootstrap-5',
            placeholder: 'Selecione...',
            allowClear: true,
            width: '100%',
            language: 'pt-BR',
            minimumResultsForSearch: 10, // Mostrar busca apenas se houver mais de 10 opções
            dropdownParent: 'body', // Evitar problemas de z-index
            closeOnSelect: true,
            selectionCssClass: 'filters-select2',
            dropdownCssClass: 'filters-dropdown'
        };

        // Inicializar Select2 para categoria
        this.initializeField('categoryFilter', {
            ...select2Config,
            placeholder: 'Todas as categorias'
        });

        // Inicializar Select2 para campo
        this.initializeField('fieldFilter', {
            ...select2Config,
            placeholder: 'Todos os campos'
        });

        // Inicializar Select2 para pastor
        this.initializeField('shepherdFilter', {
            ...select2Config,
            placeholder: 'Todos os pastores'
        });

        // Inicializar Select2 para igreja
        this.initializeField('churchFilter', {
            ...select2Config,
            placeholder: 'Todas as igrejas'
        });



        // Inicializar versões mobile se existirem
        this.initializeMobileFields(select2Config);
    }

    /**
     * Inicializa um campo específico com Select2
     */
    initializeField(fieldId, config) {
        const element = document.getElementById(fieldId);
        if (element) {
            try {
                const select2Instance = $(element).select2(config);
                this.select2Instances.set(fieldId, select2Instance);
                
                // Adicionar classes CSS para estilização
                element.closest('.form-floating').classList.add('filters-select2');
                
                // Marcar como inicializado
                element.setAttribute('data-select2-initialized', 'true');
                
                console.log(`Select2 inicializado para: ${fieldId}`);
            } catch (error) {
                console.error(`Erro ao inicializar Select2 para ${fieldId}:`, error);
            }
        }
    }

    /**
     * Inicializa campos mobile se existirem
     */
    initializeMobileFields(config) {
        const mobileFields = [
            'categoryFilter_mobile',
            'fieldFilter_mobile', 
            'shepherdFilter_mobile',
            'churchFilter_mobile'
        ];

        mobileFields.forEach(fieldId => {
            this.initializeField(fieldId, config);
        });
    }



    /**
     * Vincula eventos aos filtros
     */
    bindEvents() {
        // Evento de mudança para filtros dependentes
        this.bindDependentFilters();
        
        // Evento de limpeza de filtros
        this.bindClearFilters();
        
        // Evento de aplicação de filtros
        this.bindApplyFilters();
        
        // Evento de reset de filtros
        this.bindResetFilters();
        
        // Evento de exportação
        this.bindExportEvents();
    }

    /**
     * Vincula filtros dependentes (campo -> igreja)
     */
    bindDependentFilters() {
        const fieldFilter = document.getElementById('fieldFilter');
        const churchFilter = document.getElementById('churchFilter');
        
        if (fieldFilter && churchFilter) {
            $(fieldFilter).on('select2:select select2:clear', (e) => {
                this.updateChurchesByField(e.target.value);
            });
        }

        // Versão mobile
        const fieldFilterMobile = document.getElementById('fieldFilter_mobile');
        const churchFilterMobile = document.getElementById('churchFilter_mobile');
        
        if (fieldFilterMobile && churchFilterMobile) {
            $(fieldFilterMobile).on('select2:select select2:clear', (e) => {
                this.updateChurchesByField(e.target.value, true);
            });
        }
    }

    /**
     * Atualiza igrejas baseado no campo selecionado
     */
    updateChurchesByField(fieldId, isMobile = false) {
        const churchFilterId = isMobile ? 'churchFilter_mobile' : 'churchFilter';
        const churchFilter = document.getElementById(churchFilterId);
        
        if (!churchFilter) return;

        if (!fieldId) {
            // Se nenhum campo selecionado, carregar todas as igrejas
            this.loadAllChurches(isMobile);
            return;
        }

        // Mostrar loading
        this.showLoading(churchFilterId);

        // Fazer requisição AJAX para buscar igrejas do campo
        fetch(`/api/churches-by-field/${fieldId}/`)
            .then(response => response.json())
            .then(data => {
                this.populateChurchFilter(churchFilterId, data.churches || [], isMobile);
                this.hideLoading(churchFilterId);
            })
            .catch(error => {
                console.error('Erro ao buscar igrejas:', error);
                this.hideLoading(churchFilterId);
                this.showError(churchFilterId, 'Erro ao carregar igrejas');
            });
    }

    /**
     * Carrega todas as igrejas
     */
    loadAllChurches(isMobile = false) {
        const churchFilterId = isMobile ? 'churchFilter_mobile' : 'churchFilter';
        const churchFilter = document.getElementById(churchFilterId);
        
        if (!churchFilter) return;

        // Aqui você pode implementar uma API para buscar todas as igrejas
        // Por enquanto, vamos apenas limpar e adicionar uma opção padrão
        this.populateChurchFilter(churchFilterId, [], isMobile);
    }

    /**
     * Popula o filtro de igreja
     */
    populateChurchFilter(churchFilterId, churches, isMobile = false) {
        const churchFilter = document.getElementById(churchFilterId);
        if (!churchFilter) return;

        // Limpar opções existentes
        $(churchFilter).empty();
        
        // Adicionar opção padrão
        const defaultOption = new Option('Todas as igrejas', '', false, false);
        $(churchFilter).append(defaultOption);

        // Adicionar igrejas
        churches.forEach(church => {
            const option = new Option(church.name, church.id, false, false);
            $(churchFilter).append(option);
        });

        // Atualizar Select2
        $(churchFilter).trigger('change');
    }

    /**
     * Mostra loading no filtro
     */
    showLoading(fieldId) {
        const element = document.getElementById(fieldId);
        if (element) {
            element.closest('.form-floating').classList.add('filters-loading');
        }
    }

    /**
     * Esconde loading do filtro
     */
    hideLoading(fieldId) {
        const element = document.getElementById(fieldId);
        if (element) {
            element.closest('.form-floating').classList.remove('filters-loading');
        }
    }

    /**
     * Mostra erro no filtro
     */
    showError(fieldId, message) {
        const element = document.getElementById(fieldId);
        if (element) {
            // Adicionar mensagem de erro
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback d-block';
            errorDiv.textContent = message;
            
            const container = element.closest('.form-floating');
            const existingError = container.querySelector('.invalid-feedback');
            if (existingError) {
                existingError.remove();
            }
            
            container.appendChild(errorDiv);
            
            // Remover erro após 5 segundos
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.remove();
                }
            }, 5000);
        }
    }

    /**
     * Vincula evento de limpeza de filtros
     */
    bindClearFilters() {
        // Não interceptar botões de limpar - deixar o comportamento padrão
        // O botão já aponta para a URL correta no template
        console.log('Eventos de limpeza de filtros configurados');
    }

    /**
     * Limpa todos os filtros (método mantido para compatibilidade)
     */
    clearAllFilters() {
        console.log('Método clearAllFilters() chamado - usando comportamento padrão do botão');
    }

    /**
     * Vincula evento de aplicação de filtros
     */
    bindApplyFilters() {
        const filterForms = document.querySelectorAll('#chartFilterForm');
        filterForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFilterSubmit(e);
            });
        });
    }

    /**
     * Manipula o envio do formulário de filtros
     */
    handleFilterSubmit(e) {
        // Validar se pelo menos um filtro foi selecionado
        const hasFilters = this.hasActiveFilters();
        
        if (!hasFilters) {
            e.preventDefault();
            this.showNoFiltersWarning();
            return;
        }

        // Mostrar loading
        this.showFormLoading();
        
        // Permitir envio do formulário
        console.log('Aplicando filtros...');
    }

    /**
     * Verifica se há filtros ativos
     */
    hasActiveFilters() {
        // Verificar campos de data
        const dateFields = ['date_from', 'date_to', 'date_from_mobile', 'date_to_mobile'];
        const hasDateFilters = dateFields.some(fieldId => {
            const field = document.getElementById(fieldId);
            return field && field.value;
        });

        // Verificar campos Select2
        const hasSelect2Filters = Array.from(this.select2Instances.values()).some(instance => {
            return instance.val() && instance.val() !== '';
        });

        // Verificar outros campos
        const otherFields = ['typeFilter', 'typeFilter_mobile'];
        const hasOtherFilters = otherFields.some(fieldId => {
            const field = document.getElementById(fieldId);
            return field && field.value;
        });

        return hasDateFilters || hasSelect2Filters || hasOtherFilters;
    }

    /**
     * Mostra aviso de que não há filtros selecionados
     */
    showNoFiltersWarning() {
        // Criar toast de aviso
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-warning border-0 position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Selecione pelo menos um filtro para continuar.
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Mostrar toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remover toast após ser fechado
        toast.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(toast);
        });
    }

    /**
     * Mostra loading no formulário
     */
    showFormLoading() {
        const submitButtons = document.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(button => {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Aplicando...';
            button.disabled = true;
            
            // Restaurar após 3 segundos
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 3000);
        });
    }

    /**
     * Vincula evento de reset de filtros
     */
    bindResetFilters() {
        const resetButtons = document.querySelectorAll('.btn-reset-filters');
        resetButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.resetFiltersToDefaults();
            });
        });
    }

    /**
     * Reseta filtros para valores padrão
     */
    resetFiltersToDefaults() {
        // Implementar lógica de reset para valores padrão específicos
        console.log('Resetando filtros para valores padrão...');
    }

    /**
     * Vincula eventos de exportação
     */
    bindExportEvents() {
        const exportButtons = document.querySelectorAll('[href*="export-pdf"]');
        exportButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleExport(e);
            });
        });
    }

    /**
     * Manipula exportação
     */
    handleExport(e) {
        const button = e.target.closest('a');
        if (!button) return;

        // Verificar se há filtros ativos
        if (!this.hasActiveFilters()) {
            e.preventDefault();
            this.showNoFiltersWarning();
            return;
        }

        // Mostrar loading no botão de exportação
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Gerando...';
        button.style.pointerEvents = 'none';
        
        // Restaurar após 5 segundos
        setTimeout(() => {
            button.innerHTML = originalText;
            button.style.pointerEvents = 'auto';
        }, 5000);
    }

    /**
     * Configura sincronização entre campos mobile e desktop
     */
    setupMobileSync() {
        this.syncDateFields();
        this.syncSelect2Fields();
        this.syncNonSelect2Fields();
    }

    /**
     * Sincroniza campos de data
     */
    syncDateFields() {
        const dateFields = [
            { desktop: 'date_from', mobile: 'date_from_mobile' },
            { desktop: 'date_to', mobile: 'date_to_mobile' }
        ];

        dateFields.forEach(({ desktop, mobile }) => {
            const desktopField = document.getElementById(desktop);
            const mobileField = document.getElementById(mobile);
            
            if (desktopField && mobileField) {
                // Sincronizar desktop -> mobile
                desktopField.addEventListener('change', () => {
                    mobileField.value = desktopField.value;
                });
                
                // Sincronizar mobile -> desktop
                mobileField.addEventListener('change', () => {
                    desktopField.value = mobileField.value;
                });
            }
        });
    }

    /**
     * Sincroniza campos Select2
     */
    syncSelect2Fields() {
        const select2Fields = [
            { desktop: 'categoryFilter', mobile: 'categoryFilter_mobile' },
            { desktop: 'fieldFilter', mobile: 'fieldFilter_mobile' },
            { desktop: 'shepherdFilter', mobile: 'shepherdFilter_mobile' },
            { desktop: 'churchFilter', mobile: 'churchFilter_mobile' }
        ];

        select2Fields.forEach(({ desktop, mobile }) => {
            const desktopField = document.getElementById(desktop);
            const mobileField = document.getElementById(mobile);
            
            if (desktopField && mobileField) {
                // Sincronizar desktop -> mobile
                $(desktopField).on('select2:select select2:clear', (e) => {
                    const value = e.target.value;
                    $(mobileField).val(value).trigger('change');
                });
                
                // Sincronizar mobile -> desktop
                $(mobileField).on('select2:select select2:clear', (e) => {
                    const value = e.target.value;
                    $(desktopField).val(value).trigger('change');
                });
            }
        });
    }

    /**
     * Sincroniza campos não-Select2 (como typeFilter)
     */
    syncNonSelect2Fields() {
        const nonSelect2Fields = [
            { desktop: 'typeFilter', mobile: 'typeFilter_mobile' }
        ];

        nonSelect2Fields.forEach(({ desktop, mobile }) => {
            const desktopField = document.getElementById(desktop);
            const mobileField = document.getElementById(mobile);
            
            if (desktopField && mobileField) {
                // Sincronizar desktop -> mobile
                desktopField.addEventListener('change', () => {
                    mobileField.value = desktopField.value;
                });
                
                // Sincronizar mobile -> desktop
                mobileField.addEventListener('change', () => {
                    desktopField.value = mobileField.value;
                });
            }
        });
    }

    /**
     * Destroi todas as instâncias do Select2
     */
    destroy() {
        this.select2Instances.forEach((instance, fieldId) => {
            try {
                instance.destroy();
            } catch (error) {
                console.error(`Erro ao destruir Select2 para ${fieldId}:`, error);
            }
        });
        this.select2Instances.clear();
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se estamos em uma página com filtros
    const hasFilters = document.querySelector('#chartFilterForm') || 
                      document.querySelector('.filters-container');
    
    if (hasFilters) {
        window.filtersForm = new FiltersForm();
        console.log('Filtros inicializados com Select2');
    }
});

// Exportar para uso global
window.FiltersForm = FiltersForm;
