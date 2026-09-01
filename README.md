# Real-Time Delivery Cost Calculator using Bellman-Ford Algorithm

A professional logistics web application for minimum-cost delivery route optimization and analysis using the Bellman-Ford shortest path algorithm.

## Project Overview

This capstone project implements a complete delivery network optimization system with real location data, interactive mapping, and detailed Bellman-Ford algorithm visualization.

**Problem Statement:**  
Design and implement a system to find minimum-cost delivery routes in a delivery network represented as a weighted directed graph using the Bellman-Ford algorithm.

**Key Features:**
- Real delivery location management with geolocation support
- Weighted directed graph construction and visualization
- Custom Bellman-Ford algorithm implementation with step-by-step execution logging
- Detailed algorithm visualization showing every relaxation step
- Negative cycle detection
- Cost analysis dashboard with dynamic charts
- Interactive map with real route information
- Professional UI with three distinct modules

## Architecture Overview

### Module 1: Delivery Network Modeling
- Add/manage delivery locations with real coordinates
- Create directed delivery routes with cost, distance, and time
- Display graph as edge list and adjacency list
- Interactive map visualization
- Graph statistics

### Module 2: Bellman-Ford Cost Calculation Engine
- Execute Bellman-Ford algorithm step-by-step
- Initialize distances and predecessors
- Perform V-1 relaxation iterations
- Detect negative-weight cycles
- Reconstruct best paths with cost breakdown
- Display detailed execution log and relaxation table
- Early termination detection
- Complexity analysis

### Module 3: Cost Analysis Dashboard
- Summarize calculation results
- Visualize minimum costs with bar charts
- Analyze cost distribution with pie charts
- Display best routes to all destinations
- Interactive map highlighting optimal paths
- Cost statistics and distribution ranges

## Technology Stack

### Backend
- **Framework:** Flask 2.3.3
- **Database:** SQLite with SQLAlchemy ORM
- **Language:** Python 3.11+
- **Geocoding:** Geopy (Nominatim/OpenStreetMap)
- **Routing:** OSRM (Open Source Routing Machine)

### Frontend
- **Markup:** HTML5
- **Styling:** CSS3, Bootstrap 5
- **Scripting:** Vanilla JavaScript
- **Maps:** Leaflet.js with OpenStreetMap
- **Charts:** Chart.js 4

### Algorithm
- **Implementation:** Custom Python Bellman-Ford
- **Time Complexity:** O(VE)
- **Space Complexity:** O(V)
- **Graph Storage:** O(V+E)

## Installation

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Modern web browser
- Internet connection (for geocoding/routing services)

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd finalimpl
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file**
   ```bash
   cp .env.example .env
   ```

5. **Initialize database**
   ```bash
   python app.py
   # Database will be created automatically
   ```

6. **Start the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open http://localhost:5000 in your web browser

## Usage Guide

### Getting Started

1. **Initialize Demo Data:** Click "Demo" in navbar to load sample locations and routes
2. **Navigate Modules:** Use navbar to switch between Overview, Network Modeling, Algorithm, and Dashboard

### Module 1: Building Your Network

1. **Add Locations:**
   - Enter location name and search
   - Use "Use Current Location" to add your current position
   - Coordinates auto-populate from search results
   - Click "Add Location" to create node

2. **Create Routes:**
   - Select source and destination locations
   - Click "Get Real Route" to fetch real distance/time (optional)
   - Choose cost entry mode:
     - **Manual:** Enter cost directly
     - **Auto:** System calculates cost from distance and time
   - Adjust cost parameters if using auto mode
   - Click "Add Route" to create directed edge

3. **View Graph:**
   - Edge List shows all directed routes with costs
   - Adjacency List displays outgoing edges per vertex
   - Graph Statistics show V, E, and total cost
   - Interactive map shows location markers

### Module 2: Running Bellman-Ford

1. **Select Source:**
   - Choose source location from dropdown in Module 1
   - Click "Pass to Bellman-Ford"

