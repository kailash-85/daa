/**
 * Location Management
 */

// Add new location
function addLocation() {
    const name = document.getElementById('location-name').value.trim();
    const address = document.getElementById('location-address').value.trim();
    const lat = parseFloat(document.getElementById('location-lat').value);
    const lon = parseFloat(document.getElementById('location-lon').value);
    
    if (!name || !lat || !lon) {
        showNotification('Please fill in all required fields', 'warning');
        return;
    }
    
    const data = {
        name: name,
        address: address || `${lat}, ${lon}`,
        latitude: lat,
        longitude: lon
    };
    
    fetch('/api/locations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data.location) {
            showNotification('Location added: ' + data.location.node_label, 'success');
            
            // Clear form
            document.getElementById('location-name').value = '';
            document.getElementById('location-address').value = '';
            document.getElementById('location-lat').value = '';
            document.getElementById('location-lon').value = '';
            document.getElementById('location-search').value = '';
            document.getElementById('search-results').innerHTML = '';
            
            // Reload
            loadLocations().then(() => loadRoutes()).then(() => {
                refreshModule1View();
                refreshModule1Map();
                updateGraphStats();
            });
        }
    })
    .catch(error => {
        showNotification('Error adding location: ' + error, 'danger');
    });
}

// Search for location
function searchLocation() {
    const query = document.getElementById('location-search').value.trim();
    
    if (!query) {
        showNotification('Please enter a search query', 'warning');
        return;
    }
    
    fetch('/api/locations/geocode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('location-name').value = data.name || query;
            document.getElementById('location-address').value = data.address || '';
            document.getElementById('location-lat').value = data.latitude.toFixed(6);
            document.getElementById('location-lon').value = data.longitude.toFixed(6);
            
            // Try to get more detailed results
            fetch('/api/locations/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            })
            .then(res => res.json())
            .then(results => {
                displaySearchResults(results);
            });
            
            showNotification('Location found', 'success');
        } else {
            showNotification(data.error || 'Location not found', 'warning');
        }
    })
    .catch(error => {
        showNotification('Error searching location: ' + error, 'danger');
    });
}

// Display search results
function displaySearchResults(results) {
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '';
    
    if (!results || results.length === 0) {
        resultsDiv.innerHTML = '<p class="text-muted">No results found</p>';
        return;
    }
    
    results.forEach(result => {
        const div = document.createElement('div');
        div.className = 'search-result-item';
        div.innerHTML = `
            <div class="search-result-name">${result.name || result.address}</div>
            <div class="search-result-address">${result.address}</div>
            <small class="text-muted">${result.latitude.toFixed(4)}, ${result.longitude.toFixed(4)}</small>
        `;
        
        div.addEventListener('click', () => {
            document.getElementById('location-name').value = result.name || result.address;
            document.getElementById('location-address').value = result.address;
            document.getElementById('location-lat').value = result.latitude.toFixed(6);
            document.getElementById('location-lon').value = result.longitude.toFixed(6);
        });
        
        resultsDiv.appendChild(div);
    });
}
