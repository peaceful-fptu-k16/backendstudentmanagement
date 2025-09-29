#!/usr/bin/env python3
"""
Test Analytics Endpoints
"""

import requests
import json
import time

def test_analytics_endpoints():
    """Test all analytics endpoints"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Analytics Endpoints Test")
    print("=" * 60)
    
    # Wait for server to be ready
    time.sleep(1)
    
    endpoints = [
        "/api/v1/analytics",
        "/api/v1/analytics/summary", 
        "/api/v1/analytics/score-comparison",
        "/api/v1/analytics/hometown-analysis",
        "/api/v1/analytics/performance-trends"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success - Response keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
                except:
                    print(f"✅ Success - Response length: {len(response.text)} chars")
            elif response.status_code == 404:
                print(f"❌ NOT FOUND - Endpoint doesn't exist")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection refused - Server not running?")
            return
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_analytics_endpoints()