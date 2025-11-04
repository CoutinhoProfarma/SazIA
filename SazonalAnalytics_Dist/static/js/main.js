// static/js/main.js
let globalData = null;
let seasonalityChart = null;
let growthChart = null;
let seasonalityDataTable = null;
let growthDataTable = null;

// Configuração dos gráficos
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'top'
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '%';
                }
            }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            ticks: {
                callback: function(value) {
                    return value + '%';
                }
            }
        }
    }
};

// Meses do ano
const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];

// Upload do arquivo
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const sigmaInput = document.getElementById('sigmaInput');
    
    if (!fileInput.files[0]) {
        alert('Por favor, selecione um arquivo');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('sigma', sigmaInput.value);
    
    // Mostrar loading
    document.getElementById('loadingSpinner').classList.remove('d-none');
    document.getElementById('resultsSection').classList.add('d-none');
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Erro ao processar arquivo');
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        globalData = data;
        displayResults(data);
        
    } catch (error) {
        alert('Erro: ' + error.message);
    } finally {
        document.getElementById('loadingSpinner').classList.add('d-none');
    }
});

// Exibir resultados
function displayResults(data) {
    // Mostrar seção de resultados
    document.getElementById('resultsSection').classList.remove('d-none');
    document.getElementById('resultsSection').classList.add('fade-in');
    
    // Preencher filtro de categorias
    const categoryFilter = document.getElementById('categoryFilter');
    categoryFilter.innerHTML = '<option value="">Todas as Categorias</option>';
    data.categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat.category;
        option.textContent = cat.category;
        categoryFilter.appendChild(option);
    });
    
    // Criar gráficos
    updateCharts(data.categories);
    
    // Preencher tabelas
    updateTables(data.categories);
}

// Atualizar gráficos
function updateCharts(categories) {
    const ctx1 = document.getElementById('seasonalityChart').getContext('2d');
    const ctx2 = document.getElementById('growthChart').getContext('2d');
    
    // Destruir gráficos existentes
    if (seasonalityChart) seasonalityChart.destroy();
    if (growthChart) growthChart.destroy();
    
    // Preparar datasets
    const seasonalityDatasets = [];
    const growthDatasets = [];
    
    // Cores para diferentes categorias
    const colors = [
        '#14555a', '#b72026', '#00aeef', '#f7941d',
        '#2ecc71', '#9b59b6', '#34495e', '#e74c3c'
    ];
    
    categories.forEach((cat, index) => {
        const color = colors[index % colors.length];
        
        seasonalityDatasets.push({
            label: cat.category,
            data: cat.seasonality_year,
            borderColor: color,
            backgroundColor: color + '33',
            tension: 0.4
        });
        
        growthDatasets.push({
            label: cat.category,
            data: cat.growth_month,
            borderColor: color,
            backgroundColor: color + '33',
            tension: 0.4
        });
    });
    
    // Criar gráfico de sazonalidade
    seasonalityChart = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: monthNames,
            datasets: seasonalityDatasets
        },
        options: {
            ...chartOptions,
            plugins: {
                ...chartOptions.plugins,
                title: {
                    display: true,
                    text: 'Distribuição Percentual ao Longo do Ano'
                }
            }
        }
    });
    
    // Criar gráfico de crescimento
    growthChart = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: monthNames,
            datasets: growthDatasets
        },
        options: {
            ...chartOptions,
            plugins: {
                ...chartOptions.plugins,
                title: {
                    display: true,
                    text: 'Crescimento Mensal (%)'
                }
            }
        }
    });
}

// Atualizar tabelas
function updateTables(categories) {
    // Preparar dados para DataTables
    const seasonalityData = [];
    const growthData = [];
    
    categories.forEach(cat => {
        const seasonRow = [cat.category, ...cat.seasonality_year.map(v => v.toFixed(2) + '%')];
        const growthRow = [cat.category, ...cat.growth_month.map(v => v.toFixed(2) + '%')];
        
        seasonalityData.push(seasonRow);
        growthData.push(growthRow);
    });
    
    // Destruir tabelas existentes
    if (seasonalityDataTable) seasonalityDataTable.destroy();
    if (growthDataTable) growthDataTable.destroy();
    
    // Criar DataTables
    seasonalityDataTable = $('#seasonalityTable').DataTable({
        data: seasonalityData,
        language: {
            url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/pt-BR.json'
        },
        pageLength: 10,
        responsive: true,
        order: [[0, 'asc']]
    });
    
    growthDataTable = $('#growthTable').DataTable({
        data: growthData,
        language: {
            url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/pt-BR.json'
        },
        pageLength: 10,
        responsive: true,
        order: [[0, 'asc']]
    });
}

// Filtrar por categoria
document.getElementById('categoryFilter').addEventListener('change', (e) => {
    const selectedCategory = e.target.value;
    
    if (!selectedCategory) {
        // Mostrar todas as categorias
        updateCharts(globalData.categories);
        seasonalityDataTable.search('').draw();
        growthDataTable.search('').draw();
    } else {
        // Filtrar categoria específica
        const filtered = globalData.categories.filter(cat => cat.category === selectedCategory);
        updateCharts(filtered);
        seasonalityDataTable.search(selectedCategory).draw();
        growthDataTable.search(selectedCategory).draw();
    }
});

// Toggle tabelas
function toggleTable(tableId) {
    const container = document.getElementById(tableId + 'Container');
    const button = container.previousElementSibling.querySelector('button i');
    
    if (container.style.display === 'none') {
        container.style.display = 'block';
        button.className = 'fas fa-chevron-up';
    } else {
        container.style.display = 'none';
        button.className = 'fas fa-chevron-down';
    }
}

// Download resultados
async function downloadResults(format) {
    if (!globalData) {
        alert('Nenhum dado para download');
        return;
    }
    
    const dataStr = encodeURIComponent(JSON.stringify(globalData));
    window.location.href = `/download/${format}?data=${dataStr}`;
}
