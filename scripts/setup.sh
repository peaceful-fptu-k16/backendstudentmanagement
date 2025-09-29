#!/bin/bash

# Student Management System Backend - Development Setup

echo "Setting up Student Management System Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || venv\Scripts\activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads
mkdir -p logs

# Initialize database
echo "Initializing database..."
python -c "
from app.database import create_db_and_tables
create_db_and_tables()
print('Database initialized successfully')
"

echo "Setup complete!"
echo ""
echo "To start the development server:"
echo "  1. Activate virtual environment: source venv/bin/activate (or venv\\Scripts\\activate on Windows)"
echo "  2. Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"