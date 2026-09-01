/**
 * Dashboard Management
 */

async function loadModule3Data() {
    try {
        // Get latest calculation
        const calcRes = await fetch('/api/calculations');
        const calculations = await calcRes.json();
        
        if (calculations.length === 0) {
            showNotification('Run Bellman-Ford algorithm first', 'info');
            return;
        }
        
        const latestCalc = calculations[0];
        
        // Get results
        const resultsRes = await fetch(`/api/calculations/${latestCalc.id}/results`);
        const resultsData = await resultsRes.json();
        
        // Update summary cards
        document.getElementById('dashboard-locations').textContent = app.locations.length;
        document.getElementById('dashboard-routes').textContent = app.routes.length;
        document.getElementById('dashboard-source').textContent = latestCalc.source_label || '-';
        document.getElementById('dashboard-reachable').textContent = resultsData.statistics.reachable_count;
        document.getElementById('dashboard-unreachable').textContent = resultsData.statistics.unreachable_count;
        
        // Cost summary
        document.getElementById('dashboard-min-cost').textContent = 
            resultsData.statistics.min_cost ? '₹' + resultsData.statistics.min_cost.toFixed(2) : '₹0';
        document.getElementById('dashboard-max-cost').textContent = 
            resultsData.statistics.max_cost ? '₹' + resultsData.statistics.max_cost.toFixed(2) : '₹0';
        document.getElementById('dashboard-total-cost').textContent = 
            resultsData.statistics.total_cost ? '₹' + resultsData.statistics.total_cost.toFixed(2) : '₹0';
        document.getElementById('dashboard-avg-cost').textContent = 
            resultsData.statistics.avg_cost ? '₹' + resultsData.statistics.avg_cost.toFixed(2) : '₹0';
        document.getElementById('dashboard-avg-cost-detail').textContent = 
            resultsData.statistics.avg_cost ? '₹' + resultsData.statistics.avg_cost.toFixed(2) : '₹0';
        
        // Distribution table
        displayDistributionTable(resultsData.cost_distribution);
        
        // Display best routes table
        displayBestRoutesTable(resultsData.results, latestCalc);
        
        // Initialize charts
        initCharts(resultsData.results);
        
        // Display all locations on map
        displayAllRoutesOnMap('module3');
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showNotification('Error loading dashboard data', 'danger');
    }
}

function displayDistributionTable(distribution) {
    const tbody = document.getElementById('distribution-body');
    tbody.innerHTML = '';
    
    for (const [range, data] of Object.entries(distribution)) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><small>${range}</small></td>
            <td>${data.count}</td>
            <td>${data.percentage}%</td>
        `;
        tbody.appendChild(tr);
    }
}

function displayBestRoutesTable(results, calculation) {
    const tbody = document.getElementById('best-routes-body');
    tbody.innerHTML = '';
    
    results.forEach(result => {
        if (result.destination_label === calculation.source_label) return;
        
        const tr = document.createElement('tr');
        const pathDisplay = result.path && result.path.length > 0 ? result.path.join(' → ') : '-';
        const costDisplay = result.minimum_cost !== null ? '₹' + result.minimum_cost.toFixed(2) : '∞';
        const distanceDisplay = result.total_distance ? result.total_distance.toFixed(2) + ' km' : '-';
        const timeDisplay = result.total_time ? result.total_time + ' min' : '-';
        
        const statusBadgeClass = result.status === 'REACHABLE' ? 'bg-success' : 'bg-danger';
        const viewButtonDisabled = !result.path ? 'disabled' : '';
        const pathParam = result.path ? result.path.join('|') : '';
        
        tr.innerHTML = `
            <td><strong>${result.destination_label}: ${result.destination_name}</strong></td>
            <td><small>${pathDisplay}</small></td>
            <td>${costDisplay}</td>
            <td>${distanceDisplay}</td>
            <td>${timeDisplay}</td>
            <td><span class="badge ${statusBadgeClass}">${result.status}</span></td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewRouteOnMap('${pathParam}')" ${viewButtonDisabled}>
                    <i class="fas fa-map"></i> View
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function viewRouteOnMap(pathStr) {
    const path = pathStr.split('|');
    clearMapPolylines('module3');
    highlightBestPath(path, 'module3');
}

function initCharts(results) {
    // Prepare data
    const reachableResults = results.filter(r => r.status === 'REACHABLE' && r.minimum_cost !== null);
    
    const labels = reachableResults.map(r => r.destination_label);
    const costs = reachableResults.map(r => r.minimum_cost);
    
    // Cost chart
    const costChartCtx = document.getElementById('cost-chart').getContext('2d');
    
    if (app.charts.cost) {
        app.charts.cost.destroy();
    }
    
    app.charts.cost = new Chart(costChartCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Minimum Cost (₹)',
                data: costs,
                backgroundColor: '#3498db',
                borderColor: '#2980b9',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true, position: 'top' }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Cost (₹)' }
                }
            }
        }
    });
    
    // Distribution chart
    const distribution = {};
    const ranges = [
        [0, 100], [101, 200], [201, 300], [301, 500], [501, Infinity]
    ];
    const rangeLabels = ['₹0-100', '₹101-200', '₹201-300', '₹301-500', '₹501+'];
    
    ranges.forEach((range, idx) => {
        distribution[rangeLabels[idx]] = costs.filter(c => c >= range[0] && c <= range[1]).length;
    });
    
    const distCtx = document.getElementById('distribution-chart').getContext('2d');
    
    if (app.charts.distribution) {
        app.charts.distribution.destroy();
    }
    
    app.charts.distribution = new Chart(distCtx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(distribution),
            datasets: [{
                data: Object.values(distribution),
                backgroundColor: [
                    '#3498db',
                    '#2ecc71',
                    '#f39c12',
                    '#e74c3c',
                    '#9b59b6'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true, position: 'bottom' }
            }
        }
    });
}
