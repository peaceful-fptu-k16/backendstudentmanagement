# 🗄️ Database Schema Documentation

## 📋 Table of Contents
1. [Database Overview](#database-overview)
2. [Tables](#tables)
3. [Relationships](#relationships)
4. [Indexes](#indexes)
5. [Constraints](#constraints)
6. [Queries](#queries)

---

## 🎯 Database Overview

### Technology Stack
```yaml
Database: SQLite
ORM: SQLModel (based on SQLAlchemy + Pydantic)
Database File: students.db
Schema Version: 1.0.0
```

### Key Features
- ✅ Type-safe ORM with Pydantic validation
- ✅ Automatic schema migration
- ✅ Built-in validation
- ✅ Easy to test and mock
- ✅ Lightweight (SQLite)

---

## 📊 Tables

### `students` Table

Complete student information with academic scores.

#### Schema Definition

```python
# File: app/models/student.py

class Student(SQLModel, table=True):
    __tablename__ = "students"
    
    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Student Information
    student_id: str = Field(index=True, unique=True)
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    email: Optional[str] = Field(default=None)
    birth_date: Optional[date] = Field(default=None)
    hometown: Optional[str] = Field(default=None, index=True)
    
    # Academic Scores (0-10 scale)
    math_score: Optional[float] = Field(default=None, ge=0, le=10)
    literature_score: Optional[float] = Field(default=None, ge=0, le=10)
    english_score: Optional[float] = Field(default=None, ge=0, le=10)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

#### Column Specifications

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary key, auto-increment |
| `student_id` | VARCHAR | NO | - | Unique student identifier (6-12 chars) |
| `first_name` | VARCHAR | NO | - | Student's first name |
| `last_name` | VARCHAR | NO | - | Student's last name |
| `email` | VARCHAR | YES | NULL | Email address (validated format) |
| `birth_date` | DATE | YES | NULL | Date of birth |
| `hometown` | VARCHAR | YES | NULL | Student's hometown/city |
| `math_score` | FLOAT | YES | NULL | Math score (0.0 - 10.0) |
| `literature_score` | FLOAT | YES | NULL | Literature score (0.0 - 10.0) |
| `english_score` | FLOAT | YES | NULL | English score (0.0 - 10.0) |
| `created_at` | DATETIME | NO | NOW() | Record creation timestamp |
| `updated_at` | DATETIME | NO | NOW() | Last update timestamp |

#### SQL Schema

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR NOT NULL UNIQUE,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR,
    birth_date DATE,
    hometown VARCHAR,
    math_score FLOAT CHECK (math_score >= 0 AND math_score <= 10),
    literature_score FLOAT CHECK (literature_score >= 0 AND literature_score <= 10),
    english_score FLOAT CHECK (english_score >= 0 AND english_score <= 10),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_students_student_id ON students(student_id);
CREATE INDEX ix_students_first_name ON students(first_name);
CREATE INDEX ix_students_last_name ON students(last_name);
CREATE INDEX ix_students_hometown ON students(hometown);
```

---

## 🔗 Relationships

### Current Schema
Currently, the system has only one table (`students`).

### Future Extensions (Planned)

```sql
-- Classes table
CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_code VARCHAR NOT NULL UNIQUE,
    class_name VARCHAR NOT NULL,
    teacher_name VARCHAR,
    academic_year VARCHAR,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Student-Class relationship (many-to-many)
CREATE TABLE student_classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    enrollment_date DATE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    UNIQUE(student_id, class_id)
);

-- Courses table
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code VARCHAR NOT NULL UNIQUE,
    course_name VARCHAR NOT NULL,
    credits INTEGER,
    semester VARCHAR
);

-- Grades table (detailed scoring)
CREATE TABLE grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    score FLOAT CHECK (score >= 0 AND score <= 10),
    exam_date DATE,
    notes TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
```

---

## 🔍 Indexes

### Current Indexes

```sql
-- Primary Key Index (automatic)
PRIMARY KEY (id)

-- Unique Index on student_id
CREATE UNIQUE INDEX ix_students_student_id ON students(student_id);

-- Index on first_name for searching
CREATE INDEX ix_students_first_name ON students(first_name);

-- Index on last_name for searching
CREATE INDEX ix_students_last_name ON students(last_name);

-- Index on hometown for filtering
CREATE INDEX ix_students_hometown ON students(hometown);
```

### Index Usage

```python
# Queries that use indexes:

# 1. Find by student_id (UNIQUE INDEX)
SELECT * FROM students WHERE student_id = 'SV001';

# 2. Search by name (INDEX)
SELECT * FROM students WHERE first_name LIKE 'John%';
SELECT * FROM students WHERE last_name LIKE 'Doe%';

# 3. Filter by hometown (INDEX)
SELECT * FROM students WHERE hometown = 'Hanoi';

# 4. Combined search (uses multiple indexes)
SELECT * FROM students 
WHERE first_name LIKE 'John%' 
  AND hometown = 'Hanoi';
```

### Performance Benefits

| Query Type | Without Index | With Index | Improvement |
|------------|---------------|------------|-------------|
| Find by student_id | O(n) | O(log n) | ~100x faster |
| Search by name | O(n) | O(log n) | ~50x faster |
| Filter by hometown | O(n) | O(log n) | ~30x faster |

---

## ✅ Constraints

### Primary Key Constraint
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
```
- Ensures uniqueness
- Auto-incrementing
- Cannot be NULL

### Unique Constraint
```sql
student_id VARCHAR NOT NULL UNIQUE
```
- Each student_id must be unique
- Prevents duplicate students
- Enforced at database level

### Check Constraints
```sql
-- Score validation
math_score FLOAT CHECK (math_score >= 0 AND math_score <= 10)
literature_score FLOAT CHECK (literature_score >= 0 AND literature_score <= 10)
english_score FLOAT CHECK (english_score >= 0 AND english_score <= 10)
```

### Not Null Constraints
```sql
-- Required fields
id INTEGER NOT NULL
student_id VARCHAR NOT NULL
first_name VARCHAR NOT NULL
last_name VARCHAR NOT NULL
created_at DATETIME NOT NULL
updated_at DATETIME NOT NULL
```

### Application-Level Validation

```python
# File: app/models/student.py

class StudentBase(SQLModel):
    # Student ID validation
    @validator('student_id')
    def validate_student_id(cls, v):
        if not re.match(r'^[A-Za-z0-9]{6,12}$', v):
            raise ValueError('Student ID must be 6-12 alphanumeric characters')
        return v.upper()
    
    # Name validation
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    # Email validation
    @validator('email')
    def validate_email(cls, v):
        if v is not None and v.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError('Invalid email format')
            return v.strip()
        return v
```

---

## 🔍 Common Queries

### 1. Basic CRUD Operations

#### Create Student
```sql
INSERT INTO students (
    student_id, first_name, last_name, email, hometown,
    math_score, literature_score, english_score,
    created_at, updated_at
) VALUES (
    'SV001', 'John', 'Doe', 'john@example.com', 'Hanoi',
    8.5, 7.5, 9.0,
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);
```

#### Read Student
```sql
-- By ID
SELECT * FROM students WHERE id = 1;

-- By student_id
SELECT * FROM students WHERE student_id = 'SV001';

-- All students
SELECT * FROM students ORDER BY created_at DESC;
```

#### Update Student
```sql
UPDATE students 
SET math_score = 9.0, 
    literature_score = 8.5,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 1;
```

#### Delete Student
```sql
DELETE FROM students WHERE id = 1;
```

### 2. Search Queries

#### Search by Name
```sql
SELECT * FROM students 
WHERE first_name LIKE '%John%' 
   OR last_name LIKE '%Doe%'
ORDER BY last_name, first_name;
```

#### Search by Multiple Fields
```sql
SELECT * FROM students 
WHERE (
    student_id LIKE '%SV%' 
    OR first_name LIKE '%John%' 
    OR last_name LIKE '%Doe%'
    OR email LIKE '%john%'
)
ORDER BY student_id;
```

### 3. Filtering Queries

#### Filter by Hometown
```sql
SELECT * FROM students 
WHERE hometown = 'Hanoi'
ORDER BY student_id;
```

#### Filter by Score Range
```sql
SELECT * FROM students 
WHERE (math_score + literature_score + english_score) / 3.0 >= 8.0
ORDER BY (math_score + literature_score + english_score) / 3.0 DESC;
```

#### Filter by Grade
```sql
-- Excellent students (average >= 8.5)
SELECT * FROM students 
WHERE (math_score + literature_score + english_score) / 3.0 >= 8.5;

-- Good students (7.0 <= average < 8.5)
SELECT * FROM students 
WHERE (math_score + literature_score + english_score) / 3.0 >= 7.0
  AND (math_score + literature_score + english_score) / 3.0 < 8.5;
```

### 4. Aggregation Queries

#### Count Students
```sql
-- Total students
SELECT COUNT(*) AS total FROM students;

-- Students by hometown
SELECT hometown, COUNT(*) AS count 
FROM students 
GROUP BY hometown 
ORDER BY count DESC;

-- Students by grade
SELECT 
    CASE 
        WHEN (math_score + literature_score + english_score) / 3.0 >= 8.5 THEN 'Excellent'
        WHEN (math_score + literature_score + english_score) / 3.0 >= 7.0 THEN 'Good'
        WHEN (math_score + literature_score + english_score) / 3.0 >= 5.5 THEN 'Average'
        ELSE 'Below Average'
    END AS grade,
    COUNT(*) AS count
FROM students
GROUP BY grade
ORDER BY count DESC;
```

#### Average Scores
```sql
-- Overall averages
SELECT 
    AVG(math_score) AS avg_math,
    AVG(literature_score) AS avg_literature,
    AVG(english_score) AS avg_english,
    AVG((math_score + literature_score + english_score) / 3.0) AS avg_overall
FROM students;

-- Averages by hometown
SELECT 
    hometown,
    AVG(math_score) AS avg_math,
    AVG(literature_score) AS avg_literature,
    AVG(english_score) AS avg_english,
    COUNT(*) AS student_count
FROM students
GROUP BY hometown
ORDER BY avg_overall DESC;
```

#### Top Students
```sql
-- Top 10 students by average score
SELECT 
    student_id,
    first_name || ' ' || last_name AS full_name,
    (math_score + literature_score + english_score) / 3.0 AS average_score
FROM students
WHERE math_score IS NOT NULL 
  AND literature_score IS NOT NULL 
  AND english_score IS NOT NULL
ORDER BY average_score DESC
LIMIT 10;
```

### 5. Pagination Queries

```sql
-- Page 1 (first 10 students)
SELECT * FROM students 
ORDER BY student_id 
LIMIT 10 OFFSET 0;

-- Page 2 (next 10 students)
SELECT * FROM students 
ORDER BY student_id 
LIMIT 10 OFFSET 10;

-- Generic pagination
-- page_size = 10, page_number = 3
-- offset = (page_number - 1) * page_size = 20
SELECT * FROM students 
ORDER BY student_id 
LIMIT 10 OFFSET 20;
```

### 6. Complex Queries

#### Students with Complete Scores
```sql
SELECT * FROM students 
WHERE math_score IS NOT NULL 
  AND literature_score IS NOT NULL 
  AND english_score IS NOT NULL
ORDER BY (math_score + literature_score + english_score) / 3.0 DESC;
```

#### Students with Missing Scores
```sql
SELECT 
    student_id,
    first_name || ' ' || last_name AS full_name,
    CASE WHEN math_score IS NULL THEN 'Missing Math' ELSE '' END AS math_status,
    CASE WHEN literature_score IS NULL THEN 'Missing Literature' ELSE '' END AS lit_status,
    CASE WHEN english_score IS NULL THEN 'Missing English' ELSE '' END AS eng_status
FROM students
WHERE math_score IS NULL 
   OR literature_score IS NULL 
   OR english_score IS NULL;
```

#### Score Distribution
```sql
SELECT 
    CASE 
        WHEN (math_score + literature_score + english_score) / 3.0 < 5.5 THEN '0-5.5'
        WHEN (math_score + literature_score + english_score) / 3.0 < 7.0 THEN '5.5-7'
        WHEN (math_score + literature_score + english_score) / 3.0 < 8.5 THEN '7-8.5'
        ELSE '8.5-10'
    END AS score_range,
    COUNT(*) AS count
FROM students
WHERE math_score IS NOT NULL 
  AND literature_score IS NOT NULL 
  AND english_score IS NOT NULL
GROUP BY score_range
ORDER BY score_range;
```

---

## 🔄 Database Migrations

### Current Approach
- Automatic table creation on first run
- Schema managed by SQLModel
- No explicit migrations (SQLite auto-schema)

### Migration Code
```python
# File: app/database.py

from sqlmodel import SQLModel, create_engine
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

def create_db_and_tables():
    """Create all tables"""
    SQLModel.metadata.create_all(engine)
```

### Future Migration Strategy
For production with PostgreSQL/MySQL, use Alembic:

```bash
# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📊 Database Statistics

### Typical Data Volumes
```
Students: 100 - 10,000 records
Database Size: ~1-10 MB
Query Performance: < 50ms average
```

### Optimization Tips
1. **Use Indexes**: Already implemented on key fields
2. **Pagination**: Always use LIMIT and OFFSET
3. **Selective Queries**: Only select needed columns
4. **Batch Operations**: Use bulk insert for imports
5. **Cache Results**: Application-level caching implemented

---

## 🛠️ Database Maintenance

### Backup
```bash
# Copy database file
cp students.db students_backup_2025-10-05.db

# Using SQLite backup
sqlite3 students.db ".backup students_backup.db"
```

### Vacuum (Optimize)
```sql
-- Reclaim unused space and optimize
VACUUM;

-- Analyze for query optimization
ANALYZE;
```

### Integrity Check
```sql
-- Check database integrity
PRAGMA integrity_check;

-- Check foreign keys (when implemented)
PRAGMA foreign_key_check;
```

---

## 📝 Database Access Patterns

### Session Management
```python
# File: app/core/dependencies.py

def get_db():
    """Database dependency"""
    with Session(engine) as session:
        yield session
        # Automatic cleanup

# Usage in endpoint
@router.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.exec(select(Student)).all()
    return students
```

### Transaction Management
```python
# Explicit transaction
with Session(engine) as session:
    try:
        # Multiple operations
        student1 = Student(...)
        student2 = Student(...)
        
        session.add(student1)
        session.add(student2)
        
        # Commit all or nothing
        session.commit()
    except Exception as e:
        # Automatic rollback
        session.rollback()
        raise
```

---

**Last Updated**: October 5, 2025
**Version**: 1.0.0
