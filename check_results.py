#!/usr/bin/env python3
import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

# Get latest calculation
r = requests.get(f'{BASE_URL}/api/calculations')
calculations = r.json()

if calculations:
    latest_id = calculations[0]['id']
    print(f'Latest calculation ID: {latest_id}')
    print()
    
    # Get results
    r2 = requests.get(f'{BASE_URL}/api/calculations/{latest_id}/results')
    print(f'Results Status: {r2.status_code}')
    results = r2.json()
    
    print(f'Results type: {type(results).__name__}')
    if isinstance(results, dict):
        print(f'Results keys: {list(results.keys())}')
        print(f'Full response:\n{json.dumps(results, indent=2)[:1000]}')
    elif isinstance(results, list):
        print(f'Results is a list with {len(results)} items')
        print(f'First item:\n{json.dumps(results[0], indent=2)[:1000]}')
