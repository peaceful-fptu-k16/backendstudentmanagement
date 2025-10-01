#!/usr/bin/env python3
"""
Simple test for pandas analytics endpoint
"""
try:
    import requests
    print("✅ requests library available")
except ImportError:
    print("❌ requests library not found. Please install: pip install requests")
    exit(1)

import json

def test_endpoint():
    url = "http://127.0.0.1:8001/api/v1/students/pandas-analytics"
    
    try:
        print(f"🧪 Testing: {url}")
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print("Data received:")
            print(json.dumps(data, indent=2)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data, indent=2))
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoint()