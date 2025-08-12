# Dashboard

O Dashboard é a página principal do Nations Flow, fornecendo uma visão geral das finanças da igreja.

## 🎯 Visão Geral

O Dashboard oferece:

- **Visão Geral Financeira**: Resumo de receitas e despesas
- **Gráficos Interativos**: Visualizações dinâmicas dos dados
- **Estatísticas em Tempo Real**: Indicadores de performance
- **Transações Recentes**: Lista das últimas movimentações
- **Navegação Rápida**: Acesso direto às principais funcionalidades

## 📊 Componentes do Dashboard

### 1. Cards de Estatísticas

```html
<!-- Cards principais -->
<div class="stats-cards">
    <div class="stat-card income">
        <h3>Receitas do Mês</h3>
        <p class="amount">R$ 15.000,00</p>
        <span class="change positive">+12%</span>
    </div>
    
    <div class="stat-card expense">
        <h3>Despesas do Mês</h3>
        <p class="amount">R$ 8.500,00</p>
        <span class="change negative">-5%</span>
    </div>
    
    <div class="stat-card balance">
        <h3>Saldo Atual</h3>
        <p class="amount">R$ 6.500,00</p>
        <span class="change positive">+7%</span>
    </div>
    
    <div class="stat-card transactions">
        <h3>Transações</h3>
        <p class="amount">127</p>
        <span class="change neutral">0%</span>
    </div>
</div>
```

### 2. Gráficos Interativos

#### Gráfico de Receitas vs Despesas

```javascript
// Chart.js - Gráfico de linha
const ctx = document.getElementById('revenueChart').getContext('2d');
const revenueChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        datasets: [{
            label: 'Receitas',
            data: [12000, 15000, 14000, 16000, 15000, 18000],
            borderColor: '#28a745',
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            tension: 0.4
        }, {
            label: 'Despesas',
            data: [8000, 9000, 8500, 9500, 8800, 9200],
            borderColor: '#dc3545',
            backgroundColor: 'rgba(220, 53, 69, 0.1)',
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Receitas vs Despesas (Últimos 6 meses)'
            }
        }
    }
});
```

#### Gráfico de Pizza - Categorias

```javascript
// Gráfico de pizza para categorias
const pieCtx = document.getElementById('categoryChart').getContext('2d');
const categoryChart = new Chart(pieCtx, {
    type: 'pie',
    data: {
        labels: ['Dízimos', 'Ofertas', 'Aluguel', 'Energia', 'Água', 'Outros'],
        datasets: [{
            data: [45, 25, 15, 8, 5, 2],
            backgroundColor: [
                '#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6c757d', '#6f42c1'
            ]
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom'
            }
        }
    }
});
```

### 3. Tabela de Transações Recentes

```html
<div class="recent-transactions">
    <h3>Transações Recentes</h3>
    <div class="table-responsive">
        <table class="table">
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Descrição</th>
                    <th>Categoria</th>
                    <th>Igreja</th>
                    <th>Valor</th>
                    <th>Tipo</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>05/08/2025</td>
                    <td>Dízimos do mês</td>
                    <td>Dízimos e Ofertas</td>
                    <td>Igreja Central</td>
                    <td class="income">R$ 5.000,00</td>
                    <td><span class="badge bg-success">Receita</span></td>
                </tr>
                <tr>
                    <td>04/08/2025</td>
                    <td>Conta de luz</td>
                    <td>Energia Elétrica</td>
                    <td>Igreja Central</td>
                    <td class="expense">R$ 800,00</td>
                    <td><span class="badge bg-danger">Despesa</span></td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
```

## 🎨 Estilos CSS

### Cards de Estatísticas

```css
.stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border-left: 4px solid;
    transition: transform 0.2s;
}

.stat-card:hover {
    transform: translateY(-2px);
}

.stat-card.income {
    border-left-color: #28a745;
}

.stat-card.expense {
    border-left-color: #dc3545;
}

.stat-card.balance {
    border-left-color: #17a2b8;
}

.stat-card.transactions {
    border-left-color: #6c757d;
}

.stat-card h3 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stat-card .amount {
    font-size: 2rem;
    font-weight: bold;
    margin: 0 0 0.5rem 0;
    color: #333;
}

.stat-card .change {
    font-size: 0.8rem;
    padding: 0.2rem 0.5rem;
    border-radius: 15px;
    font-weight: 500;
}

.change.positive {
    background: rgba(40, 167, 69, 0.1);
    color: #28a745;
}

.change.negative {
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;
}

.change.neutral {
    background: rgba(108, 117, 125, 0.1);
    color: #6c757d;
}
```

