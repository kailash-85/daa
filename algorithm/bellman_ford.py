"""
Custom Bellman-Ford Algorithm Implementation
Designed for minimum cost delivery route calculation with detailed step logging.

Time Complexity: O(VE) where V = vertices, E = edges
Space Complexity: O(V) for auxiliary storage
"""

import time
from math import inf


class BellmanFord:
    """
    Bellman-Ford algorithm for finding shortest paths in a weighted directed graph.
    Handles negative edge weights and detects negative-weight cycles.
    """
    
    def __init__(self):
        self.distances = {}
        self.predecessors = {}
        self.steps = []
        self.early_termination = False
        self.negative_cycle = False
        self.vertex_count = 0
        self.edge_count = 0
        self.relaxations_count = 0
        self.iterations_performed = 0
    
    def reset(self):
        """Reset internal state for a new calculation"""
        self.distances = {}
        self.predecessors = {}
        self.steps = []
        self.early_termination = False
        self.negative_cycle = False
        self.relaxations_count = 0
        self.iterations_performed = 0
    
    def calculate(self, vertices, edges, source):
        """
        Execute Bellman-Ford algorithm.
        
        Args:
            vertices: List of vertex labels (e.g., ['A', 'B', 'C', 'D', 'E'])
            edges: List of tuples (source, destination, weight)
                   e.g., [('A', 'B', 4), ('A', 'C', 5), ...]
            source: Source vertex label
        
        Returns:
            dict: {
                'distances': {vertex: minimum_cost, ...},
                'predecessors': {vertex: predecessor, ...},
                'paths': {vertex: [path], ...},
                'steps': [step records],
                'negative_cycle': bool,
                'early_termination': bool,
                'iterations': int,
                'relaxations': int,
                'vertices': int,
                'edges': int
            }
        """
        self.reset()
        start_time = time.time()
        
        self.vertex_count = len(vertices)
        self.edge_count = len(edges)
        
        if not vertices or not edges:
            return self._empty_result()
        
        # STEP 1: INITIALIZATION
        self._initialize(vertices, source)
        
        # Log initialization step
        self.steps.append({
            'iteration': 0,
            'type': 'initialization',
            'distances': dict(self.distances),
            'predecessors': dict(self.predecessors),
            'message': f'Initialize distances. dist[{source}]=0, all others=∞'
        })
        
        # STEP 2: RELAXATION (V-1 iterations)
        max_iterations = len(vertices) - 1
        
        for iteration in range(1, max_iterations + 1):
            self.iterations_performed = iteration
            pre_relax_distances = dict(self.distances)
            relaxations_in_iteration = 0
            
            # Try to relax each edge
            for u, v, weight in edges:
                if self._relax_edge(u, v, weight, iteration):
                    relaxations_in_iteration += 1
            
            # Log iteration
            self.steps.append({
                'iteration': iteration,
                'type': 'relaxation',
                'relaxations': relaxations_in_iteration,
                'distances': dict(self.distances),
                'predecessors': dict(self.predecessors),
                'message': f'Iteration {iteration}: Relaxed {relaxations_in_iteration} edges'
            })
            
            # Early termination: if no distances changed, we're done
            if self.distances == pre_relax_distances:
                self.early_termination = True
                self.steps.append({
                    'iteration': iteration,
                    'type': 'early_termination',
                    'message': 'No updates occurred. Early termination.',
                    'iterations_possible': max_iterations,
                    'iterations_actual': iteration
                })
                break
        
        # STEP 3: NEGATIVE CYCLE DETECTION
        self._detect_negative_cycle(edges)
        
        # Construct paths
        paths = self._reconstruct_paths(vertices, source)
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return {
            'source': source,
            'distances': self.distances,
            'predecessors': self.predecessors,
            'paths': paths,
            'steps': self.steps,
            'negative_cycle': self.negative_cycle,
            'early_termination': self.early_termination,
            'iterations': self.iterations_performed,
            'relaxations': self.relaxations_count,
            'vertices': self.vertex_count,
            'edges': self.edge_count,
            'execution_time_ms': execution_time_ms
        }
    
    def _initialize(self, vertices, source):
        """Initialize distances and predecessors"""
        for v in vertices:
            self.distances[v] = 0 if v == source else inf
            self.predecessors[v] = None
    
    def _relax_edge(self, u, v, weight, iteration):
        """
        Relax an edge.
        
        Returns:
            bool: True if distance was updated, False otherwise
        """
        if self.distances[u] == inf:
            # u is unreachable, skip
            return False
        
        candidate = self.distances[u] + weight
        
        if candidate < self.distances[v]:
            old_dist = self.distances[v]
            self.distances[v] = candidate
            self.predecessors[v] = u
            self.relaxations_count += 1
            
            # Log the relaxation
            self.steps.append({
                'iteration': iteration,
                'type': 'edge_relaxation',
                'edge': f'{u} → {v}',
                'weight': weight,
                'source_distance': self.distances[u],
                'candidate': candidate,
                'old_destination_distance': old_dist,
                'new_destination_distance': candidate,
                'updated': True,
                'predecessor': u,
                'message': f'Updated dist[{v}] from {old_dist} to {candidate}'
            })
            
            return True
        
        return False
    
    def _detect_negative_cycle(self, edges):
        """Detect presence of negative-weight cycle reachable from source"""
        for u, v, weight in edges:
            if self.distances[u] != inf and self.distances[u] + weight < self.distances[v]:
                self.negative_cycle = True
                
                self.steps.append({
                    'iteration': self.vertex_count,
                    'type': 'negative_cycle_detection',
                    'edge': f'{u} → {v}',
                    'weight': weight,
                    'message': f'Negative cycle detected! Edge {u} → {v} can still be relaxed.'
                })
                
                break
    
    def _reconstruct_paths(self, vertices, source):
        """Reconstruct shortest paths for all vertices"""
        paths = {}
        
        for v in vertices:
            if self.distances[v] == inf:
                paths[v] = None  # Unreachable
            else:
                path = self._reconstruct_path(v, source)
                paths[v] = path
        
        return paths
    
    def _reconstruct_path(self, v, source):
        """Reconstruct path from source to v using predecessors"""
        path = []
        current = v
        
        while current is not None:
            path.append(current)
            current = self.predecessors[current]
        
        path.reverse()
        
        # Verify it starts with source
        if path and path[0] == source:
            return path
        else:
            return None
    
    def _empty_result(self):
        """Return empty result structure"""
        return {
            'source': None,
            'distances': {},
            'predecessors': {},
            'paths': {},
            'steps': [],
            'negative_cycle': False,
            'early_termination': False,
            'iterations': 0,
            'relaxations': 0,
            'vertices': 0,
            'edges': 0,
            'execution_time_ms': 0
        }


def bellman_ford(vertices, edges, source):
    """
    Convenience function to run Bellman-Ford algorithm.
    
    Args:
        vertices: List of vertex labels
        edges: List of (source, dest, weight) tuples
        source: Source vertex label
    
    Returns:
        dict: Algorithm result with distances, paths, and execution details
    """
    bf = BellmanFord()
    return bf.calculate(vertices, edges, source)
