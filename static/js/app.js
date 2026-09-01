/**
 * Real-Time Delivery Cost Calculator
 * Main Application Logic
 */

// Global state
const app = {
    locations: [],
    routes: [],
    currentCalculation: null,
    maps: {
        overview: null,
        module1: null,
        module3: null
    },
    charts: {
        cost: null,
        distribution: null
    }
};

// Module switching
function showModule(moduleName) {
    // Hide all modules
    document.querySelectorAll('.module-view').forEach(el => el.style.display = 'none');
    
    // Show selected module
    document.getElementById(moduleName + '-module').style.display = 'block';
    
    // Initialize maps if needed
    setTimeout(() => {
        if (moduleName === 'overview' && app.maps.overview) {
            app.maps.overview.invalidateSize();
            loadOverviewData();
        } else if (moduleName === 'module1' && app.maps.module1) {
            app.maps.module1.invalidateSize();
            refreshModule1Map();
        } else if (moduleName === 'module3' && app.maps.module3) {
            app.maps.module3.invalidateSize();
            loadModule3Data();
        }
    }, 100);
}

// Initialize demo data
function initDemoData() {
    fetch('/init-demo-data', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            showNotification('Demo data initialized: ' + data.locations + ' locations, ' + data.routes + ' routes', 'success');
            loadLocations().then(() => loadRoutes()).then(() => {
                refreshModule1View();
                showModule('module1');
            });
        })
        .catch(error => {
            showNotification('Error initializing demo data: ' + error, 'danger');
        });
}

// Notification system
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '100px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Initialize maps
        initMaps();
        
        // Load data
        await loadLocations();
        await loadRoutes();
        
        // Update UI
        refreshModule1View();
        loadOverviewData();
        
        // Show overview by default
        showModule('overview');
        
        // Setup cost mode toggle
        document.getElementById('cost-mode-manual').addEventListener('change', () => {
            document.getElementById('manual-cost-mode').style.display = 'block';
            document.getElementById('auto-cost-mode').style.display = 'none';
        });
        
        document.getElementById('cost-mode-auto').addEventListener('change', () => {
            document.getElementById('manual-cost-mode').style.display = 'none';
            document.getElementById('auto-cost-mode').style.display = 'block';
        });
        
        // Setup auto-calculate cost
        ['base-charge', 'cost-per-km', 'cost-per-min', 'route-distance', 'route-time'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('change', calculateAutoCost);
                el.addEventListener('input', calculateAutoCost);
            }
        });
        
    } catch (error) {
        console.error('Error initializing application:', error);
        showNotification('Error initializing application', 'danger');
    }
});

// Calculate auto cost
function calculateAutoCost() {
    const distance = parseFloat(document.getElementById('route-distance')?.textContent || 0);
    const time = parseFloat(document.getElementById('route-time')?.textContent || 0);
    const baseCharge = parseFloat(document.getElementById('base-charge').value || 50);
    const costPerKm = parseFloat(document.getElementById('cost-per-km').value || 10);
    const costPerMin = parseFloat(document.getElementById('cost-per-min').value || 2);
    
    if (distance && time) {
        const cost = baseCharge + (distance * costPerKm) + (time * costPerMin);
        const breakdown = `₹${baseCharge} + (₹${costPerKm}/km × ${distance.toFixed(2)}km) + (₹${costPerMin}/min × ${time}min) = ₹${cost.toFixed(2)}`;
        
        document.getElementById('cost-calculation-display').textContent = breakdown;
        document.getElementById('route-cost-manual').value = cost.toFixed(2);
    }
}

// Load locations from API
async function loadLocations() {
    try {
        const response = await fetch('/api/locations');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        app.locations = await response.json();
        updateLocationSelects();
        return app.locations;
    } catch (error) {
        console.error('Error loading locations:', error);
        return [];
    }
}

// Load routes from API
async function loadRoutes() {
    try {
        const response = await fetch('/api/routes');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        app.routes = await response.json();
        return app.routes;
    } catch (error) {
        console.error('Error loading routes:', error);
        return [];
    }
}

// Update location select dropdowns
function updateLocationSelects() {
    const selects = [
        'route-source',
        'route-destination',
        'source-location',
        'destination-select'
    ];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            const currentValue = select.value;
            select.innerHTML = '<option value="">-- Select Location --</option>';
            
            app.locations.forEach(loc => {
                const option = document.createElement('option');
                option.value = loc.id;
                option.textContent = `${loc.node_label}: ${loc.name}`;
                option.dataset.label = loc.node_label;
                select.appendChild(option);
            });
            
            if (currentValue) select.value = currentValue;
        }
    });
}

// Get current graph data
async function getGraphData() {
    try {
        const response = await fetch('/api/graph');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Error getting graph data:', error);
        return null;
    }
}

// Refresh module 1 view
function refreshModule1View() {
    displayLocationsTable();
    displayEdgeList();
    displayAdjacencyList();
    updateGraphStats();
}

