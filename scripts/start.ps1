# Student Management System - PowerShell Start Script
param(
    [switch]$Install,
    [switch]$Test,
    [switch]$Help
)

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Student Management System - Backend API" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

if ($Help) {
    Write-Host @"
Usage: .\start.ps1 [OPTIONS]

Options:
  -Install    Install dependencies before starting
  -Test       Run in test mode with sample data
  -Help       Show this help message

Examples:
  .\start.ps1                  # Start the server
  .\start.ps1 -Install         # Install dependencies and start
  .\start.ps1 -Test            # Start with test data
"@ -ForegroundColor Yellow
    exit
}

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion detected" -ForegroundColor Green
} catch {
    Write-Host "✗ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Install dependencies if requested
if ($Install) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Create directories
$dirs = @("uploads", "logs")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✓ Created $dir directory" -ForegroundColor Green
    }
}

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Yellow
try {
    python -c "from app.database import create_db_and_tables; create_db_and_tables(); print('✓ Database initialized')"
} catch {
    Write-Host "✗ Failed to initialize database" -ForegroundColor Red
    exit 1
}

if ($Test) {
    Write-Host "Starting in test mode..." -ForegroundColor Yellow
    python run.py --test
} else {
    Write-Host "Starting server..." -ForegroundColor Yellow
    Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host "-" * 50 -ForegroundColor Gray
    
    python run.py
}