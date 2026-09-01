"""
Real-Time Delivery Cost Calculator using Bellman-Ford Algorithm
A professional logistics web application for minimum-cost route optimization and analysis.

Author: Capstone Project Student
Date: 2024
"""

from flask import Flask, render_template, jsonify
from config import config
from database import db, init_db
from api.location_api import locations_bp
from api.route_api import routes_bp
from api.calculation_api import graph_bp, calc_bp
from database.models import Location, Route
import os


def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    app.register_blueprint(locations_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(graph_bp)
    app.register_blueprint(calc_bp)
    
    # Routes
    @app.route('/')
    def index():
        """Render main application"""
        return render_template('index.html')
    
    @app.route('/module1')
    def module1():
        """Network modeling module"""
        return render_template('index.html', module='module1')
    
    @app.route('/module2')
    def module2():
        """Bellman-Ford calculation engine"""
        return render_template('index.html', module='module2')
    
    @app.route('/module3')
    def module3():
        """Cost analysis dashboard"""
        return render_template('index.html', module='module3')
    
    @app.route('/health')
    def health():
        """Health check"""
        return jsonify({'status': 'ok', 'version': '1.0.0'})
    
    @app.route('/init-demo-data', methods=['POST'])
    def init_demo_data():
        """Initialize demo data for testing"""
        try:
            # Check if data already exists
            if Location.query.first():
                return jsonify({'message': 'Demo data already exists'}), 200
            
            # Create demo locations
            demo_locations = [
                {'node': 'A', 'name': 'Warehouse', 'lat': 13.1939, 'lon': 80.2740, 'address': 'Chennai Warehouse'},
                {'node': 'B', 'name': 'Shop 1', 'lat': 13.1891, 'lon': 80.2710, 'address': 'Anna Salai'},
                {'node': 'C', 'name': 'Shop 2', 'lat': 13.1913, 'lon': 80.2738, 'address': 'Teynampet'},
                {'node': 'D', 'name': 'Customer 1', 'lat': 13.1949, 'lon': 80.2750, 'address': 'Alwarpet'},
                {'node': 'E', 'name': 'Customer 2', 'lat': 13.1969, 'lon': 80.2760, 'address': 'Mylapore'},
            ]
            
            locations_dict = {}
            for loc_data in demo_locations:
                loc = Location(
                    node_label=loc_data['node'],
                    name=loc_data['name'],
                    address=loc_data['address'],
                    latitude=loc_data['lat'],
                    longitude=loc_data['lon']
                )
                db.session.add(loc)
                locations_dict[loc_data['node']] = loc
            
            db.session.flush()
            
            # Create demo routes
            demo_routes = [
                ('A', 'B', 4, 2.1, 15),
                ('A', 'C', 5, 2.5, 18),
                ('A', 'D', 7, 3.5, 25),
                ('B', 'C', 2, 1.2, 8),
                ('B', 'D', 3, 1.8, 12),
                ('C', 'D', 1, 0.8, 5),
                ('C', 'E', 4, 2.0, 14),
                ('D', 'E', 2, 1.2, 9),
            ]
            
            for source, dest, cost, distance, time in demo_routes:
                route = Route(
                    source_id=locations_dict[source].id,
                    destination_id=locations_dict[dest].id,
                    cost=cost,
                    distance=distance,
                    delivery_time=time
                )
                db.session.add(route)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Demo data initialized successfully',
                'locations': len(demo_locations),
                'routes': len(demo_routes)
            }), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error initializing demo data: {str(e)}'}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors"""
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(debug=True, host='0.0.0.0', port=5000)
