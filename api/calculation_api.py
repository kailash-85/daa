"""
Graph and calculation API endpoints
"""

from flask import Blueprint, request, jsonify
from database.models import Location, Route, Calculation, CalculationStep, CalculationResult, db
from algorithm.bellman_ford import bellman_ford
from algorithm.path_reconstruction import reconstruct_path, calculate_path_cost_breakdown, categorize_costs
import json
import time

graph_bp = Blueprint('graph', __name__, url_prefix='/api/graph')
calc_bp = Blueprint('calculations', __name__, url_prefix='/api/calculations')


@graph_bp.route('', methods=['GET'])
def get_graph():
    """Get current graph structure (vertices and edges)"""
    locations = Location.query.all()
    routes = Route.query.all()
    
    vertices = [loc.node_label for loc in locations]
    
    edges = []
    edge_list = []
    adjacency_list = {}
    
    for loc in locations:
        adjacency_list[loc.node_label] = []
    
    for route in routes:
        source_label = route.source_location.node_label
        dest_label = route.destination_location.node_label
        
        edges.append({
            'source': source_label,
            'destination': dest_label,
            'weight': route.cost,
            'distance': route.distance,
            'time': route.delivery_time
        })
        
        edge_list.append({
            'edge': f'{source_label} → {dest_label}',
            'cost': route.cost,
            'distance': route.distance,
            'time': route.delivery_time
        })
        
        adjacency_list[source_label].append({
            'destination': dest_label,
            'cost': route.cost,
            'distance': route.distance,
            'time': route.delivery_time
        })
    
    return jsonify({
        'vertices': vertices,
        'vertex_count': len(vertices),
        'edges': edges,
        'edge_count': len(edges),
        'edge_list': edge_list,
        'adjacency_list': adjacency_list
    })


@calc_bp.route('/calculate', methods=['POST'])
def run_bellman_ford():
    """Execute Bellman-Ford algorithm"""
    data = request.get_json()
    
    source_label = data.get('source')
    if not source_label:
        return jsonify({'error': 'Source location is required'}), 400
    
    # Get source location
    source_location = Location.query.filter_by(node_label=source_label).first()
    if not source_location:
        return jsonify({'error': f'Source location "{source_label}" not found'}), 404
    
    # Get all locations and routes
    locations = Location.query.all()
    routes = Route.query.all()
    
    if not locations or not routes:
        return jsonify({'error': 'Graph must have locations and routes'}), 400
    
    # Build graph data structures
    vertices = [loc.node_label for loc in locations]
    edges = [(r.source_location.node_label, r.destination_location.node_label, r.cost) for r in routes]
    
    # Execute Bellman-Ford
    start_time = time.time()
    result = bellman_ford(vertices, edges, source_label)
    execution_time = time.time() - start_time
    
    # Store calculation in database
    try:
        calculation = Calculation(
            source_id=source_location.id,
            vertices=result['vertices'],
            edges=result['edges'],
            iterations=result['iterations'],
            negative_cycle=result['negative_cycle'],
            execution_time_ms=result['execution_time_ms']
        )
        
        db.session.add(calculation)
        db.session.flush()  # Get the ID
        
        # Store calculation steps
        for step in result['steps']:
            calc_step = CalculationStep(
                calculation_id=calculation.id,
                iteration=step.get('iteration'),
                edge_source=step.get('edge_source'),
                edge_destination=step.get('edge_destination'),
                weight=step.get('weight'),
                source_distance=step.get('source_distance'),
                candidate_distance=step.get('candidate'),
                old_destination_distance=step.get('old_destination_distance'),
                new_destination_distance=step.get('new_destination_distance'),
                updated=step.get('updated', False),
                predecessor=step.get('predecessor')
            )
            db.session.add(calc_step)
        
        # Store calculation results
        for dest_label, minimum_cost in result['distances'].items():
            dest_location = Location.query.filter_by(node_label=dest_label).first()
            if not dest_location:
                continue
            
            predecessor_label = result['predecessors'].get(dest_label)
            predecessor_location = None
            if predecessor_label:
                predecessor_location = Location.query.filter_by(node_label=predecessor_label).first()
            
            path = result['paths'].get(dest_label, [])
            
            # Calculate path cost and distance/time
            total_distance = 0
            total_time = 0
            
            if path and len(path) > 1:
                for i in range(len(path) - 1):
                    route = Route.query.filter_by(
                        source_id=Location.query.filter_by(node_label=path[i]).first().id,
                        destination_id=Location.query.filter_by(node_label=path[i+1]).first().id
                    ).first()
                    
                    if route:
                        total_distance += route.distance or 0
                        total_time += route.delivery_time or 0
            
            # Determine status
            if minimum_cost == float('inf'):
                status = 'UNREACHABLE'
            elif result['negative_cycle']:
                # Check if this node is affected
                status = 'AFFECTED_BY_CYCLE' if dest_label != source_label else 'REACHABLE'
            else:
                status = 'REACHABLE'
            
            calc_result = CalculationResult(
                calculation_id=calculation.id,
                destination_id=dest_location.id,
                minimum_cost=minimum_cost if minimum_cost != float('inf') else None,
                predecessor_id=predecessor_location.id if predecessor_location else None,
                path_json=json.dumps(path),
                total_distance=total_distance if total_distance > 0 else None,
                total_time=total_time if total_time > 0 else None,
                status=status
            )
            db.session.add(calc_result)
        
        db.session.commit()
        
        # Prepare response
        response_data = {
            'calculation_id': calculation.id,
            'source': source_label,
            'vertices': result['vertices'],
            'edges': result['edges'],
            'distances': {k: v if v != float('inf') else None for k, v in result['distances'].items()},
            'predecessors': result['predecessors'],
            'paths': result['paths'],
            'negative_cycle': result['negative_cycle'],
            'early_termination': result['early_termination'],
            'iterations': result['iterations'],
            'relaxations': result['relaxations'],
            'execution_time_ms': result['execution_time_ms'],
            'steps': result['steps'],
            'complexity': {
                'time': 'O(VE)',
                'space': 'O(V)',
                'graph_storage': 'O(V+E)',
                'current_complexity': f'O({result["vertices"]}×{result["edges"]}) = O({result["vertices"] * result["edges"]})'
            }
        }
        
        return jsonify(response_data), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error storing calculation: {str(e)}'}), 500


