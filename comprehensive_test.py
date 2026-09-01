#!/usr/bin/env python3
"""
Test if the application loads and all modules are accessible
"""

import requests
import json
from bs4 import BeautifulSoup

BASE_URL = 'http://127.0.0.1:5000'

def test_homepage():
    """Test if homepage loads"""
    print("Testing homepage...")
    try:
        r = requests.get(f'{BASE_URL}/')
        print(f"  Status: {r.status_code}")
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Check for modules
            modules = ['overview-module', 'module1-module', 'module2-module', 'module3-module']
            for mod in modules:
                element = soup.find(id=mod)
                if element:
                    print(f"  ✓ {mod} found")
                else:
                    print(f"  ✗ {mod} NOT found")
            
            # Check for scripts
            scripts = ['app.js', 'map.js', 'bellman-ford.js', 'dashboard.js']
            for script in scripts:
                if script in r.text:
                    print(f"  ✓ {script} included")
                else:
                    print(f"  ✗ {script} NOT included")
        else:
            print(f"  ✗ Failed to load homepage")
    except Exception as e:
        print(f"  ✗ Error: {e}")

def test_api_endpoints():
    """Test all API endpoints"""
    print("\nTesting API endpoints...")
    
    endpoints = [
        ('GET', '/api/locations'),
        ('GET', '/api/routes'),
        ('GET', '/api/graph'),
        ('GET', '/api/calculations'),
    ]
    
    for method, endpoint in endpoints:
        try:
            if method == 'GET':
                r = requests.get(f'{BASE_URL}{endpoint}')
            print(f"  {method} {endpoint}: {r.status_code}")
        except Exception as e:
            print(f"  {method} {endpoint}: ERROR - {e}")

def test_calculation():
    """Test Bellman-Ford calculation"""
    print("\nTesting Bellman-Ford calculation...")
    
    try:
        # First, init demo data
        r = requests.post(f'{BASE_URL}/init-demo-data')
        if r.status_code == 201:
            print(f"  ✓ Demo data initialized")
        
        # Run calculation
        r = requests.post(
            f'{BASE_URL}/api/calculations/calculate',
            json={'source': 'A'}
        )
        
        if r.status_code == 201:
            data = r.json()
            print(f"  ✓ Calculation executed")
            print(f"    - Vertices: {data.get('vertices')}")
            print(f"    - Iterations: {data.get('iterations')}")
            print(f"    - Distances: {len(data.get('distances', {}))} vertices")
            print(f"    - Paths: {len(data.get('paths', {}))} vertices")
            
            # Check if calculation_id exists
            if 'calculation_id' in data:
                print(f"    - Calculation ID: {data['calculation_id']}")
                
                # Get results
                calc_id = data['calculation_id']
                r2 = requests.get(f'{BASE_URL}/api/calculations/{calc_id}/results')
                if r2.status_code == 200:
                    results = r2.json()
                    print(f"    ✓ Results retrieved")
                    print(f"      - Cost distribution: {len(results.get('cost_distribution', {}))}")
                    print(f"      - Results count: {len(results.get('results', []))}")
                    print(f"      - Statistics keys: {list(results.get('statistics', {}).keys())}")
                else:
                    print(f"    ✗ Failed to get results: {r2.status_code}")
            else:
                print(f"    ⚠ No calculation_id in response")
        else:
            print(f"  ✗ Calculation failed: {r.status_code}")
            print(f"    Response: {r.json()}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

if __name__ == '__main__':
    test_homepage()
    test_api_endpoints()
    test_calculation()
    print("\n✓ All tests completed")
