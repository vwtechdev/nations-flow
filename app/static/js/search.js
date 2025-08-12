'use strict';

// Search functionality for tables
class TableSearch {
    constructor(tableId, searchInputId) {
        this.table = document.getElementById(tableId);
        this.searchInput = document.getElementById(searchInputId);
        this.tbody = this.table.querySelector('tbody');
        this.rows = this.tbody.querySelectorAll('tr');
        
        this.init();
    }
    
    init() {
        if (!this.searchInput || !this.table) {
            console.error('Search input or table not found');
            return;
        }
        
        // Add clear button to search input
        this.addClearButton();
        
        // Add event listener for search input
        this.searchInput.addEventListener('input', (e) => {
            this.performSearch(e.target.value);
            this.toggleClearButton(e.target.value);
        });
        
        // Add event listener for Enter key to clear search
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.value === '') {
                e.target.blur();
            }
        });
        
        // Add focus effects with animations
        this.searchInput.addEventListener('focus', () => {
            this.searchInput.parentElement.classList.add('focused');
        });
        
        this.searchInput.addEventListener('blur', () => {
            this.searchInput.parentElement.classList.remove('focused');
        });
        
        // Add typing animation
        this.searchInput.addEventListener('input', () => {
            this.addTypingEffect();
        });
        
        // Add search button functionality
        this.addSearchButtonFunctionality();
        
        console.log('Table search initialized for:', this.table.id);
    }
    
    addClearButton() {
        const clearButton = document.createElement('button');
        clearButton.type = 'button';
        clearButton.className = 'search-clear';
        clearButton.innerHTML = '<i class="bi bi-x-lg"></i>';
        clearButton.title = 'Limpar busca';
        
        clearButton.addEventListener('click', () => {
            this.clearSearch();
        });
        
        this.searchInput.parentElement.appendChild(clearButton);
        this.clearButton = clearButton;
    }
    
    toggleClearButton(value) {
        if (value.length > 0) {
            this.clearButton.classList.add('show');
            this.clearButton.style.animation = 'fadeInScale 0.3s ease';
        } else {
            this.clearButton.classList.remove('show');
            this.clearButton.style.animation = 'fadeOutScale 0.3s ease';
        }
    }
    
    addSearchButtonFunctionality() {
        const searchButton = this.searchInput.parentElement.querySelector('.search-button');
        if (searchButton) {
            searchButton.addEventListener('click', () => {
                this.performSearch(this.searchInput.value);
                this.searchInput.focus();
            });
        }
    }
    
    addTypingEffect() {
        this.searchInput.style.animation = 'typingGlow 0.3s ease';
        setTimeout(() => {
            this.searchInput.style.animation = '';
        }, 300);
    }
    
    performSearch(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        let visibleCount = 0;
        
        this.rows.forEach((row) => {
            const text = row.textContent.toLowerCase();
            const isVisible = text.includes(term);
            
            if (isVisible) {
                row.style.display = '';
                visibleCount++;
                // Add highlight effect for search term
                if (term.length > 0) {
                    this.highlightSearchTerm(row, term);
                } else {
                    this.removeHighlight(row);
                }
            } else {
                row.style.display = 'none';
                this.removeHighlight(row);
            }
        });
        
        // Show/hide "no results" message
        this.showNoResultsMessage(visibleCount === 0 && term !== '');
        
        // Update search input placeholder with results count
        this.updateSearchPlaceholder(visibleCount, this.rows.length);
        
        // Add animation for results
        this.animateResults();
    }
    
    highlightSearchTerm(row, term) {
        const cells = row.querySelectorAll('td');
        cells.forEach(cell => {
            const text = cell.textContent;
            const highlightedText = text.replace(
                new RegExp(`(${term})`, 'gi'),
                '<mark class="search-highlight">$1</mark>'
            );
            if (highlightedText !== text) {
                cell.innerHTML = highlightedText;
            }
        });
    }
    
    removeHighlight(row) {
        const cells = row.querySelectorAll('td');
        cells.forEach(cell => {
            const marks = cell.querySelectorAll('mark.search-highlight');
            marks.forEach(mark => {
                mark.outerHTML = mark.textContent;
            });
        });
    }
    
    showNoResultsMessage(show) {
        let noResultsRow = this.tbody.querySelector('.no-results-row');
        
        if (show) {
            if (!noResultsRow) {
                noResultsRow = document.createElement('tr');
                noResultsRow.className = 'no-results-row';
                noResultsRow.innerHTML = `
                    <td colspan="100%" class="text-center text-muted py-4">
                        <i class="bi bi-search me-2"></i>
                        Nenhum resultado encontrado para "${this.searchInput.value}"
                    </td>
                `;
                this.tbody.appendChild(noResultsRow);
                noResultsRow.style.animation = 'fadeInUp 0.5s ease';
            }
        } else {
            if (noResultsRow) {
                noResultsRow.style.animation = 'fadeOutDown 0.3s ease';
                setTimeout(() => {
                    noResultsRow.remove();
                }, 300);
            }
        }
    }
    
    updateSearchPlaceholder(visibleCount, totalCount) {
        if (visibleCount === totalCount) {
            this.searchInput.placeholder = 'Pesquisar...';
        } else {
            this.searchInput.placeholder = `${visibleCount} de ${totalCount} resultados`;
        }
    }
    
    clearSearch() {
        this.searchInput.value = '';
        this.performSearch('');
        this.toggleClearButton('');
        this.searchInput.focus();
        
        // Add clear animation
        this.searchInput.style.animation = 'clearSearch 0.3s ease';
        setTimeout(() => {
            this.searchInput.style.animation = '';
        }, 300);
    }
    
    animateResults() {  
        const visibleRows = this.tbody.querySelectorAll('tr:not([style*="display: none"])');
        visibleRows.forEach((row, index) => {
            row.style.animation = 'none';
            setTimeout(() => {
                row.style.animation = `fadeInUp 0.4s ease ${index * 0.08}s`;
            }, 10);
        });
    }
}

