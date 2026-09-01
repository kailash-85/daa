/**
 * Bellman-Ford Algorithm UI and Execution
 */

// Run Bellman-Ford algorithm
async function runBellmanFord() {
    const sourceSelect = document.getElementById('source-location');
    const sourceId = sourceSelect.value;
    
    if (!sourceId) {
        showNotification('Please select a source location', 'warning');
        return;
    }
    
    const sourceLabel = sourceSelect.options[sourceSelect.selectedIndex].dataset.label;
    
    // Disable button
    const btn = event.target;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Running...';
    
    try {
        const response = await fetch('/api/calculations/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source: sourceLabel })
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const result = await response.json();
        app.currentCalculation = result;
        
        // Display results
        displayInitializationTable(result);
        displayRelaxationLog(result);
        displayFinalDistances(result);
        displayComplexityAnalysis(result);
        
        // Display detailed table
        displayDetailedRelaxationTable(result);
        
        // Update destination select
        updateDestinationSelect(result);
        
        // Show negative cycle warning if needed
        if (result.negative_cycle) {
            document.getElementById('negative-cycle-alert').style.display = 'block';
            document.getElementById('negative-cycle-status').textContent = 'YES - DETECTED';
            document.getElementById('negative-cycle-status').className = 'text-danger';
        } else {
            document.getElementById('negative-cycle-alert').style.display = 'none';
            document.getElementById('negative-cycle-status').textContent = 'No';
        }
        
        // Update metrics
        document.getElementById('execution-time').textContent = result.execution_time_ms.toFixed(2) + ' ms';
        document.getElementById('iterations-performed').textContent = result.iterations;
        document.getElementById('relaxations-count').textContent = result.relaxations;
        document.getElementById('algo-source-label').textContent = result.source;
        
        showNotification('Bellman-Ford calculation completed', 'success');
        
    } catch (error) {
        showNotification('Error running algorithm: ' + error, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play"></i> RUN BELLMAN-FORD';
    }
}

// Display initialization table
function displayInitializationTable(result) {
    const tbody = document.getElementById('init-table-body');
    tbody.innerHTML = '';
    
    const vertices = result.distances;
    for (const vertex in vertices) {
        const distance = vertices[vertex];
        const predecessor = result.predecessors[vertex] || '-';
        
        const tr = document.createElement('tr');
        const displayDist = distance === null || distance === Infinity ? '∞' : distance.toFixed(2);
        tr.innerHTML = `
            <td><strong>${vertex}</strong></td>
            <td>${displayDist}</td>
            <td>${predecessor}</td>
        `;
        tbody.appendChild(tr);
    }
}

// Display relaxation log
function displayRelaxationLog(result) {
    const logDiv = document.getElementById('relaxation-log');
    logDiv.innerHTML = '';
    
    let relaxationCount = 0;
    let totalSteps = result.steps.length;
    
    result.steps.forEach((step, index) => {
        if (step.type === 'initialization') {
            const div = document.createElement('div');
            div.className = 'relaxation-step';
            div.innerHTML = `
                <strong>Step 0: ${step.message}</strong>
            `;
            logDiv.appendChild(div);
        } else if (step.type === 'edge_relaxation') {
            relaxationCount++;
            const div = document.createElement('div');
            div.className = 'relaxation-step updated';
            div.innerHTML = `
                <strong>Iter ${step.iteration}:</strong> ${step.edge}<br>
                <small>dist[${step.edge.split('→')[1].trim()}] = ${step.source_distance} + ${step.weight} = ${step.new_destination_distance}</small>
            `;
            logDiv.appendChild(div);
        } else if (step.type === 'early_termination') {
            const div = document.createElement('div');
            div.className = 'relaxation-step';
            div.innerHTML = `<strong>✓ ${step.message}</strong>`;
            logDiv.appendChild(div);
        } else if (step.type === 'negative_cycle_detection') {
            const div = document.createElement('div');
            div.className = 'relaxation-step';
            div.innerHTML = `<strong>⚠ ${step.message}</strong>`;
            logDiv.appendChild(div);
        }
    });
    
    document.getElementById('relaxation-progress').textContent = relaxationCount + ' relaxations';
}

// Display final distances
function displayFinalDistances(result) {
    const tbody = document.getElementById('final-distances-body');
    tbody.innerHTML = '';
    
    // Get results
    fetch(`/api/calculations/${result.calculation_id}/results`)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (!data.results || !Array.isArray(data.results)) {
                console.error('Invalid results structure:', data);
                return;
            }
            
            data.results.forEach(res => {
                const tr = document.createElement('tr');
                const costDisplay = res.minimum_cost !== null ? '₹' + res.minimum_cost.toFixed(2) : '∞';
                const statusClass = res.status === 'REACHABLE' ? 'text-success' : 'text-danger';
                
                tr.innerHTML = `
                    <td><strong>${res.destination_label}</strong></td>
                    <td>${costDisplay}</td>
                    <td><span class="${statusClass}">${res.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Error displaying final distances:', error);
            tbody.innerHTML = `<tr><td colspan="3" class="text-danger">Error loading results</td></tr>`;
        });
}

// Display detailed relaxation table
function displayDetailedRelaxationTable(result) {
    const tbody = document.getElementById('detailed-table-body');
    tbody.innerHTML = '';
    
    result.steps.forEach(step => {
        if (step.type === 'edge_relaxation') {
            const tr = document.createElement('tr');
            const updatedClass = step.updated ? 'table-success' : 'table-light';
            const srcDist = step.source_distance === Infinity ? '∞' : step.source_distance.toFixed(2);
            const oldDist = step.old_destination_distance === Infinity ? '∞' : step.old_destination_distance.toFixed(2);
            const newDist = step.new_destination_distance === Infinity ? '∞' : step.new_destination_distance.toFixed(2);
            
            tr.className = updatedClass;
            tr.innerHTML = `
                <td>${step.iteration}</td>
                <td>${step.edge}</td>
                <td>${step.weight.toFixed(2)}</td>
                <td>${srcDist}</td>
                <td>${step.candidate.toFixed(2)}</td>
                <td>${oldDist}</td>
                <td>${newDist}</td>
                <td><span class="${step.updated ? 'badge bg-success' : 'badge bg-secondary'}">${step.updated ? 'YES' : 'NO'}</span></td>
                <td>${step.predecessor || '-'}</td>
            `;
            tbody.appendChild(tr);
        }
    });
}

// Update destination select
function updateDestinationSelect(result) {
    const select = document.getElementById('destination-select');
    select.innerHTML = '<option value="">-- Select Destination --</option>';
    
    for (const vertex in result.distances) {
        if (vertex !== result.source) {
            const option = document.createElement('option');
            option.value = vertex;
            option.textContent = vertex;
            select.appendChild(option);
        }
    }
}

// Show best path to selected destination
function showBestPath() {
    if (!app.currentCalculation) {
        showNotification('Run algorithm first', 'warning');
        return;
    }
    
    const destinationSelect = document.getElementById('destination-select');
    const destination = destinationSelect.value;
    
    if (!destination) {
        document.getElementById('best-path-display').innerHTML = '<div class="text-center text-muted">-</div>';
        return;
    }
    
    const path = app.currentCalculation.paths[destination];
    const cost = app.currentCalculation.distances[destination];
    
    if (!path) {
        document.getElementById('best-path-display').innerHTML = 
            `<div class="text-danger"><strong>Unreachable</strong></div>`;
        return;
    }
    
    // Build path display
    let html = '<div class="path-display">';
    
    // Path
    html += '<div class="mb-3">';
    path.forEach((node, idx) => {
        html += `<span class="path-step">${node}</span>`;
        if (idx < path.length - 1) {
            html += '<span class="path-arrow">→</span>';
        }
    });
    html += '</div>';
    
    // Cost info
    html += `<div class="alert alert-info py-2 px-3">
        <strong>Minimum Cost: ₹${cost.toFixed(2)}</strong>
    </div>`;
    
    // Cost breakdown
    html += '<div class="cost-breakdown">';
    html += '<strong>Cost Breakdown:</strong>';
    
    let totalDistance = 0;
    let totalTime = 0;
    
    for (let i = 0; i < path.length - 1; i++) {
        const u = path[i];
        const v = path[i + 1];
        
        const route = app.routes.find(r => 
            r.source_label === u && r.destination_label === v
        );
        
        if (route) {
            html += `<div class="cost-item">
                <span class="cost-item-label">${u} → ${v}</span>
                <span class="cost-item-value">₹${route.cost.toFixed(2)}</span>
            </div>`;
            
            if (route.distance) totalDistance += route.distance;
            if (route.delivery_time) totalTime += route.delivery_time;
        }
    }
    
    html += `<div class="cost-item" style="border-top: 1px solid #ccc; margin-top: 8px; padding-top: 8px;">
        <span class="cost-item-label"><strong>Total Distance</strong></span>
        <span class="cost-item-value">${totalDistance.toFixed(2)} km</span>
    </div>`;
    
    html += `<div class="cost-item">
        <span class="cost-item-label"><strong>Total Time</strong></span>
        <span class="cost-item-value">${totalTime} min</span>
    </div>`;
    
    html += '</div>';
    html += '</div>';
    
    document.getElementById('best-path-display').innerHTML = html;
    
    // Highlight on map
    clearMapPolylines('module3');
    highlightBestPath(path, 'module3');
}

// Display complexity analysis
function displayComplexityAnalysis(result) {
    const V = result.vertices;
    const E = result.edges;
    
    document.getElementById('current-time-complexity').textContent = 
        `O(${V}×${E}) = O(${V * E})`;
    document.getElementById('current-space-complexity').textContent = 
        `O(${V})`;
    document.getElementById('current-graph-complexity').textContent = 
        `O(${V}+${E})`;
}

// Reset calculation
function resetCalculation() {
    fetch('/api/calculations/reset', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            app.currentCalculation = null;
            
            document.getElementById('init-table-body').innerHTML = '';
            document.getElementById('relaxation-log').innerHTML = 
                '<div class="text-center text-muted p-4">No calculation yet</div>';
            document.getElementById('final-distances-body').innerHTML = '';
            document.getElementById('detailed-table-body').innerHTML = '';
            document.getElementById('best-path-display').innerHTML = '-';
            document.getElementById('negative-cycle-alert').style.display = 'none';
            
            showNotification('Calculation reset', 'info');
        });
}
