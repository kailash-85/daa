#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Test complete workflow
print("=" * 70)
print("COMPLETE WORKFLOW TEST")
print("=" * 70)

# Step 1: Get Graph
print("\n1. Get Graph Structure")
r = requests.get(f"{BASE_URL}/api/graph")
print(f"   Status: {r.status_code}")
graph = r.json()
print(f"   V={graph['vertex_count']}, E={graph['edge_count']}")

# Step 2: Run Bellman-Ford
print("\n2. Run Bellman-Ford (Source: A)")
r = requests.post(f"{BASE_URL}/api/calculations/calculate", json={'source': 'A'})
print(f"   Status: {r.status_code}")
calc_resp = r.json()
print(f"   Full Response: {json.dumps(calc_resp, indent=6)}")

# Try to get calculation ID from response
if 'id' in calc_resp:
    calc_id = calc_resp['id']
    print(f"   Calculation ID: {calc_id}")
elif 'calculation_id' in calc_resp:
    calc_id = calc_resp['calculation_id']
    print(f"   Calculation ID: {calc_id}")
else:
    print("   WARNING: Could not extract calculation ID from response!")
    calc_id = None

# Step 3: Show final distances
print("\n3. Final Distances from Source A:")
if 'distances' in calc_resp:
    for dest, dist in calc_resp['distances'].items():
        print(f"   A → {dest}: {dist if dist != float('inf') else 'unreachable'}")

# Step 4: Show paths if available
print("\n4. Paths from Source A:")
if 'paths' in calc_resp:
    for dest, path in calc_resp['paths'].items():
        if path:
            print(f"   A → {dest}: {' → '.join(path)}")
        else:
            print(f"   A → {dest}: unreachable")

print("\n" + "=" * 70)