// Initialize search for all tables when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize search for categories table
    if (document.getElementById('categoriesTable') && document.getElementById('categorySearch')) {
        new TableSearch('categoriesTable', 'categorySearch');
    }
    
    // Initialize search for fields table
    if (document.getElementById('fieldsTable') && document.getElementById('fieldSearch')) {
        new TableSearch('fieldsTable', 'fieldSearch');
    }
    
    // Initialize search for churches table
    if (document.getElementById('churchesTable') && document.getElementById('churchSearch')) {
        new TableSearch('churchesTable', 'churchSearch');
    }
    
    // Initialize search for users table
    if (document.getElementById('usersTable') && document.getElementById('userSearch')) {
        new TableSearch('usersTable', 'userSearch');
    }
    
    // Add search input styles
    addSearchInputStyles();
});

// Add custom styles for search inputs
function addSearchInputStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .search-container {
            position: relative;
            margin-bottom: 1.5rem;
        }
        
        .search-input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
            border: 1px solid #673ab7;
            border-radius: 0.5rem;
            background: #ffffff;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
        }
        
        .search-input {
            flex: 1;
            padding: 0.75rem 3rem 0.75rem 1rem;
            border: none;
            background: transparent;
            color: #000000;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }
        
        .search-input::placeholder {
            color: #666666;
            opacity: 0.8;
        }
        
        .search-input:focus {
            background: rgba(103, 58, 183, 0.05);
        }
        
        .search-clear {
            position: absolute;
            right: 4rem;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: #666666;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 50%;
            transition: all 0.3s ease;
            display: none;
            z-index: 10;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
        }
        
        .search-clear:hover {
            background-color: rgba(103, 58, 183, 0.1);
            color: var(--primary-color);
            transform: translateY(-50%) scale(1.1);
        }
        
        .search-clear.show {
            display: flex;
        }
        
        .search-button {
            background: var(--primary-color);
            border: none;
            padding: 0.75rem 1rem;
            color: #ffffff;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
        }
        
        .search-button:hover {
            background: var(--primary-hover);
            transform: scale(1.05);
        }
        
        .no-results-row td {
            background-color: #f8f9fa;
            font-style: italic;
            border-radius: 0.5rem;
        }
        
        .search-highlight {
            background: linear-gradient(120deg, #fff3cd 0%, #ffeaa7 100%);
            color: #856404;
            padding: 0.2rem 0.4rem;
            border-radius: 0.3rem;
            font-weight: 600;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .table-responsive {
            border-radius: 0.75rem;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        
        .table {
            margin-bottom: 0;
        }
        
        .table thead th {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-bottom: 2px solid #dee2e6;
            font-weight: 600;
            color: #495057;
            padding: 1rem;
        }
        
        .table tbody tr {
            transition: all 0.3s ease;
        }
        
        .table tbody tr:hover {
            background: linear-gradient(135deg, rgba(103, 58, 183, 0.05) 0%, rgba(103, 58, 183, 0.02) 100%);
            transform: translateX(2px);
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeOutDown {
            from {
                opacity: 1;
                transform: translateY(0);
            }
            to {
                opacity: 0;
                transform: translateY(20px);
            }
        }
        
        @keyframes typingGlow {
            0% { box-shadow: 0 0 10px rgba(0, 212, 255, 0.3); }
            100% { box-shadow: 0 0 15px rgba(0, 212, 255, 0.5); }
        }
        
        @keyframes clearSearch {
            0% { transform: scale(1); }
            50% { transform: scale(0.98); }
            100% { transform: scale(1); }
        }
        
        @keyframes fadeInScale {
            0% { 
                opacity: 0; 
                transform: translateY(-50%) scale(0.8); 
            }
            100% { 
                opacity: 1; 
                transform: translateY(-50%) scale(1); 
            }
        }
        
        @keyframes fadeOutScale {
            0% { 
                opacity: 1; 
                transform: translateY(-50%) scale(1); 
            }
            100% { 
                opacity: 0; 
                transform: translateY(-50%) scale(0.8); 
            }
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .search-input {
                font-size: 16px; /* Prevents zoom on iOS */
            }
            
            .search-container {
                margin-bottom: 1rem;
            }
        }
    `;
    document.head.appendChild(style);
} 