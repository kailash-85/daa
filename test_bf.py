#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Test Bellman-Ford with error details
print("Testing Bellman-Ford Algorithm...")
data = {"source_label": "A"}
r = requests.post(f"{BASE_URL}/api/calculations/calculate", json=data)
print(f"Status: {r.status_code}")
print(f"Response: {json.dumps(r.json(), indent=2)}")
