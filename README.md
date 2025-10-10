# 🎓 Student Management System - Backend API

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com)
[![SQLModel](https://img.shields.io/badge/SQLModel-0.0.14-r## 📚 Documentation

- **🎨 Seaborn Integration**: `SEABORN_QUICKSTART.md` | `SEABORN_GUIDE.md`
- **🐼 Pandas Integration**: `PANDAS_INTEGRATION_GUIDE.md`
- **📖 Daily Logging System**: `docs/DAILY_LOGGING_SYSTEM.md`
- **📊 Logging Report**: `docs/LOGGING_REPORT.md`
- **📈 Crawler Report Guide**: `CRAWLER_REPORT_GUIDE.md` ⭐ NEW
- **📊 20 Charts Guide**: `CHART_GUIDE.md` ⭐ NEW - Complete guide for all 20 charts
- **🔄 Update Summary**: `UPDATE_SUMMARY.md` ⭐ NEW
- **🔧 GitHub Copilot Instructions**: `.github/copilot/instructions.md`s://sqlmodel.tiangolo.com)
[![XML](https://img.shields.io/badge/Response-XML-orange)](https://www.w3.org/XML/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.1.0-brightgreen.svg)](README.md)

A comprehensive **FastAPI-based backend system** for managing student records with advanced logging, analytics, comprehensive reporting, and data processing capabilities.

## ⚠️ **IMPORTANT: API now returns XML instead of JSON!**

**Version 2.0.0** - All API endpoints now return **XML format** responses.  
**Version 2.1.0** - Added comprehensive report generation with 10 charts and sample data import! ⭐  
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
- 📋 **Comprehensive Reports** - Auto-generated Excel reports with 20+ charts (NEW!)
- 🎯 **Sample Data Import** - 100 pre-configured Vietnamese students for testing (NEW!)

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone <repository-url>
cd student-management-backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Import 100 sample students (optional)
python scripts/import_sample_students.py

# 4. Start development server
python scripts/run.py

# 5. Access API documentation
# Open http://localhost:8001/docs

# 6. Generate comprehensive report (optional)
# POST http://localhost:8001/api/v1/crawler/generate-report?limit=100
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
│   │   ├── students.py   # Student CRUD operations
│   │   ├── analytics.py  # Analytics endpoints
│   │   ├── crawler.py    # Crawler + Report generation ⭐ NEW
│   │   └── export.py     # Export functionality
│   ├── core/              # ⚙️  Core utilities (config, logging, db)
│   ├── crud/              # 🗄️  Database operations
│   ├── models/            # 📊 Data models (SQLModel)
│   ├── services/          # 🔧 Business logic services
│   │   ├── crawler_service.py
│   │   ├── data_service.py
│   │   ├── export_service.py
│   │   └── report_generator_service.py  ⭐ NEW (646 lines)
│   ├── utils/             # 🛠️  Utilities (XML builders, serialization)
│   └── main.py            # 🎯 FastAPI application entry
├── data/                  # 📦 Sample data ⭐ NEW
│   └── sample_students_100.json  # 100 Vietnamese students
├── docs/                  # 📖 Documentation files
├── scripts/               # 🛠️  Utility scripts
│   ├── run.py            # Start server
│   ├── import_sample_students.py  ⭐ NEW (Import 100 students)
│   ├── test_crawler_with_reports.py
│   ├── quick_test_report.py
│   ├── check_db.py
│   └── ...
├── tests/                 # 🧪 Test files
├── logs/                  # 📊 Daily logging (auto-created)
├── reports/               # 📈 Auto-generated reports ⭐ NEW
│   └── report_YYYYMMDD_HHMMSS/
│       ├── students_data.xlsx      # Excel with 6 sheets
│       ├── summary.html            # HTML summary
│       └── *.png                   # 10 charts
├── requirements.txt       # 📦 Python dependencies
├── CRAWLER_REPORT_GUIDE.md  ⭐ NEW
└── UPDATE_SUMMARY.md        ⭐ NEW
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
POST   /api/v1/crawler/crawl        # Crawl data with report generation
POST   /api/v1/crawler/crawl-and-import     # Crawl, import & generate report
POST   /api/v1/crawler/generate-report      # Generate comprehensive report (10 charts + Excel)
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

reports/                  # Auto-generated reports (NEW!)
└── report_20251010_123045/
    ├── students_data.xlsx         # Excel with 6 sheets
    ├── summary.html               # HTML summary
    ├── 01_score_distribution.png  # 10 visualization charts
    ├── 02_grade_distribution.png
    └── ...

data/                     # Sample data (NEW!)
└── sample_students_100.json  # 100 pre-configured students
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
# Import sample data
python scripts/import_sample_students.py          # Import 100 students
python scripts/import_sample_students.py --clear  # Clear DB and reimport

# Run basic tests
python tests/test_api.py

# Test specific functionality
python tests/simple_test.py

# Test report generation
python scripts/test_crawler_with_reports.py
python scripts/quick_test_report.py

# Check database
python scripts/check_db.py
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
- **� Crawler Report Guide**: `CRAWLER_REPORT_GUIDE.md` ⭐ NEW
- **🔄 Update Summary**: `UPDATE_SUMMARY.md` ⭐ NEW
- **�🔧 GitHub Copilot Instructions**: `.github/copilot/instructions.md`

## 🎨 Visualization Dashboard

Open `visualization_dashboard.html` in your browser for an interactive dashboard with all Seaborn charts!

```bash
# Start server
python scripts/run.py

# Open dashboard in browser
start visualization_dashboard.html
```

## 📊 Comprehensive Report Generation (NEW!)

The system now automatically generates comprehensive reports with **10 charts** and **Excel files**:

### 📈 Report Contents:
- **Excel File** with 6 sheets:
  - 📝 Students (complete data)
  - 📊 Statistics (summary metrics)
  - 📊 Grade Distribution
  - 🌍 Hometown Analysis
  - 🏆 Top Performers
  - 📐 Subject Analysis

- **20 Visualization Charts**:
  1. 📊 Score Distribution (3-panel histogram)
  2. 🥧 Grade Distribution (pie chart)
  3. 📊 Subject Comparison (bar chart)
  4. 🔥 Correlation Heatmap
  5. 🌍 Hometown Performance (top 15)
  6. 📦 Score Boxplot
  7. 🏆 Top 10 Students
  8. 🎻 Violin Plot
  9. 👥 Age Performance (if available)
  10. 📊 Grade by Hometown (stacked bar)
  11. 📊 **Score Range Analysis** ⭐ NEW
  12. 📊 **Avg Score by Hometown** ⭐ NEW
  13. 📈 **Score Density Plot** ⭐ NEW
  14. 🎯 **Performance Radar** ⭐ NEW
  15. 🔢 **Score Scatter Matrix** ⭐ NEW
  16. 🍩 **Grade Count Donut** ⭐ NEW
  17. 📈 **Subject Line Comparison** ⭐ NEW
  18. 📊 **Cumulative Distribution** ⭐ NEW
  19. 🔥 **Student Performance Heatmap** ⭐ NEW
  20. 📊 **Statistical Summary Dashboard** ⭐ NEW

### 🚀 Generate Report:
```bash
# Via API
POST http://localhost:8001/api/v1/crawler/generate-report?limit=100

# Or use test script
python scripts/quick_test_report.py
```

Reports are saved in `reports/report_YYYYMMDD_HHMMSS/` folder.

## 🎯 Sample Data Management (NEW!)

### 📥 Import Sample Data

Import 100 pre-configured Vietnamese students instantly:

```bash
# Import 100 students (skip duplicates)
python scripts/import_sample_students.py

# Clear database and import fresh data
python scripts/import_sample_students.py --clear
```

**Current Sample Data Features:**
- ✅ 100 students with IDs: SV0001 - SV0100
- ✅ Vietnamese names with proper accents
- ✅ Email format: `firstnamelastnamesvXXXX@university.edu.vn` (no accents, includes student ID)
- ✅ Northern region focused (50% Hà Nội, 30% Northern cities, 20% other regions)
- ✅ Realistic birth dates: 2002-2005
- ✅ Score distribution focused on average (6.0-7.5):
  - 8% Grade A (9.0-10.0) - Excellent students
  - 22% Grade B (8.0-8.9) - Good students
  - 45% Grade C (6.0-7.9) - Average students (concentrated)
  - 18% Grade D (4.0-5.9) - Below average students
  - 7% Grade F (0-3.9) - Failing students
- ✅ All 3 subjects with varied performance (Math, Literature, English)

### 🎨 Generate New Sample Data

Customize and generate new sample data with your own requirements:

```bash
# Generate new 100 students with current settings
python scripts/generate_beautiful_students.py
```

**Customization Options:**

Edit `scripts/generate_beautiful_students.py` to customize:

1. **Score Distribution** (lines 50-80):
   ```python
   # Adjust percentages for each grade level
   if rand < 0.08:  # 8% Grade A
   elif rand < 0.30:  # 22% Grade B
   elif rand < 0.75:  # 45% Grade C (average)
   # ... etc
   ```

2. **Hometown Distribution** (lines 34-44):
   ```python
   # Edit city lists and weights
   hometowns_northern = ["Hà Nội", "Hải Phòng", ...]  # Northern cities
   hometowns_other = ["TP.HCM", "Đà Nẵng", ...]       # Other regions
   hometowns = hometowns_northern * 4 + hometowns_other  # 80% North, 20% Other
   ```

3. **Name Lists** (lines 11-31):
   ```python
   first_names_male = ["Minh", "Hoàng", "Nam", ...]
   first_names_female = ["Linh", "Hương", "Lan", ...]
   last_names = ["Nguyễn", "Trần", "Lê", ...]
   ```

4. **Birth Date Range** (lines 82-87):
   ```python
   start_date = date(2002, 1, 1)
   end_date = date(2005, 12, 31)
   ```

**After customization:**
```bash
# 1. Generate new data
python scripts/generate_beautiful_students.py

# 2. Check statistics in output
# 3. Import to database
python scripts/import_sample_students.py --clear
```

### 📊 Sample Data Statistics

After generating, you'll see statistics like:
```
📊 Statistics:
   Excellent (9.0+): 8 (2.7%)
   Good (8.0-8.9): 55 (18.3%)
   Average (6.5-7.9): 149 (49.7%) ← Concentrated here
   Below Avg (5.0-6.4): 62 (20.7%)
   Poor (<5.0): 26 (8.7%)

🌍 Top 5 Hometowns:
   Hà Nội: 30 students (30.0%)
   Vĩnh Phúc: 8 students (8.0%)
   Quảng Ninh: 7 students (7.0%)
   ...
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
- 📊 **Reports**: Check `reports/` directory for generated reports

## 🎯 Quick Tips

### Generate Full Report
```bash
# 1. Import sample data
python scripts/import_sample_students.py

# 2. Start server
python scripts/run.py

# 3. Generate report (in another terminal)
# POST http://localhost:8001/api/v1/crawler/generate-report?limit=100
```

### Test Report Generation
```bash
python scripts/quick_test_report.py
```

### Reset Database
```bash
python scripts/import_sample_students.py --clear
```

### Check Database Status
```bash
python scripts/check_db.py
```

---

**🎯 Built with FastAPI, SQLModel, and ❤️ for education management**

**✨ Version 2.1.0** - Now with comprehensive reporting and sample data import!
