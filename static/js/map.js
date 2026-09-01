/**
 * Map Management using Leaflet
 */

// Default map center (Chennai, India)
const DEFAULT_MAP_CENTER = [13.1939, 80.2740];
const DEFAULT_MAP_ZOOM = 13;

let mapMarkers = {
    overview: [],
    module1: [],
    module3: []
};

let mapPolylines = {
    overview: [],
    module1: [],
    module3: []
};

// Initialize all maps
function initMaps() {
    initMap('overview-map', 'overview');
    initMap('module1-map', 'module1');
    initMap('module3-map', 'module3');
}

// Initialize a specific map
function initMap(elementId, mapName) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const map = L.map(elementId).setView(DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    app.maps[mapName] = map;
    mapMarkers[mapName] = [];
    mapPolylines[mapName] = [];
}

// Add location to map
function addLocationMarker(location, mapName) {
    if (!app.maps[mapName]) return;
    
    const marker = L.marker([location.latitude, location.longitude], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        }),
        title: location.name
    }).bindPopup(`
        <div>
            <strong>${location.node_label}: ${location.name}</strong><br>
            ${location.address}<br>
            <small>${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}</small>
        </div>
    `).addTo(app.maps[mapName]);
    
    mapMarkers[mapName].push(marker);
    return marker;
}

// Draw route between two locations
function drawRoute(source, destination, mapName, color = '#3498db', weight = 2) {
    if (!app.maps[mapName]) return;
    
    const polyline = L.polyline(
        [[source.latitude, source.longitude], [destination.latitude, destination.longitude]],
        {
            color: color,
            weight: weight,
            opacity: 0.8,
            smoothFactor: 1
        }
    ).bindPopup(`
        <div>
            <strong>${source.node_label} → ${destination.node_label}</strong><br>
            Cost: ₹${source._route_cost || '-'}<br>
            Distance: ${source._route_distance || '-'} km
        </div>
    `).addTo(app.maps[mapName]);
    
    mapPolylines[mapName].push(polyline);
    return polyline;
}

// Clear all markers from map
function clearMapMarkers(mapName) {
    mapMarkers[mapName].forEach(marker => {
        app.maps[mapName].removeLayer(marker);
    });
    mapMarkers[mapName] = [];
}

// Clear all polylines from map
function clearMapPolylines(mapName) {
    mapPolylines[mapName].forEach(polyline => {
        app.maps[mapName].removeLayer(polyline);
    });
    mapPolylines[mapName] = [];
}

// Refresh module 1 map
function refreshModule1Map() {
    if (!app.maps.module1) return;
    
    clearMapMarkers('module1');
    clearMapPolylines('module1');
    
    // Add location markers
    app.locations.forEach(loc => {
        addLocationMarker(loc, 'module1');
    });
    
    // Add route polylines
    app.routes.forEach(route => {
        const source = app.locations.find(l => l.id === route.source_id);
        const dest = app.locations.find(l => l.id === route.destination_id);
        
        if (source && dest) {
            drawRoute(source, dest, 'module1', '#3498db', 2);
        }
    });
    
    // Fit bounds
    if (mapMarkers.module1.length > 0) {
        const group = new L.featureGroup(mapMarkers.module1);
        app.maps.module1.fitBounds(group.getBounds().pad(0.1));
    }
}

// Get current location
function getCurrentLocation() {
    if (!navigator.geolocation) {
        showNotification('Geolocation is not supported by your browser', 'danger');
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        position => {
            const { latitude, longitude } = position.coords;
            document.getElementById('location-lat').value = latitude.toFixed(6);
            document.getElementById('location-lon').value = longitude.toFixed(6);
            
            // Reverse geocode
            fetch('/api/locations/reverse-geocode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ latitude, longitude })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('location-address').value = data.address;
                    if (!document.getElementById('location-name').value) {
                        document.getElementById('location-name').value = 'Current Location';
                    }
                }
            });
            
            showNotification('Current location obtained', 'success');
        },
        error => {
            let message = 'Unable to get your location. ';
            if (error.code === error.PERMISSION_DENIED) {
                message += 'Location access was denied.';
            } else if (error.code === error.POSITION_UNAVAILABLE) {
                message += 'Location information is unavailable.';
            } else if (error.code === error.TIMEOUT) {
                message += 'The request to get user location timed out.';
            }
            showNotification(message, 'danger');
        }
    );
}

// Highlight best path on map
function highlightBestPath(path, mapName) {
    if (!app.maps[mapName] || !path || path.length < 2) return;
    
    const bounds = [];
    
    for (let i = 0; i < path.length - 1; i++) {
        const sourceLoc = app.locations.find(l => l.node_label === path[i]);
        const destLoc = app.locations.find(l => l.node_label === path[i + 1]);
        
        if (sourceLoc && destLoc) {
            drawRoute(sourceLoc, destLoc, mapName, '#27ae60', 4);
            bounds.push([sourceLoc.latitude, sourceLoc.longitude]);
            bounds.push([destLoc.latitude, destLoc.longitude]);
        }
    }
    
    if (bounds.length > 0) {
        app.maps[mapName].fitBounds(bounds);
    }
}

// Display all routes on map
function displayAllRoutesOnMap(mapName) {
    if (!app.maps[mapName]) return;
    
    clearMapMarkers(mapName);
    clearMapPolylines(mapName);
    
    app.locations.forEach(loc => {
        addLocationMarker(loc, mapName);
    });
    
    app.routes.forEach(route => {
        const source = app.locations.find(l => l.id === route.source_id);
        const dest = app.locations.find(l => l.id === route.destination_id);
        
        if (source && dest) {
            drawRoute(source, dest, mapName, '#3498db', 2);
        }
    });
    
    if (mapMarkers[mapName].length > 0) {
        const group = new L.featureGroup(mapMarkers[mapName]);
        app.maps[mapName].fitBounds(group.getBounds().pad(0.1));
    }
}
