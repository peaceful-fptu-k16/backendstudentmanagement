@echo off
REM Student Management System Backend - Windows Development Setup

echo Setting up Student Management System Backend...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is required but not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs

REM Initialize database
echo Initializing database...
python -c "from app.database import create_db_and_tables; create_db_and_tables(); print('Database initialized successfully')"

echo Setup complete!
echo.
echo To start the development server:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo API will be available at:
echo   - API: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc

pause