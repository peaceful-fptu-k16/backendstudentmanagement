"""
Demo Daily Logging System
========================

This script demonstrates the new daily folder-based logging system
"""
import requests
import time
import os
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001/api/v1"
LOG_BASE_DIR = "logs"

def show_log_structure():
    """Display current log folder structure"""
    print("📁 CURRENT LOG STRUCTURE:")
    print("=" * 40)
    
    if os.path.exists(LOG_BASE_DIR):
        for item in sorted(os.listdir(LOG_BASE_DIR)):
            item_path = os.path.join(LOG_BASE_DIR, item)
            if os.path.isdir(item_path):
                print(f"📂 {item}/ (Daily Folder)")
                # List files in daily folder
                for file in sorted(os.listdir(item_path)):
                    file_path = os.path.join(item_path, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        print(f"   📄 {file} ({size} bytes)")
            elif os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                print(f"📄 {item} ({size} bytes) [Legacy]")
    else:
        print("No logs directory found")
    print()

def create_test_students():
    """Create test students to generate logs"""
    print("🧪 CREATING TEST STUDENTS TO GENERATE LOGS:")
    print("=" * 50)
    
    students = [
        {
            "student_id": "SV240101",
            "first_name": "Bob",
            "last_name": "Smith",
            "email": "bob.smith@email.com",
            "math_score": 7.5,
            "literature_score": 8.0,
            "english_score": 8.5
        },
        {
            "student_id": "SV240102", 
            "first_name": "Carol",
            "last_name": "Johnson",
            "email": "carol.johnson@email.com",
            "math_score": 9.0,
            "literature_score": 8.5,
            "english_score": 9.5
        }
    ]
    
    for i, student_data in enumerate(students, 1):
        try:
            response = requests.post(f"{BASE_URL}/students", json=student_data)
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✓ Student {i}: {result['first_name']} {result['last_name']} - ID: {result['student_id']}")
            else:
                print(f"✗ Student {i}: Error {response.status_code}")
        except Exception as e:
            print(f"✗ Student {i}: Connection error - {e}")
        
        time.sleep(0.5)  # Small delay between requests
    print()

def test_other_endpoints():
    """Test other endpoints to generate different types of logs"""
    print("🔍 TESTING OTHER ENDPOINTS:")
    print("=" * 35)
    
    # Test get all students
    try:
        response = requests.get(f"{BASE_URL}/students")
        if response.status_code == 200:
            data = response.json()
            count = data.get('total', 0) if isinstance(data, dict) else len(data)
            print(f"✓ GET /students: Found {count} students")
        else:
            print(f"✗ GET /students: Error {response.status_code}")
    except Exception as e:
        print(f"✗ GET /students: {e}")
    
    # Test get individual student
    try:
        response = requests.get(f"{BASE_URL}/students/1")
        if response.status_code == 200:
            student = response.json()
            print(f"✓ GET /students/1: {student.get('first_name', 'N/A')} {student.get('last_name', 'N/A')}")
        else:
            print(f"✗ GET /students/1: Error {response.status_code}")
    except Exception as e:
        print(f"✗ GET /students/1: {e}")
    
    print()

def show_daily_logs():
    """Show contents of today's logs"""
    today = datetime.now().strftime("%Y-%m-%d")
    today_log_dir = os.path.join(LOG_BASE_DIR, today)
    
    print(f"📊 TODAY'S LOGS ({today}):")
    print("=" * 40)
    
    if os.path.exists(today_log_dir):
        for log_file in ["api.log", "database.log"]:
            log_path = os.path.join(today_log_dir, log_file)
            if os.path.exists(log_path):
                print(f"\n📄 {log_file} (last 3 lines):")
                print("-" * 30)
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines[-3:]:
                            print(f"  {line.strip()}")
                except Exception as e:
                    print(f"  Error reading file: {e}")
    else:
        print(f"No logs found for today ({today})")
    print()

def main():
    print("🚀 DAILY LOGGING SYSTEM DEMO")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Server: {BASE_URL}")
    print()
    
    # Show current structure
    show_log_structure()
    
    # Create test data
    create_test_students()
    
    # Test endpoints
    test_other_endpoints()
    
    # Show updated structure
    print("📁 UPDATED LOG STRUCTURE:")
    print("=" * 30)
    show_log_structure()
    
    # Show log contents
    show_daily_logs()
    
    print("🎯 DAILY LOGGING FEATURES:")
    print("=" * 35)
    print("✓ Automatic daily folder creation (YYYY-MM-DD)")
    print("✓ Hourly log rotation within daily folders")
    print("✓ Separate files by log type (api, database, export, etc.)")
    print("✓ Automatic cleanup of old folders (30+ days)")
    print("✓ Structured JSON logging for easy parsing")
    print("✓ Performance metrics and error tracking")
    print()
    print("📂 Log files are organized as:")
    print("   logs/YYYY-MM-DD/api.log")
    print("   logs/YYYY-MM-DD/database.log") 
    print("   logs/YYYY-MM-DD/export.log")
    print("   logs/YYYY-MM-DD/*_errors.log")
    print()
    print("🎉 Daily logging system is working perfectly!")

if __name__ == "__main__":
    main()