from database import db
from datetime import datetime
import json

class Location(db.Model):
    """Delivery location model"""
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    node_label = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(500))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    source_routes = db.relationship('Route', foreign_keys='Route.source_id', backref='source_location', cascade='all, delete-orphan')
    dest_routes = db.relationship('Route', foreign_keys='Route.destination_id', backref='destination_location', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'node_label': self.node_label,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Location {self.node_label}: {self.name}>'


class Route(db.Model):
    """Delivery route model"""
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    cost = db.Column(db.Float, nullable=False)  # Delivery cost in rupees
    distance = db.Column(db.Float)  # Distance in km
    delivery_time = db.Column(db.Integer)  # Estimated time in minutes
    geometry = db.Column(db.Text)  # GeoJSON or encoded polyline
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'destination_id': self.destination_id,
            'source_label': self.source_location.node_label if self.source_location else None,
            'destination_label': self.destination_location.node_label if self.destination_location else None,
            'source_name': self.source_location.name if self.source_location else None,
            'destination_name': self.destination_location.name if self.destination_location else None,
            'cost': self.cost,
            'distance': self.distance,
            'delivery_time': self.delivery_time,
            'geometry': self.geometry,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Route {self.source_id} -> {self.destination_id}>'


class Calculation(db.Model):
    """Bellman-Ford calculation record"""
    __tablename__ = 'calculations'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    source_location = db.relationship('Location', foreign_keys=[source_id])
    vertices = db.Column(db.Integer)
    edges = db.Column(db.Integer)
    iterations = db.Column(db.Integer)
    negative_cycle = db.Column(db.Boolean, default=False)
    execution_time_ms = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    steps = db.relationship('CalculationStep', backref='calculation', cascade='all, delete-orphan')
    results = db.relationship('CalculationResult', backref='calculation', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'source_label': self.source_location.node_label if self.source_location else None,
            'vertices': self.vertices,
            'edges': self.edges,
            'iterations': self.iterations,
            'negative_cycle': self.negative_cycle,
            'execution_time_ms': self.execution_time_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CalculationStep(db.Model):
    """Individual relaxation step during Bellman-Ford"""
    __tablename__ = 'calculation_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    calculation_id = db.Column(db.Integer, db.ForeignKey('calculations.id'), nullable=False)
    iteration = db.Column(db.Integer)
    edge_source = db.Column(db.String(10))
    edge_destination = db.Column(db.String(10))
    weight = db.Column(db.Float)
    source_distance = db.Column(db.Float)
    candidate_distance = db.Column(db.Float)
    old_destination_distance = db.Column(db.Float)
    new_destination_distance = db.Column(db.Float)
    updated = db.Column(db.Boolean, default=False)
    predecessor = db.Column(db.String(10))
    
    def to_dict(self):
        return {
            'id': self.id,
            'calculation_id': self.calculation_id,
            'iteration': self.iteration,
            'edge_source': self.edge_source,
            'edge_destination': self.edge_destination,
            'weight': self.weight,
            'source_distance': self.source_distance,
            'candidate_distance': self.candidate_distance,
            'old_destination_distance': self.old_destination_distance,
            'new_destination_distance': self.new_destination_distance,
            'updated': self.updated,
            'predecessor': self.predecessor
        }


class CalculationResult(db.Model):
    """Final result for a destination from Bellman-Ford"""
    __tablename__ = 'calculation_results'
    
    id = db.Column(db.Integer, primary_key=True)
    calculation_id = db.Column(db.Integer, db.ForeignKey('calculations.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    destination_location = db.relationship('Location', foreign_keys=[destination_id])
    minimum_cost = db.Column(db.Float)
    predecessor_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    predecessor_location = db.relationship('Location', foreign_keys=[predecessor_id])
    path_json = db.Column(db.Text)  # JSON array of node labels
    total_distance = db.Column(db.Float)
    total_time = db.Column(db.Integer)
    status = db.Column(db.String(20))  # REACHABLE, UNREACHABLE, AFFECTED_BY_CYCLE
    
    def to_dict(self):
        path = []
        if self.path_json:
            path = json.loads(self.path_json)
        
        return {
            'id': self.id,
            'calculation_id': self.calculation_id,
            'destination_id': self.destination_id,
            'destination_label': self.destination_location.node_label if self.destination_location else None,
            'destination_name': self.destination_location.name if self.destination_location else None,
            'minimum_cost': self.minimum_cost,
            'predecessor_id': self.predecessor_id,
            'predecessor_label': self.predecessor_location.node_label if self.predecessor_location else None,
            'path': path,
            'total_distance': self.total_distance,
            'total_time': self.total_time,
            'status': self.status
        }
