"""
Route API endpoints
"""

from flask import Blueprint, request, jsonify
from database.models import Location, Route, db
from services.geocoding_service import routing_service
from services.cost_service import calculate_cost

routes_bp = Blueprint('routes', __name__, url_prefix='/api/routes')


@routes_bp.route('', methods=['GET'])
def get_routes():
    """Get all delivery routes"""
    routes = Route.query.all()
    return jsonify([route.to_dict() for route in routes])


@routes_bp.route('/<int:route_id>', methods=['GET'])
def get_route(route_id):
    """Get a specific route"""
    route = Route.query.get(route_id)
    
    if not route:
        return jsonify({'error': 'Route not found'}), 404
    
    return jsonify(route.to_dict())


@routes_bp.route('', methods=['POST'])
def create_route():
    """Create a new delivery route"""
    data = request.get_json()
    
    # Validate required fields
    required = ['source_id', 'destination_id', 'cost']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields: source_id, destination_id, cost'}), 400
    
    try:
        source_id = int(data['source_id'])
        destination_id = int(data['destination_id'])
        cost = float(data['cost'])
    except (ValueError, TypeError):
        return jsonify({'error': 'source_id, destination_id, and cost must be numbers'}), 400
    
    # Verify locations exist
    source = Location.query.get(source_id)
    destination = Location.query.get(destination_id)
    
    if not source or not destination:
        return jsonify({'error': 'Source or destination location not found'}), 404
    
    if source_id == destination_id:
        return jsonify({'error': 'Source and destination must be different'}), 400
    
    # Check if route already exists
    existing = Route.query.filter_by(source_id=source_id, destination_id=destination_id).first()
    if existing:
        return jsonify({'error': 'Route already exists between these locations'}), 400
    
    try:
        # Get route information from routing service
        distance = data.get('distance')
        delivery_time = data.get('delivery_time')
        
        if distance is None or delivery_time is None:
            # Try to get real route information
            result = routing_service.get_route(
                source.latitude, source.longitude,
                destination.latitude, destination.longitude
            )
            
            if result['success']:
                distance = distance or result['distance']
                delivery_time = delivery_time or result['duration']
                geometry = result.get('geometry', '')
            else:
                geometry = None
        else:
            geometry = None
        
        route = Route(
            source_id=source_id,
            destination_id=destination_id,
            cost=cost,
            distance=distance,
            delivery_time=delivery_time,
            geometry=geometry
        )
        
        db.session.add(route)
        db.session.commit()
        
        return jsonify({
            'message': 'Route created successfully',
            'route': route.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error creating route: {str(e)}'}), 500


@routes_bp.route('/<int:route_id>', methods=['PUT'])
def update_route(route_id):
    """Update a route"""
    route = Route.query.get(route_id)
    
    if not route:
        return jsonify({'error': 'Route not found'}), 404
    
    data = request.get_json()
    
    try:
        if 'cost' in data:
            route.cost = float(data['cost'])
        if 'distance' in data and data['distance'] is not None:
            route.distance = float(data['distance'])
        if 'delivery_time' in data and data['delivery_time'] is not None:
            route.delivery_time = int(data['delivery_time'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Route updated successfully',
            'route': route.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating route: {str(e)}'}), 500


@routes_bp.route('/<int:route_id>', methods=['DELETE'])
def delete_route(route_id):
    """Delete a route"""
    route = Route.query.get(route_id)
    
    if not route:
        return jsonify({'error': 'Route not found'}), 404
    
    try:
        db.session.delete(route)
        db.session.commit()
        
        return jsonify({'message': 'Route deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting route: {str(e)}'}), 500


@routes_bp.route('/get-real-route', methods=['POST'])
def get_real_route():
    """Get real route information between two locations"""
    data = request.get_json()
    
    try:
        source_id = int(data['source_id'])
        destination_id = int(data['destination_id'])
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'source_id and destination_id are required'}), 400
    
    source = Location.query.get(source_id)
    destination = Location.query.get(destination_id)
    
    if not source or not destination:
        return jsonify({'error': 'Location not found'}), 404
    
    result = routing_service.get_route(
        source.latitude, source.longitude,
        destination.latitude, destination.longitude
    )
    
    return jsonify(result)


@routes_bp.route('/calculate-cost', methods=['POST'])
def calculate_route_cost():
    """Calculate delivery cost for a route"""
    data = request.get_json()
    
    try:
        distance = float(data.get('distance', 0))
        time = float(data.get('delivery_time', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'distance and delivery_time must be numbers'}), 400
    
    base_charge = float(data.get('base_charge', 50))
    cost_per_km = float(data.get('cost_per_km', 10))
    cost_per_minute = float(data.get('cost_per_minute', 2))
    
    result = calculate_cost(distance, time, base_charge, cost_per_km, cost_per_minute)
    
    return jsonify(result)
