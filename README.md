# 🎓 Student Management System - Backend API

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com)
[![SQLModel](https://img.shields.io/badge/SQLModel-0.0.14-red)](https://sqlmodel.tiangolo.com)
[![XML](https://img.shields.io/badge/Response-XML-orange)](https://www.w3.org/XML/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive **FastAPI-based backend system** for managing student records with advanced logging, analytics, and data processing capabilities.

## ⚠️ **IMPORTANT: API now returns XML instead of JSON!**

**Version 2.0.0** - All API endpoints now return **XML format** responses.  
📖 Read [XML_API_MIGRATION.md](XML_API_MIGRATION.md) for migration guide.

## ✨ Features

- 🚀 **Modern FastAPI** - Async API with automatic documentation
- 🗄️ **SQLModel ORM** - Type-safe database operations
- 📊 **Advanced Analytics** - Student performance insights with Pandas
- 🎨 **Seaborn Visualizations** - Beautiful statistical charts and graphs
- 📝 **Daily Logging** - Structured logging with daily folders
- 📤 **Data Export** - Excel, CSV, XML export formats
- 🌐 **Web Scraping** - Extract data from external sources
- 🔄 **CORS Support** - Ready for frontend integration
- 📈 **Performance Monitoring** - Request timing and metrics
- 🔄 **XML Responses** - All endpoints return XML format (NEW in v2.0)

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone <repository-url>
cd student-management-backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start development server
python scripts/run.py

# 4. Access API documentation
# Open http://localhost:8000/docs

# 5. Test XML responses
python test_xml_api.py
```

## 🔄 XML Response Format

All API endpoints now return XML instead of JSON:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<students>
  <pagination>
    <total>100</total>
    <page>1</page>
  </pagination>
  <items>
    <student>
      <id>1</id>
      <student_id>SV001</student_id>
      <full_name>John Doe</full_name>
      <average_score>8.33</average_score>
    </student>
  </items>
</students>
```

📖 See [XML_SUMMARY.md](XML_SUMMARY.md) for complete examples.

## 🏗️ Project Structure

```
student-management-backend/
├── app/                    # 🚀 Main application
│   ├── api/endpoints/     # 🛣️  API route handlers (XML responses)
│   ├── core/              # ⚙️  Core utilities (config, logging, db)
│   ├── crud/              # 🗄️  Database operations
│   ├── models/            # 📊 Data models (SQLModel)
│   ├── services/          # 🔧 Business logic services
│   ├── utils/             # 🛠️  Utilities (XML builders, serialization)
│   └── main.py            # 🎯 FastAPI application entry
├── docs/                  # 📖 Documentation files
├── scripts/               # 🛠️  Utility scripts
├── tests/                 # 🧪 Test files
├── logs/                  # 📊 Daily logging (auto-created)
└── requirements.txt       # 📦 Python dependencies
```

## 🌐 API Endpoints

### Core Endpoints
```
GET    /                            # Root endpoint
GET    /health                      # Health check
GET    /docs                        # Interactive API docs (Swagger)
GET    /redoc                       # Alternative API docs
```

### Student Management
```
GET    /api/v1/students             # List students (paginated)
POST   /api/v1/students             # Create student
GET    /api/v1/students/{id}        # Get student by ID
PUT    /api/v1/students/{id}        # Update student
DELETE /api/v1/students/{id}        # Delete student
POST   /api/v1/students/bulk-import # Import from Excel/CSV
```

### Analytics & Reports
```
GET    /api/v1/analytics            # General analytics
GET    /api/v1/analytics/summary    # Summary statistics
GET    /api/v1/analytics/score-comparison    # Score analysis
GET    /api/v1/analytics/hometown-analysis   # Geographic insights
GET    /api/v1/export               # Export data (Excel/CSV/XML)
```

### Visualizations (Seaborn) 🎨
```
GET    /api/v1/visualizations/score-distribution      # Score distribution charts
GET    /api/v1/visualizations/correlation-heatmap     # Correlation matrix
GET    /api/v1/visualizations/hometown-analysis       # Hometown insights
GET    /api/v1/visualizations/age-performance         # Age vs performance
GET    /api/v1/visualizations/performance-categories  # Performance categories
GET    /api/v1/visualizations/comprehensive-report    # All charts
GET    /api/v1/visualizations/info                    # Visualization info
```

## 📊 Student Data Model

```json
{
  "student_id": "SV240001",
  "first_name": "John",
  "last_name": "Doe", 
  "email": "john@example.com",
  "birth_date": "2000-01-15",
  "hometown": "New York",
  "math_score": 8.5,
  "literature_score": 7.0,
  "english_score": 9.0,
  
  // Auto-computed fields
  "full_name": "John Doe",
  "average_score": 8.17,
  "grade": "Excellent"
}
```

**Subjects (3 môn học):**
- 📐 **Math** (Toán) - Score 0-10
- 📖 **Literature** (Văn) - Score 0-10
- 🗣️ **English** (Tiếng Anh) - Score 0-10

## 🛠️ Development

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.database import create_db_and_tables; create_db_and_tables()"

# Start development server
python scripts/run.py
```

### Environment Configuration
```python
# app/core/config.py
DATABASE_URL = "sqlite:///./students.db"  # Development database
API_V1_STR = "/api/v1"                    # API prefix
PROJECT_NAME = "Student Management API"    # API title
```

## 📈 Advanced Logging

The system features daily logging with structured JSON format:

```
logs/
├── 2025-09-29/           # Daily folder
│   ├── api.log          # API requests/responses
│   ├── database.log     # Database operations
│   ├── export.log       # Export operations
│   └── errors.log       # Error tracking
└── 2025-09-30/          # Next day folder
```

**Log Format Example:**
```json
{
  "event": "api_request",
  "timestamp": "2025-09-29T10:15:30.123456",
  "method": "POST",
  "path": "/api/v1/students",
  "status_code": 201,
  "duration_ms": 45.67,
  "remote_addr": "127.0.0.1"
}
```

## 🧪 Testing

```bash
# Run basic tests
python tests/test_api.py

# Test specific functionality
python tests/simple_test.py

# Check logging system
python tests/test_logging.py
```

## 🐳 Docker Deployment

```bash
# Using Docker Compose
docker-compose up --build

# Manual Docker build
docker build -t student-management .
docker run -p 8000:8000 student-management
```

## 📚 Documentation

- **🎨 Seaborn Integration**: `SEABORN_QUICKSTART.md` | `SEABORN_GUIDE.md`
- **🐼 Pandas Integration**: `PANDAS_INTEGRATION_GUIDE.md`
- **📖 Daily Logging System**: `docs/DAILY_LOGGING_SYSTEM.md`
- **📊 Logging Report**: `docs/LOGGING_REPORT.md`
- **🔧 GitHub Copilot Instructions**: `.github/copilot/instructions.md`

## 🎨 Visualization Dashboard

Open `visualization_dashboard.html` in your browser for an interactive dashboard with all Seaborn charts!

```bash
# Start server
python scripts/run.py

# Open dashboard in browser
start visualization_dashboard.html
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 **Issues**: GitHub Issues
- 📖 **Documentation**: Check `/docs` folder
- 💬 **API Testing**: Visit `/docs` endpoint
- 🔍 **Logs**: Check `logs/` directory for debugging

---

**🎯 Built with FastAPI, SQLModel, and ❤️ for education management**
