# 🧪 Testing Guide

## 📋 Table of Contents
1. [Testing Overview](#testing-overview)
2. [Test Types](#test-types)
3. [Running Tests](#running-tests)
4. [Test Scripts](#test-scripts)
5. [API Testing](#api-testing)
6. [Writing Tests](#writing-tests)
7. [Best Practices](#best-practices)

---

## 🎯 Testing Overview

### Testing Strategy
```yaml
Unit Tests: CRUD operations, services
Integration Tests: API endpoints, database
Functional Tests: Complete workflows
Visual Tests: Seaborn visualizations
```

### Testing Stack
- **pytest**: Primary testing framework
- **requests**: HTTP client for API testing
- **pandas**: Data validation
- **seaborn/matplotlib**: Visualization testing

---

## 🔬 Test Types

### 1. Unit Tests
Test individual functions and methods in isolation.

```python
# Test CRUD operations
def test_create_student():
    student = Student(
        student_id="SV001",
        first_name="John",
        last_name="Doe"
    )
    assert student.student_id == "SV001"
    assert student.first_name == "John"
```

### 2. Integration Tests
Test multiple components working together.

```python
# Test API endpoint with database
def test_api_create_student():
    response = requests.post(
        "http://localhost:8001/api/v1/students",
        json={
            "student_id": "SV001",
            "first_name": "John",
            "last_name": "Doe"
        }
    )
    assert response.status_code == 200
    assert response.json()["student_id"] == "SV001"
```

### 3. Functional Tests
Test complete user workflows.

```python
# Test complete student management workflow
def test_student_lifecycle():
    # 1. Create student
    create_response = create_student(...)
    student_id = create_response["id"]
    
    # 2. Read student
    get_response = get_student(student_id)
    assert get_response["id"] == student_id
    
    # 3. Update student
    update_response = update_student(student_id, ...)
    
    # 4. Delete student
    delete_response = delete_student(student_id)
    assert delete_response.status_code == 200
```

---

## 🏃 Running Tests

### Run All Tests
```bash
# Using pytest
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=app --cov-report=html
```

### Run Specific Tests
```bash
# Run single test file
pytest tests/test_api.py

# Run single test function
pytest tests/test_api.py::test_create_student

# Run tests matching pattern
pytest -k "student"
```

### Run Test Scripts
```bash
# Simple API test
python simple_test.py

# Seaborn visualization test
python test_seaborn_demo.py

# Pandas analytics test
python test_pandas_analytics.py

# Seaborn API endpoint test
python test_seaborn_visualizations.py
```

---

## 📝 Test Scripts

### 1. simple_test.py
Basic API endpoint testing.

```python
# File: simple_test.py

import requests
import json

BASE_URL = "http://localhost:8001"

def test_create_student():
    """Test creating a new student"""
    response = requests.post(
        f"{BASE_URL}/api/v1/students",
        json={
            "student_id": "SV001",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "hometown": "Hanoi",
            "math_score": 8.5,
            "literature_score": 7.5,
            "english_score": 9.0
        }
    )
    print(f"Create: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_get_students():
    """Test getting all students"""
    response = requests.get(f"{BASE_URL}/api/v1/students")
    print(f"Get All: {response.status_code}")
    print(f"Total Students: {len(response.json())}")
    return response.json()

def test_get_student(student_id):
    """Test getting a single student"""
    response = requests.get(f"{BASE_URL}/api/v1/students/{student_id}")
    print(f"Get One: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_update_student(student_id):
    """Test updating a student"""
    response = requests.put(
        f"{BASE_URL}/api/v1/students/{student_id}",
        json={
            "math_score": 9.5,
            "literature_score": 8.5,
            "english_score": 9.5
        }
    )
    print(f"Update: {response.status_code}")
    return response.json()

def test_delete_student(student_id):
    """Test deleting a student"""
    response = requests.delete(f"{BASE_URL}/api/v1/students/{student_id}")
    print(f"Delete: {response.status_code}")
    return response.status_code

if __name__ == "__main__":
    print("Running API tests...")
    
    # Test CRUD operations
    student = test_create_student()
    test_get_students()
    test_get_student(student["id"])
    test_update_student(student["id"])
    test_delete_student(student["id"])
    
    print("\nAll tests completed!")
```

### 2. test_seaborn_demo.py
Seaborn visualization testing with sample data.

```python
# File: test_seaborn_demo.py

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample student data"""
    hometowns = ["Hanoi", "Ho Chi Minh", "Da Nang", "Hai Phong", "Can Tho"]
    students = []
    
    for i in range(50):
        student = {
            "student_id": f"SV{i+1:03d}",
            "first_name": f"First{i+1}",
            "last_name": f"Last{i+1}",
            "hometown": random.choice(hometowns),
            "birth_date": datetime.now() - timedelta(days=random.randint(6570, 7300)),
            "math_score": round(random.uniform(5.0, 10.0), 1),
            "literature_score": round(random.uniform(5.0, 10.0), 1),
            "english_score": round(random.uniform(5.0, 10.0), 1)
        }
        students.append(student)
    
    return pd.DataFrame(students)

def test_basic_seaborn():
    """Test basic Seaborn functionality"""
    print("\nTest 1: Score Distribution (Histogram)")
    df = create_sample_data()
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 3, 1)
    sns.histplot(data=df, x="math_score", bins=10, kde=True)
    plt.title("Math Score Distribution")
    
    plt.subplot(1, 3, 2)
    sns.histplot(data=df, x="literature_score", bins=10, kde=True)
    plt.title("Literature Score Distribution")
    
    plt.subplot(1, 3, 3)
    sns.histplot(data=df, x="english_score", bins=10, kde=True)
    plt.title("English Score Distribution")
    
    plt.tight_layout()
    plt.savefig("test_score_distribution.png", dpi=100, bbox_inches='tight')
    print("PASS - Score distribution chart created")
    
    # Test 2: Boxplot
    print("\nTest 2: Score Comparison (Boxplot)")
    plt.figure(figsize=(10, 6))
    
    scores_df = pd.melt(
        df[["math_score", "literature_score", "english_score"]],
        var_name="Subject",
        value_name="Score"
    )
    
    sns.boxplot(data=scores_df, x="Subject", y="Score")
    plt.title("Score Comparison by Subject")
    plt.savefig("test_boxplot.png", dpi=100, bbox_inches='tight')
    print("PASS - Boxplot created")
    
    # Test 3: Correlation Heatmap
    print("\nTest 3: Correlation Heatmap")
    plt.figure(figsize=(8, 6))
    
    correlation = df[["math_score", "literature_score", "english_score"]].corr()
    sns.heatmap(correlation, annot=True, cmap="coolwarm", center=0)
    plt.title("Score Correlation Matrix")
    plt.savefig("test_heatmap.png", dpi=100, bbox_inches='tight')
    print("PASS - Heatmap created")
    
    # Test 4: Scatter Plot
    print("\nTest 4: Score Relationships (Scatter Plot)")
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 3, 1)
    sns.scatterplot(data=df, x="math_score", y="literature_score")
    plt.title("Math vs Literature")
    
    plt.subplot(1, 3, 2)
    sns.scatterplot(data=df, x="math_score", y="english_score")
    plt.title("Math vs English")
    
    plt.subplot(1, 3, 3)
    sns.scatterplot(data=df, x="literature_score", y="english_score")
    plt.title("Literature vs English")
    
    plt.tight_layout()
    plt.savefig("test_scatter.png", dpi=100, bbox_inches='tight')
    print("PASS - Scatter plot created")
    
    # Test 5: Hometown Analysis
    print("\nTest 5: Hometown Performance Dashboard")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Student count by hometown
    sns.countplot(data=df, x="hometown", ax=axes[0, 0])
    axes[0, 0].set_title("Students by Hometown")
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Average scores by hometown
    hometown_avg = df.groupby("hometown")[
        ["math_score", "literature_score", "english_score"]
    ].mean().reset_index()
    
    hometown_melted = pd.melt(
        hometown_avg,
        id_vars=["hometown"],
        value_vars=["math_score", "literature_score", "english_score"],
        var_name="Subject",
        value_name="Average Score"
    )
    
    sns.barplot(data=hometown_melted, x="hometown", y="Average Score", 
                hue="Subject", ax=axes[0, 1])
    axes[0, 1].set_title("Average Scores by Hometown")
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Score distribution by hometown (Math)
    sns.boxplot(data=df, x="hometown", y="math_score", ax=axes[1, 0])
    axes[1, 0].set_title("Math Score by Hometown")
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Overall performance
    df["average_score"] = df[["math_score", "literature_score", "english_score"]].mean(axis=1)
    sns.violinplot(data=df, x="hometown", y="average_score", ax=axes[1, 1])
    axes[1, 1].set_title("Overall Performance by Hometown")
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("test_dashboard.png", dpi=100, bbox_inches='tight')
    print("PASS - Dashboard created")

if __name__ == "__main__":
    print("Starting Seaborn Demo Tests...")
    test_basic_seaborn()
    print("\n=== ALL TESTS PASSED (5/5) ===")
```

### 3. test_seaborn_visualizations.py
Test Seaborn API endpoints.

```python
# File: test_seaborn_visualizations.py

import requests
import base64
from PIL import Image
from io import BytesIO

BASE_URL = "http://localhost:8001/api/v1"

def save_chart(base64_data, filename):
    """Save base64 image to file"""
    image_data = base64.b64decode(base64_data)
    image = Image.open(BytesIO(image_data))
    image.save(filename)
    print(f"Saved: {filename}")

def test_visualizations():
    """Test all visualization endpoints"""
    
    print("1. Testing Score Distribution Chart...")
    response = requests.get(f"{BASE_URL}/visualizations/score-distribution")
    if response.status_code == 200:
        data = response.json()
        save_chart(data["image"], "score_distribution.png")
        print(f"PASS - {data['total_students']} students")
    
    print("\n2. Testing Correlation Heatmap...")
    response = requests.get(f"{BASE_URL}/visualizations/correlation-heatmap")
    if response.status_code == 200:
        data = response.json()
        save_chart(data["image"], "correlation_heatmap.png")
        print("PASS - Correlation matrix created")
    
    print("\n3. Testing Hometown Analysis...")
    response = requests.get(f"{BASE_URL}/visualizations/hometown-analysis")
    if response.status_code == 200:
        data = response.json()
        save_chart(data["image"], "hometown_analysis.png")
        print("PASS - Hometown analysis created")
    
    print("\n4. Testing Age Performance...")
    response = requests.get(f"{BASE_URL}/visualizations/age-performance")
    if response.status_code == 200:
        data = response.json()
        save_chart(data["image"], "age_performance.png")
        print("PASS - Age performance chart created")
    
    print("\n5. Testing Performance Categories...")
    response = requests.get(f"{BASE_URL}/visualizations/performance-categories")
    if response.status_code == 200:
        data = response.json()
        save_chart(data["image"], "performance_categories.png")
        print("PASS - Performance categories chart created")
    
    print("\n6. Testing Comprehensive Report...")
    response = requests.get(f"{BASE_URL}/visualizations/comprehensive-report")
    if response.status_code == 200:
        data = response.json()
        save_chart(data["image"], "comprehensive_report.png")
        print("PASS - Comprehensive report created")

if __name__ == "__main__":
    print("Testing Seaborn Visualization Endpoints...")
    test_visualizations()
    print("\nAll visualization tests completed!")
```

---

## 🔧 API Testing

### Using cURL

#### Create Student
```bash
curl -X POST "http://localhost:8001/api/v1/students" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "SV001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "hometown": "Hanoi",
    "math_score": 8.5,
    "literature_score": 7.5,
    "english_score": 9.0
  }'
```

#### Get Students
```bash
# All students
curl "http://localhost:8001/api/v1/students"

# With pagination
curl "http://localhost:8001/api/v1/students?skip=0&limit=10"

# Search
curl "http://localhost:8001/api/v1/students/search?query=John"
```

#### Update Student
```bash
curl -X PUT "http://localhost:8001/api/v1/students/1" \
  -H "Content-Type: application/json" \
  -d '{
    "math_score": 9.5,
    "literature_score": 8.5
  }'
```

#### Delete Student
```bash
curl -X DELETE "http://localhost:8001/api/v1/students/1"
```

### Using PowerShell

```powershell
# Create student
$body = @{
    student_id = "SV001"
    first_name = "John"
    last_name = "Doe"
    email = "john@example.com"
    math_score = 8.5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/v1/students" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

# Get students
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/students"

# Delete student
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/students/1" `
    -Method Delete
```

### Using Python requests

```python
import requests

# Create student
response = requests.post(
    "http://localhost:8001/api/v1/students",
    json={
        "student_id": "SV001",
        "first_name": "John",
        "last_name": "Doe"
    }
)

# Get students
response = requests.get("http://localhost:8001/api/v1/students")
students = response.json()

# Update student
response = requests.put(
    "http://localhost:8001/api/v1/students/1",
    json={"math_score": 9.5}
)

# Delete student
response = requests.delete("http://localhost:8001/api/v1/students/1")
```

---

## ✍️ Writing Tests

### Test Structure

```python
# tests/test_students.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_student():
    """Test creating a new student"""
    response = client.post(
        "/api/v1/students",
        json={
            "student_id": "SV001",
            "first_name": "John",
            "last_name": "Doe"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "SV001"
    assert data["first_name"] == "John"

def test_get_students():
    """Test getting all students"""
    response = client.get("/api/v1/students")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_student_not_found():
    """Test getting non-existent student"""
    response = client.get("/api/v1/students/99999")
    assert response.status_code == 404

def test_update_student():
    """Test updating student"""
    # First create a student
    create_response = client.post(
        "/api/v1/students",
        json={"student_id": "SV002", "first_name": "Jane", "last_name": "Doe"}
    )
    student_id = create_response.json()["id"]
    
    # Update the student
    update_response = client.put(
        f"/api/v1/students/{student_id}",
        json={"math_score": 9.5}
    )
    assert update_response.status_code == 200
    assert update_response.json()["math_score"] == 9.5

def test_delete_student():
    """Test deleting student"""
    # Create then delete
    create_response = client.post(
        "/api/v1/students",
        json={"student_id": "SV003", "first_name": "Bob", "last_name": "Smith"}
    )
    student_id = create_response.json()["id"]
    
    delete_response = client.delete(f"/api/v1/students/{student_id}")
    assert delete_response.status_code == 200
```

### Fixtures

```python
# tests/conftest.py

import pytest
from sqlmodel import Session, create_engine, SQLModel
from app.database import get_db
from app.main import app

@pytest.fixture(name="session")
def session_fixture():
    """Create test database session"""
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with test database"""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

---

## ✅ Best Practices

### 1. Test Organization
```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── test_api.py           # API endpoint tests
├── test_crud.py          # CRUD operation tests
├── test_services.py      # Service layer tests
└── test_models.py        # Model validation tests
```

### 2. Test Naming
```python
# Good names
def test_create_student_with_valid_data()
def test_update_student_score_updates_timestamp()
def test_delete_student_returns_404_if_not_found()

# Bad names
def test1()
def test_student()
def test_stuff()
```

### 3. Test Independence
```python
# Each test should be independent
def test_create_student():
    # Create student
    # Assert results
    # Clean up (or use fixtures)
    pass

# Don't rely on other tests
def test_update_student():
    # Don't assume test_create_student ran first
    # Create your own test data
    pass
```

### 4. Use Assertions
```python
# Good assertions
assert response.status_code == 200
assert len(students) > 0
assert student.math_score == 8.5

# With messages
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
```

### 5. Test Coverage
```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html # Windows
```

### 6. Continuous Testing
```bash
# Watch mode (requires pytest-watch)
ptw

# Run on file change
pytest-watch
```

---

## 📊 Test Results

### Expected Output
```
============================= test session starts =============================
collected 15 items

tests/test_api.py ............                                          [ 80%]
tests/test_crud.py ...                                                  [100%]

============================== 15 passed in 2.34s ==============================
```

### Coverage Report
```
Name                                Stmts   Miss  Cover
-------------------------------------------------------
app/__init__.py                         0      0   100%
app/main.py                            45      2    96%
app/database.py                        12      0   100%
app/crud/student.py                    78      5    94%
app/api/endpoints/students.py          92      8    91%
app/services/data_service.py           67      4    94%
-------------------------------------------------------
TOTAL                                 294     19    94%
```

---

**Last Updated**: October 5, 2025
**Version**: 1.0.0
