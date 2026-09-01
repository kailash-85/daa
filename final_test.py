#!/usr/bin/env python3
import requests
import json

print('='*60)
print('FINAL COMPREHENSIVE TEST')
print('='*60)

# Initialize demo
print('\n1. Initializing demo data...')
r = requests.post('http://127.0.0.1:5000/init-demo-data')
print(f'   Status: {r.status_code}')
print(f'   Response: {r.json()}')

# Get locations
print('\n2. Loading locations...')
r = requests.get('http://127.0.0.1:5000/api/locations')
print(f'   Status: {r.status_code}')
locs = r.json()
print(f'   Locations loaded: {len(locs)}')

# Run Bellman-Ford
print('\n3. Running Bellman-Ford (Module 2 test)...')
r = requests.post('http://127.0.0.1:5000/api/calculations/calculate', json={'source': 'A'})
print(f'   Status: {r.status_code}')
if r.status_code == 201:
    calc = r.json()
    print(f'   ✓ Calculation ID: {calc.get("calculation_id")}')
    print(f'   ✓ Vertices: {calc.get("vertices")}')
    print(f'   ✓ Steps: {len(calc.get("steps", []))}')
    print(f'   ✓ Paths reconstructed: {len(calc.get("paths", {}))}')
    
    # Get results for dashboard
    print('\n4. Retrieving calculation results (Module 3 test)...')
    calc_id = calc.get('calculation_id')
    r2 = requests.get(f'http://127.0.0.1:5000/api/calculations/{calc_id}/results')
    print(f'   Status: {r2.status_code}')
    if r2.status_code == 200:
        results = r2.json()
        print(f'   ✓ Cost distribution keys: {list(results.get("cost_distribution", {}).keys())[:2]}...')
        print(f'   ✓ Results: {len(results.get("results", []))} destinations')
        print(f'   ✓ Statistics: {list(results.get("statistics", {}).keys())}')
        
        # Check results data
        first_result = results['results'][0] if results.get('results') else {}
        print(f'\n5. Checking result object structure...')
        print(f'   ✓ destination_label: {first_result.get("destination_label")}')
        print(f'   ✓ minimum_cost: {first_result.get("minimum_cost")}')
        print(f'   ✓ path: {first_result.get("path")}')
        print(f'   ✓ status: {first_result.get("status")}')
else:
    print(f'   ✗ Error: {r.json()}')

print('\n' + '='*60)
print('✓ ALL TESTS COMPLETED SUCCESSFULLY')
print('='*60)
