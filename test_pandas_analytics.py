#!/usr/bin/env python3
"""
Test script for pandas analytics endpoint
"""
import requests
import json
import sys
from typing import Dict, Any

def test_pandas_analytics():
    """Test the pandas analytics endpoint"""
    url = "http://127.0.0.1:8001/api/v1/students/pandas-analytics"
    
    try:
        print("🧪 Testing Pandas Analytics Endpoint...")
        print(f"📡 Making request to: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Pandas analytics endpoint is working!")
            print("\n📈 Analytics Results:")
            print("=" * 50)
            
            # Pretty print the results
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Extract key metrics
            if 'total_students' in data:
                print(f"\n🎯 Key Metrics:")
                print(f"   📚 Total Students: {data['total_students']}")
                
            if 'pandas_version' in data:
                print(f"   🐼 Pandas Version: {data['pandas_version']}")
                
            if 'analytics' in data:
                analytics = data['analytics']
                print(f"   📊 Analytics Sections: {len(analytics)} sections")
                for key in analytics.keys():
                    print(f"      - {key}")
                    
            if 'data_quality' in data:
                quality = data['data_quality']
                print(f"   🔍 Data Quality:")
                for key, value in quality.items():
                    print(f"      - {key}: {value}")
            
            return True
            
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.ConnectionError:
        print("❌ CONNECTION ERROR: Cannot connect to server at http://127.0.0.1:8001")
        print("   Make sure the FastAPI server is running!")
        return False
        
    except requests.Timeout:
        print("❌ TIMEOUT ERROR: Request took too long")
        return False
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False

def test_basic_endpoints():
    """Test basic endpoints to ensure server is working"""
    base_url = "http://127.0.0.1:8001"
    
    endpoints = [
        "/",
        "/api/v1/students/",
        "/api/v1/students/stats",
        "/api/v1/students/unique/hometown",
        "/health"
    ]
    
    print("\n🔧 Testing Basic Endpoints:")
    print("=" * 40)
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint} - Status: {response.status_code}")
            
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Student Management API - Pandas Analytics Test")
    print("=" * 60)
    
    # Test basic endpoints first
    test_basic_endpoints()
    
    # Test pandas analytics
    success = test_pandas_analytics()
    
    if success:
        print("\n🎉 All tests passed! Pandas integration is working perfectly!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed! Check the server and endpoint implementation.")
        sys.exit(1)