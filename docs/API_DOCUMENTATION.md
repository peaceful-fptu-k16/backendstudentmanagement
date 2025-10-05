# 📡 API Documentation

## 📋 Table of Contents
1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)

---

## 🎯 API Overview

### Base Information
```yaml
Base URL: http://localhost:8001
API Prefix: /api/v1
Version: 1.0.0
Protocol: HTTP/REST
Format: JSON
```

### API Characteristics
- ✅ RESTful design
- ✅ JSON request/response
- ✅ Automatic documentation (Swagger/ReDoc)
- ✅ Pagination support
- ✅ Filtering and sorting
- ✅ CORS enabled
- ✅ Request/response logging

### Interactive Documentation
```
Swagger UI:  http://localhost:8001/docs
ReDoc:       http://localhost:8001/redoc
OpenAPI Spec: http://localhost:8001/api/openapi.json
```

---

## 🔐 Authentication

**Current Version**: No authentication required (development mode)

**Future Implementation** (planned):
- JWT tokens
- API keys
- OAuth2

---

## 📌 Endpoints

### 1. Student Management

#### **GET /api/v1/students**
List students with pagination and filtering.

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number (1-indexed) |
| page_size | integer | No | 10 | Items per page (max 100) |
| search | string | No | - | Search in ID, name, email |
| hometown | string | No | - | Filter by hometown |
| min_average | float | No | - | Minimum average score (0-10) |
| max_average | float | No | - | Maximum average score (0-10) |
| sort_by | string | No | - | Sort field (student_id, average_score, etc) |
| sort_order | string | No | asc | Sort order (asc/desc) |

**Example Request:**
```bash
GET /api/v1/students?page=1&page_size=10&search=John&hometown=Hanoi&min_average=7.0
```

**Example Response:**
```json
{
  "items": [
    {
      "id": 1,
      "student_id": "SV001",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "email": "john@example.com",
      "birth_date": "2005-01-15",
      "hometown": "Hanoi",
      "math_score": 8.5,
      "literature_score": 7.5,
      "english_score": 9.0,
      "average_score": 8.33,
      "grade": "Excellent",
      "created_at": "2025-10-05T10:00:00",
      "updated_at": "2025-10-05T10:00:00"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 10,
  "total_pages": 5,
  "has_next": true,
  "has_prev": false
}
```

---

#### **POST /api/v1/students**
Create a new student.

**Request Body:**
```json
{
  "student_id": "SV001",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "birth_date": "2005-01-15",
  "hometown": "Hanoi",
  "math_score": 8.5,
  "literature_score": 7.5,
  "english_score": 9.0
}
```

**Required Fields:**
- `student_id` (string, 6-12 alphanumeric)
- `first_name` (string)
- `last_name` (string)

**Optional Fields:**
- `email` (string, valid email format)
- `birth_date` (date, YYYY-MM-DD)
- `hometown` (string)
- `math_score` (float, 0-10)
- `literature_score` (float, 0-10)
- `english_score` (float, 0-10)

**Response:**
```json
{
  "id": 1,
  "student_id": "SV001",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "email": "john@example.com",
  "birth_date": "2005-01-15",
  "hometown": "Hanoi",
  "math_score": 8.5,
  "literature_score": 7.5,
  "english_score": 9.0,
  "average_score": 8.33,
  "grade": "Excellent",
  "created_at": "2025-10-05T10:00:00",
  "updated_at": "2025-10-05T10:00:00"
}
```

**Status Codes:**
- `201 Created` - Student created successfully
- `400 Bad Request` - Invalid input data
- `409 Conflict` - Student ID already exists

---

#### **GET /api/v1/students/{student_id}**
Get a specific student by ID.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| student_id | integer | Yes | Database ID of the student |

**Example Request:**
```bash
GET /api/v1/students/1
```

**Response:**
```json
{
  "id": 1,
  "student_id": "SV001",
  "full_name": "John Doe",
  "email": "john@example.com",
  "hometown": "Hanoi",
  "math_score": 8.5,
  "literature_score": 7.5,
  "english_score": 9.0,
  "average_score": 8.33,
  "grade": "Excellent",
  "created_at": "2025-10-05T10:00:00",
  "updated_at": "2025-10-05T10:00:00"
}
```

**Status Codes:**
- `200 OK` - Student found
- `404 Not Found` - Student doesn't exist

---

#### **PUT /api/v1/students/{student_id}**
Update an existing student.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| student_id | integer | Yes | Database ID of the student |

**Request Body (partial update allowed):**
```json
{
  "math_score": 9.0,
  "literature_score": 8.5,
  "hometown": "Ho Chi Minh City"
}
```

**Response:**
```json
{
  "id": 1,
  "student_id": "SV001",
  "full_name": "John Doe",
  "math_score": 9.0,
  "literature_score": 8.5,
  "english_score": 9.0,
  "average_score": 8.83,
  "grade": "Excellent",
  "hometown": "Ho Chi Minh City",
  "updated_at": "2025-10-05T11:00:00"
}
```