2. **Execute Algorithm:**
   - Click "RUN BELLMAN-FORD"
   - Watch initialization step setup distances and predecessors
   - View relaxation log showing edge updates
   - Monitor final distances table

3. **Analyze Results:**
   - Check iteration count and relaxation count
   - Review negative cycle detection status
   - Select destination to see best path
   - View cost breakdown per route segment
   - Check complexity metrics

4. **Detailed Examination:**
   - Scroll to see Detailed Relaxation Table
   - Each row shows:
     - Iteration number
     - Edge being relaxed
     - Weight calculation
     - Old vs new distance
     - Whether distance was updated

### Module 3: Cost Analysis

1. **View Dashboard:**
   - Summary cards show network metrics
   - Cost distribution table shows ranges
   - Map highlights all delivery locations and routes

2. **Analyze Charts:**
   - **Bar Chart:** Minimum cost to each destination
   - **Pie Chart:** Cost distribution across ranges

3. **Best Routes Table:**
   - View optimal path to each destination
   - See total cost, distance, and time
   - Click "View" to highlight path on map

## Database Schema

### Locations Table
```sql
- id (Primary Key)
- node_label (Unique: A, B, C, ...)
- name
- address
- latitude, longitude
- created_at
```

### Routes Table
```sql
- id (Primary Key)
- source_id (Foreign Key → locations)
- destination_id (Foreign Key → locations)
- cost (Delivery cost in ₹)
- distance (in km)
- delivery_time (in minutes)
- geometry (GeoJSON/polyline)
- created_at
```

### Calculations Table
```sql
- id (Primary Key)
- source_id (Foreign Key → locations)
- vertices, edges (Graph dimensions)
- iterations (Actual iterations performed)
- negative_cycle (Boolean)
- execution_time_ms
- created_at
```

### Calculation Results Table
```sql
- id (Primary Key)
- calculation_id (Foreign Key)
- destination_id (Foreign Key)
- minimum_cost
- predecessor_id (Foreign Key)
- path_json (Array of node labels)
- total_distance, total_time
- status (REACHABLE, UNREACHABLE, AFFECTED_BY_CYCLE)
```

## Bellman-Ford Algorithm

### Implementation Details

The algorithm implementation (`algorithm/bellman_ford.py`) includes:

1. **Initialization Phase**
   - Set distance[source] = 0
   - Set distance[all others] = ∞
   - Set all predecessors = None

2. **Relaxation Phase** (V-1 iterations)
   - For each iteration, relax every edge
   - If dist[u] + weight < dist[v]:
     - Update dist[v]
     - Update predecessor[v]
     - Record the update

3. **Early Termination**
   - If no distances changed in an iteration
   - Terminate early (optimization)

4. **Negative Cycle Detection**
   - After V-1 iterations, attempt one more relaxation
   - If improvement still possible, negative cycle exists

5. **Path Reconstruction**
   - Follow predecessors from destination to source
   - Reverse to get path from source to destination

### Complexity Analysis

**Time Complexity: O(VE)**
- V-1 iterations
- Each iteration examines E edges
- Total: (V-1) × E = O(VE)

**Space Complexity: O(V)**
- Distance array: O(V)
- Predecessor array: O(V)
- Algorithm auxiliary space: O(V)

**Graph Storage: O(V+E)**
- V vertices in adjacency list
- E edges in adjacency list

## API Endpoints

### Locations
- `GET /api/locations` - List all locations
- `POST /api/locations` - Create location
- `DELETE /api/locations/<id>` - Delete location
- `POST /api/locations/geocode` - Geocode location query
- `POST /api/locations/reverse-geocode` - Reverse geocode coordinates

### Routes
- `GET /api/routes` - List all routes
- `POST /api/routes` - Create route
- `DELETE /api/routes/<id>` - Delete route
- `POST /api/routes/get-real-route` - Get real routing info
- `POST /api/routes/calculate-cost` - Calculate delivery cost

