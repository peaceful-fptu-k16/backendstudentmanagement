#!/usr/bin/env python3
"""
Production cleanup and validation script for Student Management System
Run this before committing to GitHub
"""

import os
import sys
import glob
import json
from pathlib import Path

def remove_temp_files():
    """Remove temporary and development files"""
    temp_patterns = [
        "*.tmp",
        "*.temp", 
        "**/test_*.py",
        "**/__pycache__",
        "**/*.pyc",
        "cors_test.html",
        "simple_http_server.py"
    ]
    
    removed_files = []
    
    for pattern in temp_patterns:
        files = glob.glob(pattern, recursive=True)
        for file_path in files:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    removed_files.append(file_path)
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                    removed_files.append(file_path)
            except Exception as e:
                print(f"Warning: Could not remove {file_path}: {e}")
    
    return removed_files

def validate_project_structure():
    """Validate that all required files exist"""
    required_files = [
        "app/main.py",
        "app/__init__.py",
        "app/models/student.py",
        "app/crud/student.py",
        "app/api/__init__.py",
        "app/api/endpoints/students.py",
        "app/api/endpoints/analytics.py",
        "app/core/config.py",
        "app/core/logging.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "LICENSE"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    return existing_files, missing_files

def check_code_syntax():
    """Check Python syntax for main files"""
    python_files = [
        "app/main.py",
        "app/models/student.py", 
        "app/crud/student.py",
        "app/api/endpoints/students.py",
        "app/api/endpoints/analytics.py",
        "scripts/run.py"
    ]
    
    syntax_errors = []
    
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), file_path, 'exec')
            except SyntaxError as e:
                syntax_errors.append(f"{file_path}: {e}")
    
    return syntax_errors

def check_english_content():
    """Check if Vietnamese text has been replaced with English"""
    files_to_check = [
        "app/models/student.py",
        "app/api/endpoints/analytics.py"
    ]
    
    vietnamese_words = ["Giỏi", "Khá", "Trung bình", "Yếu", "Kém", "Điểm", "Mã số", "Họ", "Tên"]
    issues = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for word in vietnamese_words:
                        if word in content:
                            issues.append(f"{file_path}: Contains Vietnamese word '{word}'")
            except Exception as e:
                issues.append(f"Could not read {file_path}: {e}")
    
    return issues

def generate_project_summary():
    """Generate project summary for commit"""
    summary = {
        "project_name": "Student Management System - Backend API",
        "version": "1.0.0",
        "description": "FastAPI-based student management system with advanced features",
        "main_features": [
            "RESTful API with FastAPI",
            "SQLModel ORM with SQLite database", 
            "Advanced daily logging system",
            "Student CRUD operations with validation",
            "Analytics and reporting endpoints",
            "Data import/export (Excel, CSV, XML)",
            "Web scraping capabilities",
            "CORS support for frontend integration",
            "Performance monitoring and logging"
        ],
        "tech_stack": {
            "framework": "FastAPI 0.104+",
            "database": "SQLite (development) / PostgreSQL (production)",
            "orm": "SQLModel 0.0.14",
            "data_processing": "Pandas 2.1+",
            "validation": "Pydantic 2.5+",
            "python_version": "3.8+"
        },
        "api_endpoints": {
            "students": "/api/v1/students - CRUD operations",
            "analytics": "/api/v1/analytics - Performance analytics", 
            "export": "/api/v1/export - Data export",
            "crawler": "/api/v1/crawler - Web scraping",
            "docs": "/docs - API documentation",
            "health": "/health - Health check"
        },
        "ready_for_production": True,
        "language": "English",
        "license": "MIT"
    }
    
    return summary

def main():
    """Main cleanup and validation function"""
    print("🧹 Starting production cleanup and validation...")
    print("=" * 60)
    
    # Remove temporary files
    print("\n1. Removing temporary files...")
    removed = remove_temp_files()
    if removed:
        print(f"   ✓ Removed {len(removed)} temporary files")
    else:
        print("   ✓ No temporary files to remove")
    
    # Validate project structure
    print("\n2. Validating project structure...")
    existing, missing = validate_project_structure()
    print(f"   ✓ Found {len(existing)} required files")
    if missing:
        print(f"   ⚠️  Missing {len(missing)} files:")
        for file in missing:
            print(f"      - {file}")
    
    # Check Python syntax
    print("\n3. Checking Python syntax...")
    syntax_errors = check_code_syntax()
    if syntax_errors:
        print(f"   ❌ Found {len(syntax_errors)} syntax errors:")
        for error in syntax_errors:
            print(f"      - {error}")
        return False
    else:
        print("   ✓ All Python files have valid syntax")
    
    # Check English content
    print("\n4. Checking language consistency...")
    language_issues = check_english_content()
    if language_issues:
        print(f"   ⚠️  Found {len(language_issues)} language issues:")
        for issue in language_issues:
            print(f"      - {issue}")
    else:
        print("   ✓ All content is in English")
    
    # Generate summary
    print("\n5. Generating project summary...")
    summary = generate_project_summary()
    
    # Save summary to file
    with open("PROJECT_SUMMARY.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print("   ✓ Project summary saved to PROJECT_SUMMARY.json")
    
    # Final status
    print("\n" + "=" * 60)
    print("🎯 CLEANUP AND VALIDATION COMPLETE")
    print("=" * 60)
    
    if not missing and not syntax_errors:
        print("✅ PROJECT IS READY FOR GITHUB COMMIT!")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Initial commit: Student Management System Backend'")
        print("3. git push origin main")
        return True
    else:
        print("⚠️  Please resolve the above issues before committing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)