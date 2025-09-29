#!/usr/bin/env python3
"""
Quick start script for Student Management System API
"""


import os
import sys
import subprocess
import time
import requests

# Ensure project root is in sys.path for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        sys.exit(1)

def initialize_database():
    """Initialize the database"""
    print("Initializing database...")
    try:
        from app.database import create_db_and_tables
        create_db_and_tables()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        sys.exit(1)

def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")
    try:
        import requests
        time.sleep(2)  # Wait for server to be ready
        
        response = requests.post("http://localhost:8000/api/v1/students/generate-sample?count=20")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Created {result['successful_imports']} sample students")
        else:
            print(f"⚠ Failed to create sample data: {response.status_code}")
    except Exception as e:
        print(f"⚠ Could not create sample data: {e}")

def test_api():
    """Test basic API endpoints"""
    print("Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health endpoint working")
        else:
            print("✗ Health endpoint failed")
            return False
    except:
        print("✗ Cannot connect to API")
        return False
    
    # Test students endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/students", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Students endpoint working ({data['total']} students found)")
        else:
            print("✗ Students endpoint failed")
    except:
        print("✗ Students endpoint error")
    
    # Test analytics endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/analytics", timeout=5)
        if response.status_code == 200:
            print("✓ Analytics endpoint working")
        else:
            print("✗ Analytics endpoint failed")
    except:
        print("✗ Analytics endpoint error")
    
    return True

def start_server():
    """Start the FastAPI server"""
    print("Starting Student Management API server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for stability
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("=" * 60)
    print("Student Management System - Backend API")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        install_dependencies()
    
    # Initialize database
    initialize_database()
    
    # Start server in background for testing if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        import threading
        import signal
        
        # Start server in background thread
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(3)
        
        # Test API
        if test_api():
            # Create sample data
            create_sample_data()
            print("\n✓ All tests passed!")
            print("API is ready to use!")
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            
    else:
        # Normal server start
        start_server()

if __name__ == "__main__":
    main()