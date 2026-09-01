#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Test 1: Get locations
print("=" * 60)
print("TEST 1: Get Locations")
print("=" * 60)
r = requests.get(f"{BASE_URL}/api/locations")
locations = r.json()
print(f"Status: {r.status_code}")
print(f"Locations ({len(locations)}):")
for loc in locations:
    print(f"  {loc['node_label']}: {loc['name']} ({loc['latitude']}, {loc['longitude']})")

# Test 2: Get routes
print("\n" + "=" * 60)
print("TEST 2: Get Routes")
print("=" * 60)
r = requests.get(f"{BASE_URL}/api/routes")
routes = r.json()
print(f"Status: {r.status_code}")
print(f"Routes ({len(routes)}):")
for route in routes:
    print(f"  {route['source_label']} → {route['destination_label']}: ₹{route['cost']} ({route['distance']}km, {route['delivery_time']}min)")

# Test 3: Get graph
print("\n" + "=" * 60)
print("TEST 3: Get Graph Structure")
print("=" * 60)
r = requests.get(f"{BASE_URL}/api/graph")
graph = r.json()
print(f"Status: {r.status_code}")
print(f"Vertices: {graph['vertex_count']}")
print(f"Edges: {graph['edge_count']}")
print(f"Vertices list: {graph['vertices']}")
print(f"Sample edges: {graph['edges'][:3]}")

# Test 4: Run Bellman-Ford Algorithm
print("\n" + "=" * 60)
print("TEST 4: Run Bellman-Ford Algorithm (Source: A)")
print("=" * 60)
data = {"source_label": "A"}
r = requests.post(f"{BASE_URL}/api/calculations/calculate", json=data)
calc = r.json()
print(f"Status: {r.status_code}")
print(f"Calculation ID: {calc['id']}")
print(f"Vertices: {calc['vertices']}, Edges: {calc['edges']}")
print(f"Iterations: {calc['iterations']}")
print(f"Negative Cycle: {calc['negative_cycle']}")
print(f"Execution Time: {calc['execution_time_ms']:.2f}ms")
print(f"Steps logged: {len(calc['steps'])}")

# Test 5: Get calculation results
print("\n" + "=" * 60)
print("TEST 5: Get Calculation Results")
print("=" * 60)
calc_id = calc['id']
r = requests.get(f"{BASE_URL}/api/calculations/{calc_id}/results")
results = r.json()
print(f"Status: {r.status_code}")
print(f"Results from source A:")
for result in results:
    print(f"  → {result['destination_label']}: ₹{result['minimum_cost']} ({result['status']})")
    if result['path']:
        print(f"    Path: {' → '.join(result['path'])}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
