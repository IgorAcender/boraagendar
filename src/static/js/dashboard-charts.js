/**
 * Dashboard Charts - Chart.js Integration
 */

// Configuração padrão dos gráficos
const defaultChartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            display: true,
            labels: {
                font: { size: 12, family: "'Segoe UI', 'Roboto', sans-serif" },
                color: '#64748b',
                padding: 15,
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            titleFont: { size: 14, weight: 'bold' },
            bodyFont: { size: 13 },
            borderColor: '#e2e8f0',
            borderWidth: 1,
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(226, 232, 240, 0.3)',
                drawBorder: false,
            },
            ticks: {
                color: '#94a3b8',
                font: { size: 11 },
                callback: function(value) {
                    return 'R$ ' + value.toLocaleString('pt-BR');
                }
            }
        },
        x: {
            grid: { display: false },
            ticks: {
                color: '#94a3b8',
                font: { size: 11 }
            }
        }
    }
};

/**
 * Gráfico de Receita - Últimos 7 Dias
 */
function initChart7Days(chartData) {
    const ctx = document.getElementById('chart-7days');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.map(item => item.date),
            datasets: [{
                label: 'Receita (R$)',
                data: chartData.map(item => item.revenue),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 8,
            }]
        },
        options: {
            ...defaultChartOptions,
            plugins: {
                ...defaultChartOptions.plugins,
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Gráfico de Receita - Últimos 12 Meses
 */
function initChart12Months(chartData) {
    const ctx = document.getElementById('chart-12months');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.map(item => item.month),
            datasets: [{
                label: 'Receita Mensal (R$)',
                data: chartData.map(item => item.revenue),
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(244, 63, 94, 0.8)',
                    'rgba(168, 85, 247, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(244, 63, 94, 0.8)',
                ].slice(0, chartData.length),
                borderColor: [
                    '#667eea',
                    '#10b981',
                    '#f59e0b',
                    '#ec4899',
                    '#8b5cf6',
                    '#3b82f6',
                    '#22c55e',
                    '#f43f5e',
                    '#a855f7',
                    '#3b82f6',
                    '#22c55e',
                    '#f43f5e',
                ].slice(0, chartData.length),
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            ...defaultChartOptions,
            plugins: {
                ...defaultChartOptions.plugins,
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Inicializar todos os gráficos
 */
document.addEventListener('DOMContentLoaded', function() {
    // Debug: Verificar dados disponíveis
    console.log('🔍 Dashboard Charts - Debug');
    console.log('chart7DaysData:', window.chart7DaysData);
    console.log('chart12MonthsData:', window.chart12MonthsData);
    
    // Dados devem ser passados globalmente pela template
    if (typeof window.chart7DaysData !== 'undefined' && window.chart7DaysData && window.chart7DaysData.length > 0) {
        try {
            initChart7Days(window.chart7DaysData);
            console.log('✅ Gráfico 7 dias inicializado');
        } catch(e) {
            console.error('❌ Erro ao inicializar gráfico 7 dias:', e);
        }
    } else {
        console.warn('⚠️ Dados de 7 dias não disponíveis');
    }
    
    if (typeof window.chart12MonthsData !== 'undefined' && window.chart12MonthsData && window.chart12MonthsData.length > 0) {
        try {
            initChart12Months(window.chart12MonthsData);
            console.log('✅ Gráfico 12 meses inicializado');
        } catch(e) {
            console.error('❌ Erro ao inicializar gráfico 12 meses:', e);
        }
    } else {
        console.warn('⚠️ Dados de 12 meses não disponíveis');
    }
});
