"""
Import 100 sample students from JSON file to database
Run this script anytime to populate database with sample data
"""

import sys
import os
import json
from datetime import date, datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlmodel import Session, create_engine, select
from app.models.student import Student
from app.core.config import settings


def parse_date(date_string):
    """Parse date string to date object"""
    return datetime.strptime(date_string, "%Y-%m-%d").date()


def load_sample_data():
    """Load sample students from JSON file"""
    json_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_students_100.json')
    
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return None
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def import_students(clear_existing=False):
    """
    Import students to database
    
    Args:
        clear_existing: If True, delete all existing students before import
    """
    
    print("=" * 70)
    print("🚀 IMPORT 100 SAMPLE STUDENTS TO DATABASE")
    print("=" * 70)
    
    # Load sample data
    print("\n📂 Loading sample data from JSON file...")
    students_data = load_sample_data()
    
    if not students_data:
        return
    
    print(f"✅ Loaded {len(students_data)} students from file")
    
    # Create database engine
    engine = create_engine(settings.DATABASE_URL, echo=False)
    
    with Session(engine) as session:
        
        # Clear existing data if requested
        if clear_existing:
            print("\n🗑️  Clearing existing students from database...")
            existing_count = len(session.exec(select(Student)).all())
            session.exec(select(Student)).all()
            for student in session.exec(select(Student)).all():
                session.delete(student)
            session.commit()
            print(f"✅ Deleted {existing_count} existing students")
        
        # Check for duplicates
        print("\n🔍 Checking for existing student IDs...")
        existing_ids = set()
        for student in session.exec(select(Student)).all():
            existing_ids.add(student.student_id)
        
        if existing_ids:
            print(f"⚠️  Found {len(existing_ids)} existing students in database")
            print(f"   Will skip duplicates and only import new students")
        
        # Import students
        print(f"\n💾 Importing students to database...")
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        for student_data in students_data:
            student_id = student_data['student_id']
            
            # Skip if already exists
            if student_id in existing_ids:
                skipped_count += 1
                continue
            
            try:
                # Create Student object
                student = Student(
                    student_id=student_data['student_id'],
                    first_name=student_data['first_name'],
                    last_name=student_data['last_name'],
                    email=student_data['email'],
                    birth_date=parse_date(student_data['birth_date']),
                    hometown=student_data['hometown'],
                    math_score=student_data['math_score'],
                    literature_score=student_data['literature_score'],
                    english_score=student_data['english_score']
                )
                
                session.add(student)
                imported_count += 1
                
                # Show progress every 20 students
                if imported_count % 20 == 0:
                    print(f"   📝 Imported {imported_count} students...")
                
            except Exception as e:
                error_count += 1
                print(f"   ❌ Error importing {student_id}: {str(e)}")
        
        # Commit all changes
        session.commit()
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 IMPORT SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully imported: {imported_count} students")
    if skipped_count > 0:
        print(f"⏭️  Skipped (already exists): {skipped_count} students")
    if error_count > 0:
        print(f"❌ Errors: {error_count} students")
    print(f"📦 Total in file: {len(students_data)} students")
    
    # Show sample data
    if imported_count > 0:
        with Session(engine) as session:
            print("\n" + "=" * 70)
            print("📋 SAMPLE DATA (First 5 students)")
            print("=" * 70)
            
            students = session.exec(select(Student).limit(5)).all()
            for student in students:
                print(f"\n  🎓 {student.student_id} - {student.first_name} {student.last_name}")
                print(f"     Email: {student.email}")
                print(f"     Hometown: {student.hometown}")
                print(f"     Scores: Math={student.math_score}, Lit={student.literature_score}, Eng={student.english_score}")
                avg = student.get_average_score()
                grade = student.get_grade()
                if avg is not None and grade is not None:
                    print(f"     Average: {avg:.2f} | Grade: {grade}")
    
    print("\n" + "=" * 70)
    print("✅ IMPORT COMPLETED!")
    print("=" * 70)
    
    # Show next steps
    print("\n📌 Next Steps:")
    print("   1. Start server:")
    print("      python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    print()
    print("   2. Generate report (PowerShell):")
    print("      $body = @{")
    print('          current_url = "http://127.0.0.1:5500/index.html"')
    print('          frontend_base_url = "http://127.0.0.1:5500"')
    print(f'          timestamp = "{datetime.now().isoformat()}"')
    print("      } | ConvertTo-Json")
    print()
    print('      Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/crawler/generate-report" `')
    print("          -Method POST -Body $body -ContentType 'application/json'")
    print()
    print("   3. Or use test script:")
    print("      python scripts/test_generate_report.py")
    print()
    print("   4. View API docs:")
    print("      http://127.0.0.1:8000/docs")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Import 100 sample students to database')
    parser.add_argument('--clear', action='store_true', 
                       help='Clear all existing students before import')
    
    args = parser.parse_args()
    
    if args.clear:
        print("\n⚠️  WARNING: This will delete ALL existing students!")
        confirm = input("Are you sure? Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("❌ Import cancelled")
            sys.exit(0)
    
    import_students(clear_existing=args.clear)
