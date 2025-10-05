# 🔄 Code Flow Documentation

## 📋 Table of Contents
1. [Request Lifecycle](#request-lifecycle)
2. [CRUD Operations Flow](#crud-operations-flow)
3. [Service Layer Flow](#service-layer-flow)
4. [Middleware Processing](#middleware-processing)
5. [Error Handling Flow](#error-handling-flow)
6. [Caching Flow](#caching-flow)

---

## 🔄 Request Lifecycle

### Complete Request Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLIENT REQUEST                                           │
│    HTTP Request → http://localhost:8001/api/v1/students    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. FASTAPI APPLICATION (app/main.py)                        │
│    • Receives request                                       │
│    • Matches route                                          │
│    • Prepares for middleware chain                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. MIDDLEWARE CHAIN                                         │
│    ┌─────────────────────────────────────────────────────┐ │
│    │ A. TrustedHost Middleware                           │ │
│    │    - Validates Host header                          │ │
│    └─────────────────────────────────────────────────────┘ │
│                         ↓                                   │
│    ┌─────────────────────────────────────────────────────┐ │
│    │ B. CORS Middleware                                  │ │
│    │    - Checks origin                                  │ │
│    │    - Sets CORS headers                              │ │
│    └─────────────────────────────────────────────────────┘ │
│                         ↓                                   │
│    ┌─────────────────────────────────────────────────────┐ │
│    │ C. Custom Logging Middleware                        │ │
│    │    - Logs request details                           │ │
│    │    - Starts timing                                  │ │
│    │    - Captures IP, user-agent                        │ │
│    └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. ROUTE MATCHING                                           │
│    • FastAPI router finds matching endpoint                 │
│    • Loads endpoint function                                │
│    • Prepares dependency injection                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. DEPENDENCY INJECTION                                     │
│    ┌─────────────────────────────────────────────────────┐ │
│    │ get_db() - Database Session                         │ │
│    │   • Creates new session                             │ │
│    │   • Yields session to endpoint                      │ │
│    │   • Ensures cleanup after request                   │ │
│    └─────────────────────────────────────────────────────┘ │
│    ┌─────────────────────────────────────────────────────┐ │
│    │ PaginationParams - Query parameters                 │ │
│    │   • Extracts page, page_size                        │ │
│    │   • Validates values                                │ │
│    └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. REQUEST VALIDATION                                       │
│    • Pydantic validates request body                        │
│    • Type checking                                          │
│    • Custom validators run                                  │
│    • Raises ValidationError if invalid                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. ENDPOINT FUNCTION                                        │
│    • Executes endpoint logic                                │
│    • Calls service layer if needed                          │
│    • Calls CRUD layer                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. RESPONSE FORMATTING                                      │
│    • Converts to response schema                            │
│    • Serializes to JSON                                     │
│    • Sets status code                                       │
│    • Sets response headers                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 9. MIDDLEWARE CLEANUP                                       │
│    • Logs response details                                  │
│    • Calculates execution time                              │
│    • Adds X-Process-Time header                             │
│    • Logs to daily log file                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 10. CLIENT RESPONSE                                         │
│     • HTTP response with status code                        │
│     • JSON body                                             │
│     • Response headers                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 CRUD Operations Flow

### 1. CREATE Operation

**File**: `app/api/endpoints/students.py` → `app/crud/student.py`

```python
# Step 1: Client Request
POST /api/v1/students
Content-Type: application/json
{
  "student_id": "SV001",
  "first_name": "John",
  "last_name": "Doe",
  "math_score": 8.5,
  "literature_score": 7.5,
  "english_score": 9.0,
  "email": "john@example.com",
  "hometown": "Hanoi"
}

# Step 2: Endpoint Function (students.py)
@router.post("", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    # 2a. Pydantic validates input
    # 2b. Dependency injection provides db session
    
    # 2c. Handle full_name vs first_name/last_name
    first_name = student.first_name
    last_name = student.last_name
    
    # 2d. Create StudentBase for database
    student_data = StudentBase(
        student_id=student.student_id,
        first_name=first_name,
        last_name=last_name,
        email=student.email,
        # ... other fields
    )
    
    # 2e. Call CRUD layer
    db_student = student_crud.create(db=db, obj_in=student_data)
    
    # 2f. Format response
    return StudentResponse(
        **db_student.dict(),
        full_name=db_student.get_full_name(),
        average_score=db_student.get_average_score(),
        grade=db_student.get_grade()
    )

# Step 3: CRUD Layer (crud/student.py)
def create(self, db: Session, *, obj_in: StudentCreate) -> Student:
    start_time = time.time()
    
    # 3a. Log operation start
    logger.info(f"Creating student: {obj_in.student_id}")
    
    # 3b. Check for duplicate
    existing = self.get_by_student_id(db, student_id=obj_in.student_id)
    if existing:
        raise ValueError(f"Student {obj_in.student_id} already exists")
    
    # 3c. Create model instance
    db_obj = Student.from_orm(obj_in)
    db_obj.created_at = datetime.now()
    db_obj.updated_at = datetime.now()
    
    # 3d. Add to session and commit
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # 3e. Log operation completion
    duration = time.time() - start_time
    structured_logger.log_database_query(
        operation="INSERT",
        table="students",
        duration=duration,
        record_count=1
    )
    
    # 3f. Clear cache
    self._clear_cache_pattern("students_")
    
    return db_obj

# Step 4: Response to Client
HTTP/1.1 201 Created
X-Process-Time: 0.0234
Content-Type: application/json

{
  "id": 1,
  "student_id": "SV001",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "email": "john@example.com",
  "hometown": "Hanoi",
  "math_score": 8.5,
  "literature_score": 7.5,
  "english_score": 9.0,
  "average_score": 8.33,
  "grade": "Excellent",
  "created_at": "2025-10-05T10:30:00",
  "updated_at": "2025-10-05T10:30:00"
}
```

### 2. READ Operation (List with Pagination)

```python
# Step 1: Client Request
GET /api/v1/students?page=1&page_size=10&search=John&hometown=Hanoi

# Step 2: Endpoint (students.py)
@router.get("", response_model=PaginatedResponse[StudentResponse])
def get_students(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = None,
    hometown: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # 2a. Extract parameters
    # pagination.page = 1
    # pagination.page_size = 10
    # search = "John"
    # hometown = "Hanoi"
    
    # 2b. Call CRUD layer
    students, total = student_crud.get_multi(
        db=db,
        skip=pagination.offset,  # 0
        limit=pagination.page_size,  # 10
        search=search,
        hometown=hometown
    )
    
    # 2c. Format each student
    student_responses = []
    for student in students:
        response = StudentResponse(
            **student.dict(),
            full_name=student.get_full_name(),
            average_score=student.get_average_score(),
            grade=student.get_grade()
        )
        student_responses.append(response)
    
    # 2d. Calculate pagination metadata
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    
    # 2e. Return paginated response
    return PaginatedResponse(
        items=student_responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1
    )

# Step 3: CRUD Layer
def get_multi(
    self,
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    hometown: Optional[str] = None,
    # ... other filters
) -> tuple[List[Student], int]:
    
    # 3a. Check cache
    cache_key = f"students_{skip}_{limit}_{search}_{hometown}"
    cached = self._get_from_cache(cache_key)
    if cached:
        return cached
    
    # 3b. Build query
    query = select(Student)
    
    # 3c. Apply filters
    filters = []
    if search:
        search_filter = or_(
            Student.student_id.ilike(f"%{search}%"),
            Student.first_name.ilike(f"%{search}%"),
            Student.last_name.ilike(f"%{search}%"),
            Student.email.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if hometown:
        filters.append(Student.hometown == hometown)
    
    if filters:
        query = query.where(and_(*filters))
    
    # 3d. Get total count
    count_query = select(func.count()).select_from(Student)
    if filters:
        count_query = count_query.where(and_(*filters))
    total = db.exec(count_query).one()
    
    # 3e. Apply pagination
    query = query.offset(skip).limit(limit)
    
    # 3f. Execute query
    students = db.exec(query).all()
    
    # 3g. Cache result
    result = (students, total)
    self._set_cache(cache_key, result)
    
    # 3h. Log query
    structured_logger.log_database_query(
        operation="SELECT",
        table="students",
        duration=duration,
        record_count=len(students)
    )
    
    return result

# Step 4: Response
{
  "items": [
    {
      "id": 1,
      "student_id": "SV001",
      "full_name": "John Doe",
      "average_score": 8.33,
      // ... other fields
    },
    // ... more students
  ],
  "total": 45,
  "page": 1,
  "page_size": 10,
  "total_pages": 5,
  "has_next": true,
  "has_prev": false
}
```

### 3. UPDATE Operation

```python
# Step 1: Client Request
PUT /api/v1/students/1
{
  "math_score": 9.0,
  "literature_score": 8.5
}

# Step 2: Endpoint
@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    # 2a. Get existing student
    db_student = student_crud.get(db, id=student_id)
    if not db_student:
        raise HTTPException(404, "Student not found")
    
    # 2b. Update student
    updated_student = student_crud.update(
        db=db,
        db_obj=db_student,
        obj_in=student_update
    )
    
    # 2c. Return response
    return StudentResponse(
        **updated_student.dict(),
        full_name=updated_student.get_full_name(),
        average_score=updated_student.get_average_score(),
        grade=updated_student.get_grade()
    )

# Step 3: CRUD Layer
def update(
    self,
    db: Session,
    *,
    db_obj: Student,
    obj_in: StudentUpdate
) -> Student:
    # 3a. Get update data (only provided fields)
    update_data = obj_in.dict(exclude_unset=True)
    
    # 3b. Update fields
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    # 3c. Update timestamp
    db_obj.updated_at = datetime.now()
    
    # 3d. Commit changes
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # 3e. Clear cache
    self._clear_cache_pattern(f"student_{db_obj.id}")
    self._clear_cache_pattern("students_")
    
    # 3f. Log operation
    structured_logger.log_student_operation(
        operation="update",
        student_id=db_obj.student_id,
        details={"updated_fields": list(update_data.keys())}
    )
    
    return db_obj
```

### 4. DELETE Operation

```python
# Step 1: Client Request
DELETE /api/v1/students/1

# Step 2: Endpoint
@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = student_crud.get(db, id=student_id)
    if not db_student:
        raise HTTPException(404, "Student not found")
    
    student_crud.delete(db=db, id=student_id)
    return None  # 204 No Content

# Step 3: CRUD Layer
def delete(self, db: Session, *, id: int) -> Student:
    obj = db.get(Student, id)
    if not obj:
        raise ValueError(f"Student with id {id} not found")
    
    # Log before deletion
    structured_logger.log_student_operation(
        operation="delete",
        student_id=obj.student_id,
        details={"name": obj.get_full_name()}
    )
    
    # Delete from database
    db.delete(obj)
    db.commit()
    
    # Clear all caches
    self._clear_cache_pattern("")
    
    return obj
```

---

## 🎯 Service Layer Flow

### 1. Data Import Flow

```python
# File: app/services/data_service.py

# Step 1: Client uploads file
POST /api/v1/students/bulk-import
Content-Type: multipart/form-data
file: students.xlsx

# Step 2: Endpoint receives file
@router.post("/bulk-import")
async def bulk_import(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    # 2a. Validate file type
    if not file.filename.endswith(('.xlsx', '.csv')):
        raise HTTPException(400, "Invalid file type")
    
    # 2b. Read file content
    content = await file.read()
    
    # 2c. Call service layer
    data_service = DataService()
    
    if file.filename.endswith('.xlsx'):
        df = data_service.parse_excel_file(content)
    else:
        df = data_service.parse_csv_file(content)
    
    # 2d. Clean and validate data
    df_clean = data_service.clean_dataframe(df)
    
    # 2e. Convert to student objects
    students = []
    errors = []
    
    for idx, row in df_clean.iterrows():
        try:
            student = StudentCreate(
                student_id=row['student_id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                # ... other fields
            )
            students.append(student)
        except Exception as e:
            errors.append({
                "row": idx + 2,  # Excel row (header = 1)
                "error": str(e)
            })
    
    # 2f. Bulk insert
    created = []
    for student in students:
        try:
            db_student = student_crud.create(db=db, obj_in=student)
            created.append(db_student)
        except Exception as e:
            errors.append({
                "student_id": student.student_id,
                "error": str(e)
            })
    
    # 2g. Return results
    return {
        "total_rows": len(df_clean),
        "created": len(created),
        "errors": len(errors),
        "error_details": errors
    }

# Step 3: DataService processes file
class DataService:
    def parse_excel_file(self, file_content: bytes) -> pd.DataFrame:
        # 3a. Read Excel file
        df = pd.read_excel(io.BytesIO(file_content))
        
        # 3b. Normalize column names
        df = self._normalize_column_names(df)
        
        return df
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        # 3c. Remove duplicates
        df = df.drop_duplicates(subset=['student_id'])
        
        # 3d. Handle missing values
        df = df.fillna({
            'email': '',
            'hometown': 'Unknown',
            'math_score': None,
            'literature_score': None,
            'english_score': None
        })
        
        # 3e. Validate score ranges
        score_cols = ['math_score', 'literature_score', 'english_score']
        for col in score_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].apply(
                lambda x: x if pd.isna(x) or (0 <= x <= 10) else None
            )
        
        # 3f. Clean strings
        df['student_id'] = df['student_id'].str.strip().str.upper()
        df['first_name'] = df['first_name'].str.strip()
        df['last_name'] = df['last_name'].str.strip()
        
        return df
```

### 2. Export Flow

```python
# File: app/services/export_service.py

# Step 1: Client requests export
GET /api/v1/export?format=excel

# Step 2: Endpoint
@router.get("")
async def export_students(
    format: str = Query("excel", regex="^(excel|csv|xml)$"),
    db: Session = Depends(get_db)
):
    # 2a. Get all students
    students = student_crud.get_all(db=db)
    
    # 2b. Call export service
    export_service = ExportService()
    
    if format == "excel":
        file_content = export_service.students_to_excel(students)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "students.xlsx"
    elif format == "csv":
        file_content = export_service.students_to_csv(students)
        media_type = "text/csv"
        filename = "students.csv"
    else:  # xml
        file_content = export_service.students_to_xml(students)
        media_type = "application/xml"
        filename = "students.xml"
    
    # 2c. Return file response
    return Response(
        content=file_content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

# Step 3: ExportService generates file
class ExportService:
    def students_to_excel(self, students: List[Student]) -> bytes:
        # 3a. Convert to DataFrame
        data = []
        for student in students:
            data.append({
                'Student ID': student.student_id,
                'Full Name': student.get_full_name(),
                'Email': student.email or '',
                'Hometown': student.hometown or '',
                'Math': student.math_score,
                'Literature': student.literature_score,
                'English': student.english_score,
                'Average': student.get_average_score(),
                'Grade': student.get_grade()
            })
        
        df = pd.DataFrame(data)
        
        # 3b. Create Excel writer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write main sheet
            df.to_excel(writer, sheet_name='Students', index=False)
            
            # Format worksheet
            worksheet = writer.sheets['Students']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = max(len(str(cell.value or '')) for cell in column)
                worksheet.column_dimensions[column[0].column_letter].width = max_length + 2
            
            # Add summary sheet
            summary = pd.DataFrame({
                'Metric': ['Total Students', 'Average Score', 'Excellent', 'Good', 'Average', 'Below Average'],
                'Value': [
                    len(students),
                    df['Average'].mean(),
                    len(df[df['Grade'] == 'Excellent']),
                    len(df[df['Grade'] == 'Good']),
                    len(df[df['Grade'] == 'Average']),
                    len(df[df['Grade'] == 'Below Average'])
                ]
            })
            summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # 3c. Return bytes
        output.seek(0)
        return output.getvalue()
```

### 3. Visualization Flow

```python
# File: app/services/visualization_service.py

# Step 1: Client requests chart
GET /api/v1/visualizations/score-distribution

# Step 2: Endpoint
@router.get("/score-distribution")
def get_score_distribution(db: Session = Depends(get_db)):
    return visualization_service.generate_score_distribution_plot(db)

# Step 3: VisualizationService generates chart
class VisualizationService:
    def generate_score_distribution_plot(self, db: Session) -> Dict:
        # 3a. Get all students
        df = self.create_students_dataframe(db)
        
        if df.empty:
            return {"error": "No data available"}
        
        # 3b. Create matplotlib figure
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Score Distribution Analysis', fontsize=16)
        
        # 3c. Plot 1: Histogram with KDE
        sns.histplot(data=df, x='average_score', kde=True, 
                    ax=axes[0, 0], color='skyblue')
        axes[0, 0].set_title('Distribution of Average Scores')
        
        # 3d. Plot 2: Box plot
        subjects_data = df[['math_score', 'literature_score', 'english_score']].melt()
        sns.boxplot(data=subjects_data, x='variable', y='value',
                   ax=axes[0, 1], palette='Set2')
        axes[0, 1].set_title('Score Distribution by Subject')
        
        # 3e. Plot 3: Violin plot
        sns.violinplot(data=subjects_data, x='variable', y='value',
                      ax=axes[1, 0], palette='muted')
        axes[1, 0].set_title('Score Density by Subject')
        
        # 3f. Plot 4: Bar chart
        avg_scores = df[['math_score', 'literature_score', 'english_score']].mean()
        sns.barplot(x=['Math', 'Literature', 'English'], 
                   y=avg_scores.values, ax=axes[1, 1])
        axes[1, 1].set_title('Average Scores by Subject')
        
        plt.tight_layout()
        
        # 3g. Convert to base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        # 3h. Return response
        return {
            "chart_type": "score_distribution",
            "image": image_base64,
            "format": "png",
            "encoding": "base64",
            "statistics": {
                "total_students": len(df),
                "average_scores": {
                    "math": float(df['math_score'].mean()),
                    "literature": float(df['literature_score'].mean()),
                    "english": float(df['english_score'].mean()),
                    "overall": float(df['average_score'].mean())
                }
            }
        }
```

---

## 🔧 Middleware Processing

### Middleware Execution Order

```python
# File: app/main.py

# 1. Application Setup
app = FastAPI(...)

# 2. Add Middleware (LIFO order - Last In First Out)
app.add_middleware(CORSMiddleware, ...)       # Executes 2nd
app.add_middleware(TrustedHostMiddleware, ...) # Executes 1st

# 3. Custom Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # PRE-PROCESSING (before endpoint)
    # Executes 3rd (last middleware)
    
    # Log request
    structured_logger.log_api_request(
        method=request.method,
        path=str(request.url.path),
        remote_addr=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    # Start timer
    start_time = time.time()
    
    # Call next middleware/endpoint
    response = await call_next(request)
    
    # POST-PROCESSING (after endpoint)
    
    # Calculate duration
    process_time = time.time() - start_time
    
    # Add header
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log response
    structured_logger.log_api_response(
        method=request.method,
        path=str(request.url.path),
        status_code=response.status_code,
        duration=process_time
    )
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    return response

# Execution Flow:
# Request → TrustedHost → CORS → Custom → Endpoint
# Response ← Custom ← CORS ← TrustedHost ← Endpoint
```

---

## ⚠️ Error Handling Flow

```python
# Global Exception Handler

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # 1. Capture exception details
    error_trace = traceback.format_exc()
    error_type = type(exc).__name__
    error_message = str(exc)
    
    # 2. Log error with context
    structured_logger.log_error(
        error_type=error_type,
        error_message=error_message,
        stack_trace=error_trace,
        context={
            "method": request.method,
            "path": str(request.url.path),
            "remote_addr": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }
    )
    
    # 3. Log to error log file
    logger.error(f"Unhandled exception on {request.method} {request.url.path}")
    logger.error(f"Error: {error_message}")
    logger.error(f"Stack trace:\n{error_trace}")
    
    # 4. Return safe error response
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": error_type,
            "timestamp": time.time()
        }
    )

# Custom Exception Handling

# Step 1: Define custom exceptions
class StudentNotFoundError(Exception):
    def __init__(self, student_id: str):
        self.student_id = student_id
        super().__init__(f"Student {student_id} not found")

# Step 2: Raise in code
def get_student(db: Session, student_id: str):
    student = student_crud.get_by_student_id(db, student_id)
    if not student:
        raise StudentNotFoundError(student_id)
    return student

# Step 3: Catch in endpoint
try:
    student = get_student(db, student_id)
except StudentNotFoundError as e:
    raise HTTPException(
        status_code=404,
        detail=str(e)
    )
```

---

## 💾 Caching Flow

```python
# In-Memory Cache with TTL

class StudentCRUD:
    def __init__(self):
        self.cache = {}  # {key: value}
        self.cache_timestamps = {}  # {key: timestamp}
    
    # CACHE READ
    def _get_from_cache(self, key: str):
        # 1. Check if key exists
        if key not in self.cache:
            return None
        
        # 2. Check if expired
        if key not in self.cache_timestamps:
            return None
        
        age = time.time() - self.cache_timestamps[key]
        if age > settings.CACHE_TTL:  # Default: 300 seconds
            # Expired, remove from cache
            del self.cache[key]
            del self.cache_timestamps[key]
            return None
        
        # 3. Return cached value
        return self.cache[key]
    
    # CACHE WRITE
    def _set_cache(self, key: str, value):
        self.cache[key] = value
        self.cache_timestamps[key] = time.time()
    
    # CACHE INVALIDATION
    def _clear_cache_pattern(self, pattern: str):
        # Find all keys matching pattern
        keys_to_remove = [
            key for key in self.cache.keys() 
            if key.startswith(pattern)
        ]
        
        # Remove them
        for key in keys_to_remove:
            if key in self.cache:
                del self.cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
    
    # USAGE EXAMPLE
    def get(self, db: Session, id: int) -> Optional[Student]:
        # Try cache first
        cache_key = f"student_{id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.debug(f"Cache hit for {cache_key}")
            return cached
        
        # Cache miss, query database
        logger.debug(f"Cache miss for {cache_key}")
        student = db.get(Student, id)
        
        # Store in cache
        if student:
            self._set_cache(cache_key, student)
        
        return student
    
    # CLEAR CACHE ON WRITE
    def create(self, db: Session, *, obj_in: StudentCreate):
        # ... create student ...
        
        # Clear all list caches
        self._clear_cache_pattern("students_")
        
        return db_obj
    
    def update(self, db: Session, *, db_obj: Student, obj_in: StudentUpdate):
        # ... update student ...
        
        # Clear specific student cache
        self._clear_cache_pattern(f"student_{db_obj.id}")
        
        # Clear all list caches
        self._clear_cache_pattern("students_")
        
        return db_obj
```

---

## 📊 Complete Flow Diagram

```
[CLIENT]
   │
   │ HTTP Request
   │
   ▼
[FASTAPI APP]
   │
   │ Match Route
   │
   ▼
[MIDDLEWARE CHAIN]
   ├──> TrustedHost Middleware
   ├──> CORS Middleware
   └──> Custom Logging Middleware
   │
   │ Validated & Logged
   │
   ▼
[DEPENDENCY INJECTION]
   ├──> get_db() → Session
   ├──> PaginationParams
   └──> Other Dependencies
   │
   │ Dependencies Ready
   │
   ▼
[PYDANTIC VALIDATION]
   │
   │ Request Body Validated
   │
   ▼
[ENDPOINT FUNCTION]
   │
   ├──> Service Layer (Optional)
   │    ├──> DataService
   │    ├──> ExportService
   │    └──> VisualizationService
   │
   └──> CRUD Layer
        │
        ├──> Check Cache
        │    ├──> Hit → Return
        │    └──> Miss → Continue
        │
        └──> Database Query
             │
             ├──> SQLModel ORM
             └──> Execute SQL
   │
   │ Data Retrieved
   │
   ▼
[RESPONSE FORMATTING]
   │
   │ Convert to Response Schema
   │
   ▼
[MIDDLEWARE POST-PROCESSING]
   │
   │ Add Headers, Log Response
   │
   ▼
[CLIENT RESPONSE]
```

---

**Last Updated**: October 5, 2025
**Version**: 1.0.0
