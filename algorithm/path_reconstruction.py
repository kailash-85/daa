"""
Path reconstruction and analysis utilities for Bellman-Ford results.
"""


def reconstruct_path(destination, predecessors, source):
    """
    Reconstruct path from source to destination using predecessor map.
    
    Args:
        destination: Target vertex
        predecessors: Dict mapping vertex to its predecessor
        source: Source vertex
    
    Returns:
        list: Path from source to destination, or None if unreachable
    """
    if destination not in predecessors:
        return None
    
    path = []
    current = destination
    
    while current is not None:
        path.append(current)
        current = predecessors.get(current)
    
    path.reverse()
    
    if path and path[0] == source:
        return path
    return None


def calculate_path_cost_breakdown(path, routes_dict):
    """
    Calculate cost breakdown for a given path.
    
    Args:
        path: List of vertices [A, B, C, D]
        routes_dict: Dict mapping (source, dest) -> route data
    
    Returns:
        dict: Breakdown of costs per edge
    """
    breakdown = []
    total_cost = 0
    total_distance = 0
    total_time = 0
    
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        
        route_key = (u, v)
        if route_key in routes_dict:
            route = routes_dict[route_key]
            breakdown.append({
                'from': u,
                'to': v,
                'cost': route.get('cost', 0),
                'distance': route.get('distance', 0),
                'time': route.get('time', 0)
            })
            total_cost += route.get('cost', 0)
            total_distance += route.get('distance', 0)
            total_time += route.get('time', 0)
    
    return {
        'path': path,
        'breakdown': breakdown,
        'total_cost': total_cost,
        'total_distance': total_distance,
        'total_time': total_time
    }


def get_reachable_vertices(distances):
    """Get list of reachable vertices (distance != inf)"""
    return [v for v, d in distances.items() if d != float('inf')]


def get_unreachable_vertices(distances):
    """Get list of unreachable vertices (distance == inf)"""
    return [v for v, d in distances.items() if d == float('inf')]


def analyze_cost_distribution(results):
    """
    Analyze cost distribution from calculation results.
    
    Args:
        results: List of CalculationResult objects
    
    Returns:
        dict: Cost distribution analysis
    """
    costs = [r.minimum_cost for r in results if r.status == 'REACHABLE' and r.minimum_cost is not None]
    
    if not costs:
        return {
            'min': None,
            'max': None,
            'avg': None,
            'total': None,
            'count': 0
        }
    
    return {
        'min': min(costs),
        'max': max(costs),
        'avg': sum(costs) / len(costs),
        'total': sum(costs),
        'count': len(costs)
    }


def categorize_costs(results, ranges=None):
    """
    Categorize costs into ranges.
    
    Args:
        results: List of CalculationResult objects
        ranges: List of tuples [(min, max), ...] or None for auto-generation
    
    Returns:
        dict: Cost categories with counts and percentages
    """
    if ranges is None:
        ranges = [(0, 100), (101, 200), (201, 300), (301, 500), (501, float('inf'))]
    
    categories = {}
    for min_val, max_val in ranges:
        key = f'₹{min_val}–₹{max_val}' if max_val != float('inf') else f'₹{min_val}+'
        categories[key] = {'count': 0, 'percentage': 0, 'destinations': []}
    
    reachable = [r for r in results if r.status == 'REACHABLE' and r.minimum_cost is not None]
    
    for result in reachable:
        cost = result.minimum_cost
        dest = result.destination_location.node_label if result.destination_location else 'Unknown'
        
        for (min_val, max_val), key in zip(ranges, categories.keys()):
            if min_val <= cost <= max_val:
                categories[key]['count'] += 1
                categories[key]['destinations'].append({
                    'label': dest,
                    'cost': cost
                })
                break
    
    # Calculate percentages
    total = len(reachable)
    if total > 0:
        for key in categories:
            categories[key]['percentage'] = round((categories[key]['count'] / total) * 100, 2)
    
    return categories
