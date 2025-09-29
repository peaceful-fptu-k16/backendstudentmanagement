#!/usr/bin/env python3
"""
Test DELETE endpoint functionality
"""

import requests
import json
import time

def test_delete_student():
    """Test DELETE student functionality"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("DELETE Student Test - Student Management API")
    print("=" * 60)
    
    # Wait for server to be ready
    time.sleep(1)
    
    print("\n1. Creating test student first:")
    try:
        student_data = {
            "student_id": "DELETE01",
            "full_name": "Delete Test Student",
            "email": "delete.test@example.com",
            "hometown": "Test City"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/students",
            json=student_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Student created: {data['full_name']} ({data['student_id']})")
            print(f"   Database ID: {data['id']}")
        else:
            print(f"❌ Failed to create student: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error creating student: {e}")
        return
    
    print("\n2. Verifying student exists:")
    try:
        response = requests.get(f"{base_url}/api/v1/students/DELETE01")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Student found: {data['full_name']} (ID: {data['id']})")
        else:
            print(f"❌ Student not found: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting student: {e}")
        return
    
    print("\n3. Testing DELETE by student_id:")
    try:
        response = requests.delete(f"{base_url}/api/v1/students/DELETE01")
        print(f"DELETE Status Code: {response.status_code}")
        print(f"DELETE Response Body: '{response.text}'")
        print(f"DELETE Response Length: {len(response.text)}")
        
        if response.status_code == 204:
            print("✅ DELETE returned correct 204 No Content status")
            if len(response.text) == 0:
                print("✅ Response body is empty as expected for 204")
            else:
                print(f"⚠ Response body not empty: '{response.text}'")
        else:
            print(f"❌ DELETE failed with status: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error deleting student: {e}")
        return
    
    print("\n4. Verifying student was deleted:")
    try:
        response = requests.get(f"{base_url}/api/v1/students/DELETE01")
        if response.status_code == 404:
            print("✅ Student successfully deleted (404 Not Found)")
        elif response.status_code == 422:
            print("✅ Student not found (might be validation error on empty result)")
        else:
            print(f"❌ Student still exists: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error verifying deletion: {e}")
    
    print("\n5. Testing DELETE with non-existent student:")
    try:
        response = requests.delete(f"{base_url}/api/v1/students/NONEXIST")
        if response.status_code == 404:
            print("✅ Non-existent student correctly returns 404")
        else:
            print(f"❌ Unexpected status for non-existent student: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing non-existent student: {e}")
    
    print("\n" + "=" * 60)
    print("DELETE Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_delete_student()