### Gráficos

```css
.charts-container {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
}

.chart-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.chart-card h3 {
    margin: 0 0 1rem 0;
    color: #333;
    font-size: 1.2rem;
}

@media (max-width: 768px) {
    .charts-container {
        grid-template-columns: 1fr;
    }
}
```

## 🔧 Funcionalidades JavaScript

### Atualização Automática

```javascript
// Atualizar dados a cada 5 minutos
setInterval(() => {
    updateDashboardData();
}, 300000);

function updateDashboardData() {
    fetch('/api/dashboard/stats/')
        .then(response => response.json())
        .then(data => {
            updateStatCards(data.stats);
            updateCharts(data.charts);
        })
        .catch(error => {
            console.error('Erro ao atualizar dashboard:', error);
        });
}
```

### Filtros de Período

```javascript
// Filtros de período
document.getElementById('periodFilter').addEventListener('change', function() {
    const period = this.value;
    updateDashboardPeriod(period);
});

function updateDashboardPeriod(period) {
    fetch(`/api/dashboard/stats/?period=${period}`)
        .then(response => response.json())
        .then(data => {
            updateStatCards(data.stats);
            updateCharts(data.charts);
        });
}
```

### Responsividade

```javascript
// Ajustar gráficos para mobile
function adjustChartsForMobile() {
    const isMobile = window.innerWidth < 768;
    
    if (isMobile) {
        // Configurações para mobile
        Chart.defaults.font.size = 12;
        Chart.defaults.plugins.legend.position = 'bottom';
    } else {
        // Configurações para desktop
        Chart.defaults.font.size = 14;
        Chart.defaults.plugins.legend.position = 'right';
    }
}

window.addEventListener('resize', adjustChartsForMobile);
adjustChartsForMobile();
```

## 📊 Dados do Dashboard

### View do Dashboard

```python
class DashboardView(LoginRequiredMixin, View):
    template_name = 'pages/dashboard.html'
    
    def get(self, request):
        context = {
            'stats': self.get_stats(),
            'recent_transactions': self.get_recent_transactions(),
            'chart_data': self.get_chart_data(),
        }
        return render(request, self.template_name, context)
    
    def get_stats(self):
        """Calcula estatísticas do dashboard"""
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        # Receitas do mês
        monthly_income = Transaction.objects.filter(
            type='income',
            date__month=current_month,
            date__year=current_year
        ).aggregate(total=Sum('value'))['total'] or 0
        
        # Despesas do mês
        monthly_expense = Transaction.objects.filter(
            type='expense',
            date__month=current_month,
            date__year=current_year
        ).aggregate(total=Sum('value'))['total'] or 0
        
        # Saldo atual
        total_income = Transaction.objects.filter(
            type='income'
        ).aggregate(total=Sum('value'))['total'] or 0
        
        total_expense = Transaction.objects.filter(
            type='expense'
        ).aggregate(total=Sum('value'))['total'] or 0
        
        balance = total_income - total_expense
        
        # Total de transações
        total_transactions = Transaction.objects.count()
        
        return {
            'monthly_income': monthly_income,
            'monthly_expense': monthly_expense,
            'balance': balance,
            'total_transactions': total_transactions,
        }
    
    def get_recent_transactions(self):
        """Busca transações recentes"""
        return Transaction.objects.select_related(
            'category', 'church', 'user'
        ).order_by('-date')[:10]
    
    def get_chart_data(self):
        """Dados para os gráficos"""
        # Dados dos últimos 6 meses
        months = []
        income_data = []
        expense_data = []
        
        for i in range(6):
            date = timezone.now() - timedelta(days=30*i)
            month = date.month
            year = date.year
            
            months.append(date.strftime('%b'))
            
            income = Transaction.objects.filter(
                type='income',
                date__month=month,
                date__year=year
            ).aggregate(total=Sum('value'))['total'] or 0
            
            expense = Transaction.objects.filter(
                type='expense',
                date__month=month,
                date__year=year
            ).aggregate(total=Sum('value'))['total'] or 0
            
            income_data.append(float(income))
            expense_data.append(float(expense))
        
        return {
            'months': months,
            'income': income_data,
            'expense': expense_data,
        }
```

