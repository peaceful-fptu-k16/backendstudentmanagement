# Test script for Student Management API
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Testing Student Management API" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"

function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [string]$Body = $null,
        [string]$Description
    )
    
    Write-Host "`n🔍 Testing: $Description" -ForegroundColor Yellow
    Write-Host "   $Method $Url" -ForegroundColor Gray
    
    try {
        if ($Body) {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -Body $Body -ContentType "application/json"
        } else {
            $response = Invoke-RestMethod -Uri $Url -Method $Method
        }
        
        Write-Host "   ✅ Success" -ForegroundColor Green
        return $response
    }
    catch {
        Write-Host "   ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Test 1: Health Check
$health = Test-Endpoint -Url "$baseUrl/health" -Description "Health Check"
if ($health) {
    Write-Host "   Status: $($health.status)" -ForegroundColor Green
}

# Test 2: Root Endpoint
$root = Test-Endpoint -Url "$baseUrl/" -Description "Root Endpoint"
if ($root) {
    Write-Host "   Message: $($root.message)" -ForegroundColor Green
}

# Test 3: Create Sample Student
$studentData = @{
    student_id = "SV2024001"
    first_name = "Nguyễn"
    last_name = "Văn An"
    email = "nva@university.edu.vn"
    birth_date = "2000-01-15"
    hometown = "Hà Nội"
    math_score = 8.5
    literature_score = 7.0
    english_score = 9.0
} | ConvertTo-Json

$student = Test-Endpoint -Url "$baseUrl/api/v1/students" -Method "POST" -Body $studentData -Description "Create Student"
if ($student) {
    Write-Host "   Created: $($student.full_name) (ID: $($student.student_id))" -ForegroundColor Green
    Write-Host "   Average Score: $($student.average_score)" -ForegroundColor Green
    Write-Host "   Grade: $($student.grade)" -ForegroundColor Green
}

# Test 4: Generate Sample Data
Write-Host "`n🔍 Generating sample data..." -ForegroundColor Yellow
try {
    $sampleResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/students/generate-sample?count=20" -Method "POST"
    Write-Host "   ✅ Generated $($sampleResponse.successful_imports) sample students" -ForegroundColor Green
}
catch {
    Write-Host "   ⚠️  Sample data generation failed or students already exist" -ForegroundColor Yellow
}

# Test 5: Get Students List
$students = Test-Endpoint -Url "$baseUrl/api/v1/students?page=1&page_size=5" -Description "Get Students List"
if ($students) {
    Write-Host "   Total Students: $($students.total)" -ForegroundColor Green
    Write-Host "   Page: $($students.page)/$($students.total_pages)" -ForegroundColor Green
    Write-Host "   Students in this page:" -ForegroundColor Green
    foreach ($s in $students.items) {
        Write-Host "     - $($s.full_name) ($($s.student_id)) - Avg: $($s.average_score)" -ForegroundColor Gray
    }
}

# Test 6: Search Students
$searchResults = Test-Endpoint -Url "$baseUrl/api/v1/students?search=Nguyen&page=1&page_size=3" -Description "Search Students"
if ($searchResults) {
    Write-Host "   Found $($searchResults.total) students matching 'Nguyen'" -ForegroundColor Green
}

# Test 7: Analytics
$analytics = Test-Endpoint -Url "$baseUrl/api/v1/analytics" -Description "Get Analytics"
if ($analytics) {
    Write-Host "   Total Students: $($analytics.total_students)" -ForegroundColor Green
    Write-Host "   Average Scores:" -ForegroundColor Green
    if ($analytics.average_scores.math) { Write-Host "     Math: $($analytics.average_scores.math)" -ForegroundColor Gray }
    if ($analytics.average_scores.literature) { Write-Host "     Literature: $($analytics.average_scores.literature)" -ForegroundColor Gray }
    if ($analytics.average_scores.english) { Write-Host "     English: $($analytics.average_scores.english)" -ForegroundColor Gray }
}

# Test 8: Export Test
Write-Host "`n🔍 Testing: Export to CSV" -ForegroundColor Yellow
try {
    $csvUrl = "$baseUrl/api/v1/export/students?format=csv&include_analytics=true"
    Invoke-WebRequest -Uri $csvUrl -OutFile "students_export.csv"
    Write-Host "   ✅ Exported to students_export.csv" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Export failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "API Testing Complete!" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "`nAPI Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "API Root: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Yellow