@calc_bp.route('/<int:calc_id>', methods=['GET'])
def get_calculation(calc_id):
    """Get calculation details"""
    calculation = Calculation.query.get(calc_id)
    
    if not calculation:
        return jsonify({'error': 'Calculation not found'}), 404
    
    # Get all steps
    steps = [step.to_dict() for step in calculation.steps]
    results = [result.to_dict() for result in calculation.results]
    
    return jsonify({
        'calculation': calculation.to_dict(),
        'steps': steps,
        'results': results
    })


@calc_bp.route('', methods=['GET'])
def list_calculations():
    """List all calculations"""
    calculations = Calculation.query.order_by(Calculation.created_at.desc()).all()
    
    return jsonify([calc.to_dict() for calc in calculations])


@calc_bp.route('/<int:calc_id>/results', methods=['GET'])
def get_calculation_results(calc_id):
    """Get results for a calculation"""
    calculation = Calculation.query.get(calc_id)
    
    if not calculation:
        return jsonify({'error': 'Calculation not found'}), 404
    
    results = calculation.results
    
    # Categorize results
    reachable = [r for r in results if r.status == 'REACHABLE']
    unreachable = [r for r in results if r.status == 'UNREACHABLE']
    
    # Calculate statistics
    costs = [r.minimum_cost for r in reachable if r.minimum_cost is not None]
    
    statistics = {
        'total_destinations': len(results),
        'reachable_count': len(reachable),
        'unreachable_count': len(unreachable),
        'min_cost': min(costs) if costs else None,
        'max_cost': max(costs) if costs else None,
        'avg_cost': sum(costs) / len(costs) if costs else None,
        'total_cost': sum(costs) if costs else None
    }
    
    # Cost distribution
    distribution = categorize_costs(results)
    
    return jsonify({
        'results': [r.to_dict() for r in results],
        'statistics': statistics,
        'cost_distribution': distribution
    })


@calc_bp.route('/<int:calc_id>/results/<int:dest_id>', methods=['GET'])
def get_calculation_result(calc_id, dest_id):
    """Get specific result"""
    result = CalculationResult.query.filter_by(
        calculation_id=calc_id,
        destination_id=dest_id
    ).first()
    
    if not result:
        return jsonify({'error': 'Result not found'}), 404
    
    return jsonify(result.to_dict())


@calc_bp.route('/reset', methods=['POST'])
def reset():
    """Delete all calculations"""
    try:
        db.session.query(CalculationResult).delete()
        db.session.query(CalculationStep).delete()
        db.session.query(Calculation).delete()
        db.session.commit()
        
        return jsonify({'message': 'All calculations reset'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error resetting: {str(e)}'}), 500