### API para Dados

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def dashboard_stats_api(request):
    """API para dados do dashboard"""
    period = request.GET.get('period', 'month')
    
    # Lógica para calcular estatísticas baseada no período
    stats = calculate_stats(period)
    
    return JsonResponse({
        'stats': stats,
        'success': True
    })

def calculate_stats(period):
    """Calcula estatísticas baseadas no período"""
    if period == 'month':
        # Estatísticas do mês atual
        pass
    elif period == 'quarter':
        # Estatísticas do trimestre
        pass
    elif period == 'year':
        # Estatísticas do ano
        pass
    
    return {
        'income': 15000.00,
        'expense': 8500.00,
        'balance': 6500.00,
        'transactions': 127
    }
```

## 🔍 Personalização

### Temas de Cores

```css
/* Tema claro (padrão) */
:root {
    --primary-color: #007bff;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #17a2b8;
    --light-color: #f8f9fa;
    --dark-color: #343a40;
}

/* Tema escuro */
[data-theme="dark"] {
    --primary-color: #0056b3;
    --success-color: #1e7e34;
    --danger-color: #c82333;
    --warning-color: #e0a800;
    --info-color: #138496;
    --light-color: #343a40;
    --dark-color: #f8f9fa;
}
```

### Configurações do Usuário

```python
class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dashboard_period = models.CharField(
        max_length=20,
        choices=[
            ('week', 'Semana'),
            ('month', 'Mês'),
            ('quarter', 'Trimestre'),
            ('year', 'Ano'),
        ],
        default='month'
    )
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Claro'),
            ('dark', 'Escuro'),
            ('auto', 'Automático'),
        ],
        default='light'
    )
    auto_refresh = models.BooleanField(default=True)
    refresh_interval = models.IntegerField(default=5)  # minutos
```

## 📱 Responsividade

### Breakpoints

```css
/* Mobile First */
@media (max-width: 576px) {
    .stats-cards {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .stat-card {
        padding: 1rem;
    }
    
    .stat-card .amount {
        font-size: 1.5rem;
    }
}

@media (min-width: 577px) and (max-width: 768px) {
    .stats-cards {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (min-width: 769px) {
    .stats-cards {
        grid-template-columns: repeat(4, 1fr);
    }
}
```

### Navegação Mobile

```javascript
// Sidebar responsiva
function toggleMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    sidebar.classList.toggle('show');
    overlay.classList.toggle('show');
}

// Fechar sidebar ao clicar fora
document.getElementById('sidebar-overlay').addEventListener('click', function() {
    toggleMobileSidebar();
});
```

## 🔧 Manutenção

### Performance

```python
# Otimização de queries
class DashboardView(LoginRequiredMixin, View):
    def get_stats(self):
        # Usar select_related para evitar N+1 queries
        transactions = Transaction.objects.select_related(
            'category', 'church'
        ).filter(
            date__month=timezone.now().month
        )
        
        # Usar annotate para cálculos no banco
        from django.db.models import Sum, Count
        
        stats = transactions.aggregate(
            total_income=Sum('value', filter=Q(type='income')),
            total_expense=Sum('value', filter=Q(type='expense')),
            count=Count('id')
        )
        
        return stats
```

### Cache

```python
from django.core.cache import cache

def get_cached_stats():
    """Busca estatísticas do cache"""
    cache_key = 'dashboard_stats'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = calculate_stats()
        cache.set(cache_key, stats, 300)  # Cache por 5 minutos
    
    return stats
```

## 📊 Métricas e Analytics

### Eventos de Tracking

```javascript
// Tracking de interações do usuário
function trackDashboardInteraction(action, data) {
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            'event_category': 'Dashboard',
            'event_label': data
        });
    }
}

// Exemplos de tracking
document.querySelectorAll('.stat-card').forEach(card => {
    card.addEventListener('click', function() {
        const cardType = this.classList.contains('income') ? 'income' : 'expense';
        trackDashboardInteraction('card_click', cardType);
    });
});
```

### Analytics de Uso

```python
class DashboardAnalytics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'action', 'timestamp'])
        ]
```

O Dashboard é o coração do Nations Flow, fornecendo uma visão clara e intuitiva das finanças da igreja. Com gráficos interativos, estatísticas em tempo real e uma interface responsiva, os usuários podem tomar decisões informadas sobre a gestão financeira. 