**Status Codes:**
- `200 OK` - Student updated successfully
- `404 Not Found` - Student doesn't exist
- `400 Bad Request` - Invalid input data

---

#### **DELETE /api/v1/students/{student_id}**
Delete a student.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| student_id | integer | Yes | Database ID of the student |

**Example Request:**
```bash
DELETE /api/v1/students/1
```

**Response:**
```
204 No Content
```

**Status Codes:**
- `204 No Content` - Student deleted successfully
- `404 Not Found` - Student doesn't exist

---

#### **POST /api/v1/students/bulk-import**
Import multiple students from Excel or CSV file.

**Request:**
```
Content-Type: multipart/form-data

file: students.xlsx (or .csv)
```

**Excel/CSV Format:**
| student_id | first_name | last_name | email | hometown | math_score | literature_score | english_score |
|------------|------------|-----------|-------|----------|------------|------------------|---------------|
| SV001 | John | Doe | john@... | Hanoi | 8.5 | 7.5 | 9.0 |
| SV002 | Jane | Smith | jane@... | HCMC | 9.0 | 8.0 | 8.5 |

**Response:**
```json
{
  "total_rows": 100,
  "created": 95,
  "errors": 5,
  "error_details": [
    {
      "row": 15,
      "student_id": "SV015",
      "error": "Student SV015 already exists"
    },
    {
      "row": 23,
      "error": "Invalid email format"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Import completed (check errors array for partial failures)
- `400 Bad Request` - Invalid file format

---

### 2. Analytics

#### **GET /api/v1/analytics**
Get general analytics and statistics.

**Response:**
```json
{
  "total_students": 150,
  "average_age": 20.5,
  "average_scores": {
    "math": 7.5,
    "literature": 7.2,
    "english": 7.8,
    "overall": 7.5
  },
  "grade_distribution": {
    "Excellent": 45,
    "Good": 60,
    "Average": 35,
    "Below Average": 10
  },
  "score_distribution": {
    "0-5.5": 10,
    "5.5-7": 35,
    "7-8.5": 60,
    "8.5-10": 45
  },
  "hometown_distribution": {
    "Hanoi": 50,
    "HCMC": 45,
    "Danang": 30,
    "Haiphong": 25
  },
  "age_distribution": {
    "18": 20,
    "19": 35,
    "20": 40,
    "21": 35,
    "22": 20
  }
}
```

---

#### **GET /api/v1/analytics/summary**
Get comprehensive analytics summary with insights.

**Response:**
```json
{
  "overview": {
    "total_students": 150,
    "average_age": 20.5,
    "total_hometowns": 15
  },
  "academic_performance": {
    "average_scores": {
      "math": 7.5,
      "literature": 7.2,
      "english": 7.8
    },
    "grade_distribution": {
      "Excellent": 45,
      "Good": 60,
      "Average": 35,
      "Below Average": 10
    }
  },
  "demographics": {
    "hometown_distribution": {...},
    "age_distribution": {...}
  },
  "insights": {
    "strongest_subject": "English",
    "weakest_subject": "Literature",
    "excellence_rate": 30.0,
    "pass_rate": 93.33,
    "most_common_hometown": "Hanoi"
  }
}
```

---

### 3. Visualizations (Seaborn)

#### **GET /api/v1/visualizations/score-distribution**
Generate score distribution visualization.

**Response:**
```json
{
  "chart_type": "score_distribution",
  "image": "iVBORw0KGgoAAAANSUhEUg...",
  "format": "png",
  "encoding": "base64",
  "statistics": {
    "total_students": 150,
    "average_scores": {
      "math": 7.5,
      "literature": 7.2,
      "english": 7.8,
      "overall": 7.5
    }
  }
}
```

**To display the image:**
```html
<img src="data:image/png;base64,{image}" />
```

---

#### **GET /api/v1/visualizations/correlation-heatmap**
Generate correlation heatmap between subjects.

**Response:**
```json
{
  "chart_type": "correlation_heatmap",
  "image": "iVBORw0KGgoAAAANSUhEUg...",
  "format": "png",
  "encoding": "base64",
  "correlation_matrix": {
    "math_score": {
      "math_score": 1.0,
      "literature_score": 0.65,
      "english_score": 0.72
    },
    "literature_score": {
      "math_score": 0.65,
      "literature_score": 1.0,
      "english_score": 0.68
    },
    "english_score": {
      "math_score": 0.72,
      "literature_score": 0.68,
      "english_score": 1.0
    }
  }
}
```

---

#### **GET /api/v1/visualizations/comprehensive-report**
Get all visualizations in one request.

**Response:**
```json
{
  "score_distribution": {
    "chart_type": "score_distribution",
    "image": "...",
    "statistics": {...}
  },
  "correlation_analysis": {
    "chart_type": "correlation_heatmap",
    "image": "...",
    "correlation_matrix": {...}
  },
  "hometown_analysis": {
    "chart_type": "hometown_analysis",
    "image": "...",
    "statistics": {...}
  },
  "age_performance": {
    "chart_type": "age_performance",
    "image": "...",
    "statistics": {...}
  },
  "performance_categories": {
    "chart_type": "performance_categories",
    "image": "...",
    "category_distribution": {...}
  }
}
```

---

### 4. Export

#### **GET /api/v1/export**
Export students data in various formats.

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| format | string | No | excel | Format: excel, csv, xml |

**Example Requests:**
```bash
GET /api/v1/export?format=excel
GET /api/v1/export?format=csv
GET /api/v1/export?format=xml
```

**Response:**
- Excel: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- CSV: `text/csv`
- XML: `application/xml`

**Response Headers:**
```
Content-Disposition: attachment; filename=students.xlsx
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