// Update overview data
async function loadOverviewData() {
    try {
        const graph = await getGraphData();
        if (!graph) return;
        
        document.getElementById('overview-locations').textContent = graph.vertex_count;
        document.getElementById('overview-routes').textContent = graph.edge_count;
        
        const sourceSelect = document.getElementById('source-location');
        const sourceLabel = sourceSelect.value ? sourceSelect.options[sourceSelect.selectedIndex].dataset.label : '-';
        document.getElementById('overview-source').textContent = sourceLabel || '-';
        
        // Count calculations
        const calcResponse = await fetch('/api/calculations');
        if (calcResponse.ok) {
            const calculations = await calcResponse.json();
            document.getElementById('overview-calculations').textContent = calculations.length;
        }
    } catch (error) {
        console.error('Error loading overview data:', error);
    }
}

// Update graph statistics
function updateGraphStats() {
    const graph = getGraphData();
    Promise.resolve(graph).then(g => {
        if (g) {
            document.getElementById('vertex-count').textContent = g.vertex_count;
            document.getElementById('edge-count').textContent = g.edge_count;
            
            let totalCost = 0;
            g.edges.forEach(edge => {
                totalCost += edge.weight;
            });
            document.getElementById('total-cost').textContent = '₹' + totalCost.toFixed(2);
            
            // Update complexity
            const maxIter = g.vertex_count - 1;
            document.getElementById('max-iterations').value = maxIter;
            
            if (document.getElementById('algo-vertex-count')) {
                document.getElementById('algo-vertex-count').textContent = g.vertex_count;
                document.getElementById('algo-edge-count').textContent = g.edge_count;
                document.getElementById('current-time-complexity').textContent = 
                    `O(${g.vertex_count}×${g.edge_count}) = O(${g.vertex_count * g.edge_count})`;
                document.getElementById('current-space-complexity').textContent = 
                    `O(${g.vertex_count})`;
                document.getElementById('current-graph-complexity').textContent = 
                    `O(${g.vertex_count}+${g.edge_count})`;
            }
        }
    });
}

// Display locations in table
function displayLocationsTable() {
    const tbody = document.getElementById('locations-table-body');
    tbody.innerHTML = '';
    
    app.locations.forEach(loc => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${loc.node_label}</strong></td>
            <td>${loc.name}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteLocation(${loc.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Display edge list
function displayEdgeList() {
    const tbody = document.getElementById('edge-list-body');
    tbody.innerHTML = '';
    
    app.routes.forEach(route => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${route.source_label} → ${route.destination_label}</td>
            <td>₹${route.cost.toFixed(2)}</td>
            <td>${route.distance ? route.distance.toFixed(2) : '-'}</td>
            <td>${route.delivery_time ? route.delivery_time : '-'}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteRoute(${route.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Display adjacency list
function displayAdjacencyList() {
    const display = document.getElementById('adjacency-list-display');
    let text = '';
    
    app.locations.forEach(source => {
        text += source.node_label + ':\n';
        
        const outgoing = app.routes.filter(r => r.source_id === source.id);
        if (outgoing.length === 0) {
            text += '  (no outgoing routes)\n';
        } else {
            outgoing.forEach(route => {
                const destLabel = route.destination_label;
                text += `  → ${destLabel} (₹${route.cost.toFixed(2)})\n`;
            });
        }
        text += '\n';
    });
    
    display.textContent = text || '(No locations)';
}

// Delete location
function deleteLocation(locationId) {
    if (confirm('Delete this location? This will also delete all connected routes.')) {
        fetch(`/api/locations/${locationId}`, { method: 'DELETE' })
            .then(res => {
                if (res.ok) {
                    showNotification('Location deleted', 'success');
                    loadLocations().then(() => loadRoutes()).then(() => {
                        refreshModule1View();
                        updateGraphStats();
                    });
                }
            })
            .catch(error => showNotification('Error deleting location: ' + error, 'danger'));
    }
}

// Delete route
function deleteRoute(routeId) {
    if (confirm('Delete this route?')) {
        fetch(`/api/routes/${routeId}`, { method: 'DELETE' })
            .then(res => {
                if (res.ok) {
                    showNotification('Route deleted', 'success');
                    loadRoutes().then(() => {
                        refreshModule1View();
                        updateGraphStats();
                    });
                }
            })
            .catch(error => showNotification('Error deleting route: ' + error, 'danger'));
    }
}

// Pass graph to algorithm
function passGraphToAlgorithm() {
    const sourceSelect = document.getElementById('source-location');
    if (!sourceSelect.value) {
        showNotification('Please select a source location', 'warning');
        return;
    }
    
    // Update algorithm view with graph data
    updateGraphStats();
    showModule('module2');
    showNotification('Graph passed to Bellman-Ford. Ready to calculate.', 'info');
}
