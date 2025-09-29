"""
Simple test to check logging system
"""
import requests
import time
import sys

def test_health():
    """Simple health check"""
    try:
        response = requests.get("http://127.0.0.1:8001/")
        print(f"Health check: {response.status_code}")
        return True
    except:
        print("Server not ready")
        return False

def test_student_create():
    """Create a student"""
    data = {
        "name": "Test Student",
        "email": "test@example.com",
        "age": 22,
        "student_id": "TEST001",
        "major": "Computer Science"
    }
    
    try:
        response = requests.post("http://127.0.0.1:8001/api/v1/students/", json=data)
        print(f"Create student: {response.status_code}")
        if response.status_code in [200, 201]:
            return response.json()
        return None
    except Exception as e:
        print(f"Error creating student: {e}")
        return None

def main():
    print("Testing logging system...")
    
    # Test health
    if not test_health():
        print("Server not ready, exiting")
        sys.exit(1)
    
    # Create student
    student = test_student_create()
    if student:
        print(f"Student created with ID: {student.get('id', 'unknown')}")
    
    print("Check log files:")
    print("- logs/app.log")
    print("- logs/api.log") 
    print("- logs/performance.log")
    print("- logs/error.log")

if __name__ == "__main__":
    main()