### Graph & Calculations
- `GET /api/graph` - Get current graph structure
- `POST /api/calculations/calculate` - Execute Bellman-Ford
- `GET /api/calculations/<id>` - Get calculation details
- `GET /api/calculations/<id>/results` - Get calculation results

## Testing

### Run Tests
```bash
python -m pytest tests/ -v
```

### Test Coverage
- Bellman-Ford algorithm correctness
- Graph representation
- Path reconstruction
- Negative cycle detection
- API endpoints
- Database operations

## Demonstration/Viva Preparation

### Quick Demo Flow
1. Load demo data (navbar "Demo" button)
2. Navigate to Module 1 to show network building
3. Go to Module 2 and run Bellman-Ford
4. Show step-by-step relaxation process
5. Display final costs and best paths
6. Go to Module 3 to show analysis dashboard
7. Highlight specific route on interactive map

### Key Points to Explain
- Graph as weighted directed edges
- Edge weight represents delivery cost
- Bellman-Ford finds minimum cost paths
- Algorithm correctness with V-1 iterations
- Negative cycle implications
- Complexity trade-offs
- Real location and routing integration

## Files and Structure

```
delivery-cost-calculator/
├── app.py                          # Flask application entry point
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .env.example                    # Environment variables template
│
├── database/
│   ├── __init__.py                # Database initialization
│   └── models.py                  # SQLAlchemy models
│
├── algorithm/
│   ├── __init__.py
│   ├── bellman_ford.py            # Bellman-Ford implementation
│   └── path_reconstruction.py     # Path utilities
│
├── services/
│   ├── __init__.py
│   ├── geocoding_service.py       # Location and routing services
│   └── cost_service.py            # Cost calculation service
│
├── api/
│   ├── __init__.py
│   ├── location_api.py            # Location endpoints
│   ├── route_api.py               # Route endpoints
│   └── calculation_api.py         # Graph and calculation endpoints
│
├── templates/
│   └── index.html                 # Single-page application
│
├── static/
│   ├── css/
│   │   └── style.css             # Application styling
│   │
│   └── js/
│       ├── app.js                # Main application logic
│       ├── map.js                # Leaflet map management
│       ├── locations.js          # Location UI
│       ├── routes.js             # Route UI
│       ├── bellman-ford.js       # Algorithm execution UI
│       ├── dashboard.js          # Dashboard management
│       └── charts.js             # Chart configuration
│
└── tests/
    ├── test_bellman_ford.py
    ├── test_locations.py
    ├── test_routes.py
    └── test_api.py
```

## Known Limitations

- Geolocation requires permission and internet connection
- OSRM routing service may not be available in all regions
- Supports up to ~50 locations and ~200 routes for optimal performance
- Real route info requires external service availability

## Future Enhancements

- Multi-depot vehicle routing
- Time window constraints
- Vehicle capacity constraints
- Real-time traffic integration
- Export results as PDF/Excel
- Batch operations
- Advanced filtering and search
- Persistent route history
- Mobile app
- Docker containerization

## Troubleshooting

### Application won't start
- Check Python 3.11+ is installed
- Verify all dependencies: `pip install -r requirements.txt`
- Check database file permissions
- Review error logs

### Location search not working
- Ensure internet connection
- Check if Nominatim service is available
- Try different search terms

### Map not displaying
- Verify browser JavaScript is enabled
- Check Leaflet CSS/JS are loading
- Check OpenStreetMap is accessible

### Routing returns no results
- Check location coordinates are in service area
- Verify OSRM service is available
- Try entering distance/time manually

## Credits

**Project Type:** Design and Analysis of Algorithms Capstone  
**Algorithms:** Bellman-Ford Shortest Path  
**Time Complexity:** O(VE)  
**Space Complexity:** O(V)

## License

Educational project - Use for learning and evaluation purposes.

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Status:** Production Ready
