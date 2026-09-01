"""
Unit tests for path reconstruction utilities
"""

import pytest
from algorithm.path_reconstruction import (
    reconstruct_path, calculate_path_cost_breakdown,
    get_reachable_vertices, get_unreachable_vertices,
    analyze_cost_distribution, categorize_costs
)


class TestPathReconstruction:
    """Test path reconstruction functions"""
    
    def test_reconstruct_path_basic(self):
        """Test basic path reconstruction"""
        predecessors = {
            'A': None,
            'B': 'A',
            'C': 'B',
            'D': 'C'
        }
        
        path = reconstruct_path('D', predecessors, 'A')
        
        assert path == ['A', 'B', 'C', 'D']
    
    def test_reconstruct_path_single_vertex(self):
        """Test path reconstruction for single vertex"""
        predecessors = {'A': None}
        
        path = reconstruct_path('A', predecessors, 'A')
        
        assert path == ['A']
    
    def test_reconstruct_path_unreachable(self):
        """Test unreachable vertex returns None"""
        predecessors = {
            'A': None,
            'B': None,  # Not reachable from A
        }
        
        path = reconstruct_path('B', predecessors, 'A')
        
        assert path is None


class TestReachableVertices:
    """Test reachable vertex detection"""
    
    def test_get_reachable_vertices(self):
        """Test identifying reachable vertices"""
        distances = {
            'A': 0,
            'B': 5,
            'C': float('inf'),
            'D': 10
        }
        
        reachable = get_reachable_vertices(distances)
        
        assert set(reachable) == {'A', 'B', 'D'}
        assert 'C' not in reachable
    
    def test_get_unreachable_vertices(self):
        """Test identifying unreachable vertices"""
        distances = {
            'A': 0,
            'B': 5,
            'C': float('inf'),
            'D': 10
        }
        
        unreachable = get_unreachable_vertices(distances)
        
        assert unreachable == ['C']


class TestCostDistribution:
    """Test cost distribution analysis"""
    
    def test_categorize_costs_default_ranges(self):
        """Test cost categorization with default ranges"""
        # Mock results with cost information
        class MockResult:
            def __init__(self, cost, status='REACHABLE'):
                self.minimum_cost = cost
                self.status = status
                self.destination_location = type('obj', (object,), {'node_label': 'X'})()
        
        results = [
            MockResult(50),
            MockResult(150),
            MockResult(250),
            MockResult(400),
            MockResult(600),
        ]
        
        categories = categorize_costs(results)
        
        assert categories['₹0–₹100']['count'] == 1
        assert categories['₹101–₹200']['count'] == 1
        assert categories['₹201–₹300']['count'] == 1
        assert categories['₹301–₹500']['count'] == 1
        assert categories['₹501+']['count'] == 1
    
    def test_categorize_costs_skip_unreachable(self):
        """Test that unreachable destinations are excluded"""
        class MockResult:
            def __init__(self, cost, status='REACHABLE'):
                self.minimum_cost = cost
                self.status = status
                self.destination_location = type('obj', (object,), {'node_label': 'X'})()
        
        results = [
            MockResult(50),
            MockResult(None, 'UNREACHABLE'),
            MockResult(150),
        ]
        
        categories = categorize_costs(results)
        
        total = sum(c['count'] for c in categories.values())
        assert total == 2  # Only reachable destinations


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
