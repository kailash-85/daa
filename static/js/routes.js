/**
 * Route Management
 */

// Get real route information
function getRealRoute() {
    const sourceId = document.getElementById('route-source').value;
    const destId = document.getElementById('route-destination').value;
    
    if (!sourceId || !destId) {
        showNotification('Please select both source and destination', 'warning');
        return;
    }
    
    if (sourceId === destId) {
        showNotification('Source and destination must be different', 'warning');
        return;
    }
    
    fetch('/api/routes/get-real-route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_id: sourceId, destination_id: destId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('route-distance').textContent = data.distance;
            document.getElementById('route-time').textContent = data.duration;
            document.getElementById('route-info').style.display = 'block';
            
            // If in auto mode, calculate cost
            if (document.getElementById('cost-mode-auto').checked) {
                calculateAutoCost();
            }
            
            showNotification('Real route information obtained', 'success');
        } else {
            showNotification(data.error || 'Could not get route information. Enter manually.', 'warning');
            document.getElementById('route-info').style.display = 'none';
        }
    })
    .catch(error => {
        showNotification('Error getting route: ' + error, 'danger');
    });
}

// Add new route
function addRoute() {
    const sourceId = document.getElementById('route-source').value;
    const destId = document.getElementById('route-destination').value;
    const cost = parseFloat(document.getElementById('route-cost-manual').value);
    
    if (!sourceId || !destId) {
        showNotification('Please select source and destination', 'warning');
        return;
    }
    
    if (sourceId === destId) {
        showNotification('Source and destination must be different', 'warning');
        return;
    }
    
    if (isNaN(cost) || cost < 0) {
        showNotification('Please enter a valid cost', 'warning');
        return;
    }
    
    const distance = document.getElementById('route-distance').textContent;
    const time = document.getElementById('route-time').textContent;
    
    const data = {
        source_id: sourceId,
        destination_id: destId,
        cost: cost,
        distance: distance !== '-' ? parseFloat(distance) : null,
        delivery_time: time !== '-' ? parseInt(time) : null
    };
    
    fetch('/api/routes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data.route) {
            showNotification('Route added', 'success');
            
            // Reset form
            document.getElementById('route-source').value = '';
            document.getElementById('route-destination').value = '';
            document.getElementById('route-cost-manual').value = '';
            document.getElementById('route-distance').textContent = '-';
            document.getElementById('route-time').textContent = '-';
            document.getElementById('route-info').style.display = 'none';
            
            // Reload
            loadRoutes().then(() => {
                refreshModule1View();
                refreshModule1Map();
                updateGraphStats();
            });
        }
    })
    .catch(error => {
        showNotification('Error adding route: ' + error, 'danger');
    });
}
