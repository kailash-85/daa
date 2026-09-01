"""
Location API endpoints
"""

from flask import Blueprint, request, jsonify
from database.models import Location, db
from services.geocoding_service import geocoding_service, routing_service
import string

locations_bp = Blueprint('locations', __name__, url_prefix='/api/locations')


def generate_node_label():
    """Generate next available node label (A, B, C, ..., Z, AA, AB, ...)"""
    locations = Location.query.all()
    existing_labels = {loc.node_label for loc in locations}
    
    # Single letters
    for letter in string.ascii_uppercase:
        if letter not in existing_labels:
            return letter
    
    # Double letters
    for first in string.ascii_uppercase:
        for second in string.ascii_uppercase:
            label = first + second
            if label not in existing_labels:
                return label
    
    return f"LOC_{len(locations) + 1}"


@locations_bp.route('', methods=['GET'])
def get_locations():
    """Get all delivery locations"""
    locations = Location.query.all()
    return jsonify([loc.to_dict() for loc in locations])


@locations_bp.route('/<int:location_id>', methods=['GET'])
def get_location(location_id):
    """Get a specific location"""
    location = Location.query.get(location_id)
    
    if not location:
        return jsonify({'error': 'Location not found'}), 404
    
    return jsonify(location.to_dict())


@locations_bp.route('', methods=['POST'])
def create_location():
    """Create a new delivery location"""
    data = request.get_json()
    
    # Validate required fields
    required = ['name', 'latitude', 'longitude']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields: name, latitude, longitude'}), 400
    
    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Latitude and longitude must be numbers'}), 400
    
    # Get address from coordinates if not provided
    address = data.get('address', '')
    if not address:
        result = geocoding_service.reverse_geocode(latitude, longitude)
        address = result.get('address', f'({latitude}, {longitude})')
    
    # Generate node label
    node_label = generate_node_label()
    
    try:
        location = Location(
            node_label=node_label,
            name=data['name'],
            address=address,
            latitude=latitude,
            longitude=longitude
        )
        
        db.session.add(location)
        db.session.commit()
        
        return jsonify({
            'message': 'Location created successfully',
            'location': location.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error creating location: {str(e)}'}), 500


@locations_bp.route('/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    """Update a location"""
    location = Location.query.get(location_id)
    
    if not location:
        return jsonify({'error': 'Location not found'}), 404
    
    data = request.get_json()
    
    try:
        if 'name' in data:
            location.name = data['name']
        if 'address' in data:
            location.address = data['address']
        if 'latitude' in data:
            location.latitude = float(data['latitude'])
        if 'longitude' in data:
            location.longitude = float(data['longitude'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Location updated successfully',
            'location': location.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating location: {str(e)}'}), 500


@locations_bp.route('/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    """Delete a location"""
    location = Location.query.get(location_id)
    
    if not location:
        return jsonify({'error': 'Location not found'}), 404
    
    try:
        db.session.delete(location)
        db.session.commit()
        
        return jsonify({'message': 'Location deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting location: {str(e)}'}), 500


@locations_bp.route('/search', methods=['POST'])
def search_locations():
    """Search for locations by name"""
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # First try to geocode the query
    results = geocoding_service.search_locations(query, limit=5)
    
    return jsonify(results)


@locations_bp.route('/geocode', methods=['POST'])
def geocode_query():
    """Geocode a location query"""
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    result = geocoding_service.geocode_location(query)
    
    return jsonify(result)


@locations_bp.route('/reverse-geocode', methods=['POST'])
def reverse_geocode_coords():
    """Reverse geocode coordinates"""
    data = request.get_json()
    
    try:
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
    except (ValueError, TypeError):
        return jsonify({'error': 'Valid latitude and longitude are required'}), 400
    
    result = geocoding_service.reverse_geocode(latitude, longitude)
    
    return jsonify(result)