---

### 5. Utility Endpoints

#### **GET /**
Root endpoint with API information.

**Response:**
```json
{
  "message": "Student Management System API",
  "version": "1.0.0",
  "docs_url": "/docs",
  "redoc_url": "/redoc",
  "api_prefix": "/api/v1"
}
```

---

#### **GET /health**
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1696502400.123,
  "version": "1.0.0"
}
```

---

## 📊 Request/Response Formats

### Pagination Response
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 10,
  "total_pages": 15,
  "has_next": true,
  "has_prev": false
}
```

### Student Object
```json
{
  "id": 1,
  "student_id": "SV001",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "email": "john@example.com",
  "birth_date": "2005-01-15",
  "hometown": "Hanoi",
  "math_score": 8.5,
  "literature_score": 7.5,
  "english_score": 9.0,
  "average_score": 8.33,
  "grade": "Excellent",
  "created_at": "2025-10-05T10:00:00",
  "updated_at": "2025-10-05T10:00:00"
}
```

### Grade Classification
| Grade | Average Score Range |
|-------|-------------------|
| Excellent | ≥ 8.5 |
| Good | 7.0 - 8.49 |
| Average | 5.5 - 6.99 |
| Below Average | < 5.5 |

---

## ⚠️ Error Handling

### Error Response Format
```json
{
  "detail": "Error message",
  "error_type": "ValidationError",
  "timestamp": 1696502400.123
}
```

### HTTP Status Codes
| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Resource deleted successfully |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

### Common Errors

#### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "math_score"],
      "msg": "ensure this value is less than or equal to 10",
      "type": "value_error.number.not_le"
    }
  ]
}
```

#### Not Found (404)
```json
{
  "detail": "Student with ID SV001 not found"
}
```

#### Conflict (409)
```json
{
  "detail": "Student with ID SV001 already exists"
}
```

---

## 🚦 Rate Limiting

**Current**: No rate limiting (development mode)

**Future Implementation**:
- 100 requests per minute per IP
- 1000 requests per hour per API key

---

## 📝 Examples

### cURL Examples

#### Create Student
```bash
curl -X POST "http://localhost:8001/api/v1/students" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "SV001",
    "first_name": "John",
    "last_name": "Doe",
    "math_score": 8.5,
    "literature_score": 7.5,
    "english_score": 9.0
  }'
```

#### Get Students
```bash
curl "http://localhost:8001/api/v1/students?page=1&page_size=10"
```

#### Update Student
```bash
curl -X PUT "http://localhost:8001/api/v1/students/1" \
  -H "Content-Type: application/json" \
  -d '{"math_score": 9.0}'
```

#### Delete Student
```bash
curl -X DELETE "http://localhost:8001/api/v1/students/1"
```

### Python Examples

```python
import requests

BASE_URL = "http://localhost:8001/api/v1"

# Create student
response = requests.post(
    f"{BASE_URL}/students",
    json={
        "student_id": "SV001",
        "first_name": "John",
        "last_name": "Doe",
        "math_score": 8.5
    }
)
print(response.json())

# Get students
response = requests.get(f"{BASE_URL}/students?page=1&page_size=10")
data = response.json()
print(f"Total: {data['total']}")
for student in data['items']:
    print(f"{student['student_id']}: {student['full_name']}")

# Get analytics
response = requests.get(f"{BASE_URL}/analytics")
analytics = response.json()
print(f"Total students: {analytics['total_students']}")
print(f"Average score: {analytics['average_scores']['overall']}")

# Get visualization
response = requests.get(f"{BASE_URL}/visualizations/score-distribution")
chart_data = response.json()
# Save image
import base64
image_bytes = base64.b64decode(chart_data['image'])
with open('chart.png', 'wb') as f:
    f.write(image_bytes)
```

---

**Last Updated**: October 5, 2025
**Version**: 1.0.0
