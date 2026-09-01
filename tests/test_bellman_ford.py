"""
Unit tests for Bellman-Ford algorithm implementation
"""

import pytest
from algorithm.bellman_ford import bellman_ford, BellmanFord


class TestBellmanFord:
    """Test cases for Bellman-Ford algorithm"""
    
    def test_basic_shortest_path(self):
        """Test basic shortest path calculation"""
        vertices = ['A', 'B', 'C', 'D', 'E']
        edges = [
            ('A', 'B', 4),
            ('A', 'C', 5),
            ('A', 'D', 7),
            ('B', 'C', 2),
            ('B', 'D', 3),
            ('C', 'D', 1),
            ('C', 'E', 4),
            ('D', 'E', 2),
        ]
        
        result = bellman_ford(vertices, edges, 'A')
        
        # Check distances
        assert result['distances']['A'] == 0
        assert result['distances']['B'] == 4
        assert result['distances']['C'] == 5
        assert result['distances']['D'] == 6
        assert result['distances']['E'] == 8
        
        # Check paths
        assert result['paths']['A'] == ['A']
        assert result['paths']['B'] == ['A', 'B']
        assert result['paths']['E'] == ['A', 'B', 'D', 'E']
    
    def test_unreachable_vertex(self):
        """Test with unreachable vertices"""
        vertices = ['A', 'B', 'C']
        edges = [
            ('A', 'B', 5),
            ('C', 'A', 3),
        ]
        
        result = bellman_ford(vertices, edges, 'A')
        
        assert result['distances']['A'] == 0
        assert result['distances']['B'] == 5
        assert result['distances']['C'] == float('inf')
        assert result['paths']['C'] is None
    
    def test_negative_edge_weights(self):
        """Test with negative edge weights (no cycle)"""
        vertices = ['A', 'B', 'C']
        edges = [
            ('A', 'B', -1),
            ('B', 'C', -2),
            ('A', 'C', 5),
        ]
        
        result = bellman_ford(vertices, edges, 'A')
        
        assert result['distances']['A'] == 0
        assert result['distances']['B'] == -1
        assert result['distances']['C'] == -3  # Via A -> B -> C
        assert result['negative_cycle'] == False
    
    def test_negative_cycle_detection(self):
        """Test negative cycle detection"""
        vertices = ['A', 'B', 'C']
        edges = [
            ('A', 'B', 1),
            ('B', 'C', -3),
            ('C', 'B', 1),  # Cycle: B -> C -> B with total weight -2
        ]
        
        result = bellman_ford(vertices, edges, 'A')
        
        # Should detect negative cycle
        assert result['negative_cycle'] == True
    
    def test_single_vertex(self):
        """Test with single vertex"""
        vertices = ['A']
        edges = []
        
        result = bellman_ford(vertices, edges, 'A')
        
        assert result['distances']['A'] == 0
        assert result['vertices'] == 1
        assert result['edges'] == 0
    
    def test_early_termination(self):
        """Test early termination when no improvements possible"""
        vertices = ['A', 'B', 'C']
        edges = [
            ('A', 'B', 1),
            ('B', 'C', 2),
        ]
        
        result = bellman_ford(vertices, edges, 'A')
        
        # Early termination should occur
        assert result['early_termination'] == True
        assert result['iterations'] < len(vertices) - 1
    
    def test_empty_graph(self):
        """Test with empty graph"""
        vertices = []
        edges = []
        
        result = bellman_ford(vertices, edges, 'A')
        
        assert result['vertices'] == 0
        assert result['edges'] == 0
    
    def test_execution_logging(self):
        """Test that execution steps are logged"""
        vertices = ['A', 'B']
        edges = [('A', 'B', 5)]
        
        result = bellman_ford(vertices, edges, 'A')
        
        # Should have initialization and relaxation steps
        assert len(result['steps']) > 0
        assert any(step['type'] == 'initialization' for step in result['steps'])
        assert any(step['type'] == 'edge_relaxation' for step in result['steps'])
    
    def test_predecessor_tracking(self):
        """Test that predecessors are correctly tracked"""
        vertices = ['A', 'B', 'C']
        edges = [
            ('A', 'B', 1),
            ('B', 'C', 2),
        ]
        
        result = bellman_ford(vertices, edges, 'A')
        
        assert result['predecessors']['A'] is None
        assert result['predecessors']['B'] == 'A'
        assert result['predecessors']['C'] == 'B'
    
    def test_large_graph(self):
        """Test with larger graph"""
        # Create a graph with 10 vertices
        vertices = [chr(ord('A') + i) for i in range(10)]
        edges = []
        
        # Create edges with increasing weights
        for i in range(9):
            edges.append((vertices[i], vertices[i+1], 1))
        
        result = bellman_ford(vertices, edges, 'A')
        
        # Distances should be cumulative
        for i, v in enumerate(vertices):
            assert result['distances'][v] == i


class TestBellmanFordClass:
    """Test cases for BellmanFord class"""
    
    def test_reset_state(self):
        """Test that reset clears state"""
        bf = BellmanFord()
        
        # Run once
        bf.calculate(['A', 'B'], [('A', 'B', 1)], 'A')
        
        # Reset
        bf.reset()
        
        assert bf.distances == {}
        assert bf.predecessors == {}
        assert bf.steps == []
        assert bf.early_termination == False
        assert bf.negative_cycle == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
