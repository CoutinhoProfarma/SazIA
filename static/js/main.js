// static/js/main.js
let analysisResults = null;
let charts = {};

$(document).ready(function() {
    // Handle form submission
    $('#uploadForm').on('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const fileInput = $('#fileInput')[0];
        formData.append('file', fileInput.files[0]);
        
        // Show loading
        $('#loadingSpinner').removeClass('d-none');
        
        // Send to backend
        $.ajax({
            url: '/analyze',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                analysisResults = response;
                displayResults(response);
                $('#loadingSpinner').addClass('d-none');
            },
            error: function(xhr, status, error) {
                alert('Erro ao processar arquivo: ' + error);
                $('#loadingSpinner').addClass('d-none');
            }
        });
    });
    
    // Export Excel
    $('#exportExcel').on('click', function() {
        if (analysisResults) {
            window.location.href = '/export/excel?data=' + encodeURIComponent(JSON.stringify(analysisResults));
        }
    });
});

function displayResults(data) {
    // Show results section
    $('#resultsSection').removeClass('d-none');
    
    // Update summary cards
    $('#totalSkus').text(data.total_skus);
    $('#seasonalSkus').text(data.seasonal_skus);
    $('#seasonalityPercentage').text(data.seasonality_percentage.toFixed(2) + '%');
    $('#avgCV').text((data.stats.cv || 0).toFixed(2) + '%');
    
    // Create charts
    createPieChart(data);
    createTopSeasonalChart(data);
    createHistogram(data);
    
    // Populate data table
    populateDataTable(data.items);
}

function createPieChart(data) {
    // Destroy existing chart if any
    if (charts.pie) {
        charts.pie.destroy();
    }
    
    const ctx = document.getElementById('seasonalityPieChart').getContext('2d');
    charts.pie = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Sazonais', 'Não Sazonais'],
            datasets: [{
                data: [
                    data.seasonal_skus,
                    data.total_skus - data.seasonal_skus
                ],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(2);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function createTopSeasonalChart(data) {
    // Destroy existing chart if any
    if (charts.bar) {
        charts.bar.destroy();
    }
    
    // Get top 10 seasonal items
    const seasonalItems = data.items
        .filter(item => item.is_seasonal)
        .sort((a, b) => b.seasonality_index - a.seasonality_index)
        .slice(0, 10);
    
    const ctx = document.getElementById('topSeasonalChart').getContext('2d');
    charts.bar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: seasonalItems.map(item => item.sku),
            datasets: [{
                label: 'Índice de Sazonalidade (%)',
                data: seasonalItems.map(item => item.seasonality_index),
                backgroundColor: 'rgba(255, 159, 64, 0.8)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Índice: ${context.parsed.y.toFixed(2)}%`;
                        }
                    }
                }
            }
        }
    });
}

function createHistogram(data) {
    // Destroy existing chart if any
    if (charts.histogram) {
        charts.histogram.destroy();
    }
    
    // Create bins for histogram
    const bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
    const binCounts = new Array(bins.length - 1).fill(0);
    const binLabels = [];
    
    // Count items in each bin
    data.items.forEach(item => {
        const index = Math.floor(item.seasonality_index / 10);
        if (index < binCounts.length) {
            binCounts[index]++;
        }
    });
    
    // Create labels
    for (let i = 0; i < bins.length - 1; i++) {
        binLabels.push(`${bins[i]}-${bins[i + 1]}%`);
    }
    
    const ctx = document.getElementById('seasonalityHistogram').getContext('2d');
    charts.histogram = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: binLabels,
            datasets: [{
                label: 'Quantidade de SKUs',
                data: binCounts,
                backgroundColor: 'rgba(75, 192, 192, 0.8)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Índice de Sazonalidade'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function populateDataTable(items) {
    // Destroy existing DataTable if any
    if ($.fn.DataTable.isDataTable('#dataTable')) {
        $('#dataTable').DataTable().destroy();
    }
    
    // Clear table body
    $('#dataTable tbody').empty();
    
    // Add rows
    items.forEach(item => {
        const row = `
            <tr>
                <td>${item.sku}</td>
                <td>${item.description || '-'}</td>
                <td>${item.category || '-'}</td>
                <td>
                    ${item.is_seasonal ? 
                        '<span class="badge bg-danger">Sim</span>' : 
                        '<span class="badge bg-success">Não</span>'}
                </td>
                <td>${item.seasonality_index.toFixed(2)}%</td>
                <td>${(item.cv || 0).toFixed(2)}%</td>
                <td>${item.avg_sales.toFixed(2)}</td>
            </tr>
        `;
        $('#dataTable tbody').append(row);
    });
    
    // Initialize DataTable
    $('#dataTable').DataTable({
        pageLength: 25,
        order: [[4, 'desc']], // Order by seasonality index
        language: {
            url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/pt-BR.json'
        },
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ]
    });
}
