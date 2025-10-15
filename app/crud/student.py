from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, and_, or_, func, desc, asc
import time

from app.models.student import Student, StudentCreate, StudentUpdate
from app.core.config import settings
from app.core.logging import get_database_logger, get_structured_logger

logger = get_database_logger()
structured_logger = get_structured_logger("database")

class StudentCRUD:
    
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
    
    def _is_cache_valid(self, key: str) -> bool:
        if key not in self.cache:
            return False
        if key not in self.cache_timestamps:
            return False
        
        # Check TTL
        age = time.time() - self.cache_timestamps[key]
        return age < settings.CACHE_TTL
    
    def _get_from_cache(self, key: str):
        if self._is_cache_valid(key):
            return self.cache[key]
        return None
    
    def _set_cache(self, key: str, value):
        self.cache[key] = value
        self.cache_timestamps[key] = time.time()
    
    def _clear_cache_pattern(self, pattern: str):
        keys_to_remove = [key for key in self.cache.keys() if key.startswith(pattern)]
        for key in keys_to_remove:
            if key in self.cache:
                del self.cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
    
    def create(self, db: Session, *, obj_in: StudentCreate) -> Student:
        start_time = time.time()
        logger.info(f"Creating new student with ID: {obj_in.student_id}")
        
        # Check if student_id already exists
        existing = self.get_by_student_id(db, student_id=obj_in.student_id)
        if existing:
            logger.warning(f"Attempt to create duplicate student ID: {obj_in.student_id}")
            raise ValueError(f"Student with ID {obj_in.student_id} already exists")
        
        db_obj = Student.from_orm(obj_in)
        db_obj.created_at = datetime.now()
        db_obj.updated_at = datetime.now()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        duration = time.time() - start_time
        
        # Log database operation
        structured_logger.log_database_query(
            operation="INSERT",
            table="students",
            duration=duration,
            record_count=1
        )
        
        structured_logger.log_student_operation(
            operation="create",
            student_id=obj_in.student_id,
            details={"full_name": f"{obj_in.first_name} {obj_in.last_name}"}
        )
        
        logger.info(f"Student created successfully: {obj_in.student_id} in {duration:.4f}s")
        
        # Clear related cache entries
        self._clear_cache_pattern("students_")
        
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[Student]:
        cache_key = f"student_{id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        student = db.get(Student, id)
        if student:
            self._set_cache(cache_key, student)
        return student
    
    def get_by_student_id(self, db: Session, student_id: str) -> Optional[Student]:
        cache_key = f"student_by_id_{student_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        statement = select(Student).where(Student.student_id == student_id)
        student = db.exec(statement).first()
        if student:
            self._set_cache(cache_key, student)
        return student
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 1000,
        search: Optional[str] = None,
        hometown: Optional[str] = None,
        min_average: Optional[float] = None,
        max_average: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Student], int]:
        
        # Build cache key based on parameters
        cache_key = f"students_{skip}_{limit}_{search}_{hometown}_{min_average}_{max_average}_{sort_by}_{sort_order}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Build query
        statement = select(Student)
        count_statement = select(func.count(Student.id))
        
        # Apply filters
        conditions = []
        
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    Student.student_id.ilike(search_pattern),
                    Student.first_name.ilike(search_pattern),
                    Student.last_name.ilike(search_pattern),
                    Student.email.ilike(search_pattern)
                )
            )
        
        if hometown:
            conditions.append(Student.hometown.ilike(f"%{hometown}%"))
        
        # Apply average score filters (computed on-the-fly)
        if min_average is not None or max_average is not None:
            # This is a simplified approach - in production, you might want to store computed scores
            pass  # We'll filter after fetching for now
        
        if conditions:
            statement = statement.where(and_(*conditions))
            count_statement = count_statement.where(and_(*conditions))
        
        # Apply sorting
        if sort_by:
            if sort_by in ["student_id", "first_name", "last_name", "email", "hometown", "birth_date", "created_at"]:
                column = getattr(Student, sort_by)
                if sort_order.lower() == "desc":
                    statement = statement.order_by(desc(column))
                else:
                    statement = statement.order_by(asc(column))
        else:
            statement = statement.order_by(Student.created_at.desc())
        
        # Get total count
        total = db.exec(count_statement).one()
        
        # Apply pagination
        statement = statement.offset(skip).limit(limit)
        
        # Execute query
        students = db.exec(statement).all()
        
        # Apply average score filters if needed
        if min_average is not None or max_average is not None:
            filtered_students = []
            for student in students:
                avg = student.get_average_score()
                if avg is not None:
                    if min_average is not None and avg < min_average:
                        continue
                    if max_average is not None and avg > max_average:
                        continue
                filtered_students.append(student)
            students = filtered_students
        
        result = (students, total)
        self._set_cache(cache_key, result)
        return result
    
    def update(self, db: Session, *, db_obj: Student, obj_in: StudentUpdate) -> Student:
        update_data = obj_in.dict(exclude_unset=True)
        
        # Check if updating student_id and it doesn't conflict
        if "student_id" in update_data and update_data["student_id"] != db_obj.student_id:
            existing = self.get_by_student_id(db, student_id=update_data["student_id"])
            if existing and existing.id != db_obj.id:
                raise ValueError(f"Student with ID {update_data['student_id']} already exists")
        
        # Update fields
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db_obj.updated_at = datetime.now()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Clear cache
        self._clear_cache_pattern(f"student_{db_obj.id}")
        self._clear_cache_pattern(f"student_by_id_{db_obj.student_id}")
        self._clear_cache_pattern("students_")
        
        return db_obj
    
    def delete(self, db: Session, *, id: int) -> Optional[Student]:
        student = db.get(Student, id)
        if student:
            db.delete(student)
            db.commit()
            
            # Clear cache
            self._clear_cache_pattern(f"student_{id}")
            self._clear_cache_pattern(f"student_by_id_{student.student_id}")
            self._clear_cache_pattern("students_")
        
        return student
    
    def bulk_create(self, db: Session, *, students_in: List[StudentCreate]) -> tuple[List[Student], List[str]]:
        start_time = time.time()
        logger.info(f"Starting bulk create for {len(students_in)} students")
        
        created_students = []
        errors = []
        
        for i, student_data in enumerate(students_in):
            try:
                # Check if student_id already exists
                existing = self.get_by_student_id(db, student_id=student_data.student_id)
                if existing:
                    errors.append(f"Student {student_data.student_id} already exists")
                    continue
                
                db_obj = Student.from_orm(student_data)
                db_obj.created_at = datetime.now()
                db_obj.updated_at = datetime.now()
                
                db.add(db_obj)
                created_students.append(db_obj)
                
            except Exception as e:
                logger.error(f"Error creating student {student_data.student_id}: {str(e)}")
                errors.append(f"Error creating student {student_data.student_id}: {str(e)}")
        
        try:
            db.commit()
            for student in created_students:
                db.refresh(student)
            
            duration = time.time() - start_time
            
            # Log bulk operation
            structured_logger.log_database_query(
                operation="BULK_INSERT",
                table="students",
                duration=duration,
                record_count=len(created_students)
            )
            
            structured_logger.log_data_import(
                file_name="bulk_create",
                file_type="api",
                processed=len(students_in),
                successful=len(created_students),
                failed=len(students_in) - len(created_students),
                errors=errors
            )
            
            logger.info(f"Bulk create completed: {len(created_students)}/{len(students_in)} students created in {duration:.4f}s")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Bulk create transaction failed: {str(e)}")
            errors.append(f"Transaction failed: {str(e)}")
            created_students = []
        
        # Clear cache
        self._clear_cache_pattern("students_")
        
        return created_students, errors
    
    def get_analytics(self, db: Session) -> Dict[str, Any]:
        cache_key = "analytics"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Total students in database
        total_students = db.exec(select(func.count(Student.id))).one()
        
        # Get all students for analysis
        students = db.exec(select(Student)).all()
        
        # Filter students with complete scores (all 3 subjects)
        students_with_complete_scores = [
            s for s in students 
            if s.math_score is not None 
            and s.literature_score is not None 
            and s.english_score is not None
        ]
        
        # Calculate analytics
        analytics = {
            "total_students": total_students,
            "students_with_complete_scores": len(students_with_complete_scores),
            "students_with_incomplete_scores": total_students - len(students_with_complete_scores),
            "average_scores": {},
            "score_distribution": {},
            "hometown_distribution": {},
            "grade_distribution": {},
            "subject_comparison": {}
        }
        
        if students_with_complete_scores:
            # Average scores by subject (only from students with complete scores)
            math_scores = [s.math_score for s in students_with_complete_scores]
            lit_scores = [s.literature_score for s in students_with_complete_scores]
            eng_scores = [s.english_score for s in students_with_complete_scores]
            
            analytics["average_scores"] = {
                "math": sum(math_scores) / len(math_scores) if math_scores else None,
                "literature": sum(lit_scores) / len(lit_scores) if lit_scores else None,
                "english": sum(eng_scores) / len(eng_scores) if eng_scores else None
            }
            
            # Score distribution (only students with complete scores)
            score_ranges = {"0-4": 0, "4-5.5": 0, "5.5-7": 0, "7-8.5": 0, "8.5-10": 0}
            for student in students_with_complete_scores:
                avg = student.get_average_score()
                if avg is not None:  # Should always be true here, but safety check
                    if avg < 4:
                        score_ranges["0-4"] += 1
                    elif avg < 5.5:
                        score_ranges["4-5.5"] += 1
                    elif avg < 7:
                        score_ranges["5.5-7"] += 1
                    elif avg < 8.5:
                        score_ranges["7-8.5"] += 1
                    else:
                        score_ranges["8.5-10"] += 1
            
            analytics["score_distribution"] = score_ranges
            
            # Hometown distribution (all students, not just those with complete scores)
            hometown_count = {}
            for student in students:
                if student.hometown:
                    hometown_count[student.hometown] = hometown_count.get(student.hometown, 0) + 1
            analytics["hometown_distribution"] = dict(sorted(hometown_count.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # Grade distribution (only students with complete scores)
            grade_count = {}
            for student in students_with_complete_scores:
                grade = student.get_grade()
                if grade:  # Should always be true here
                    grade_count[grade] = grade_count.get(grade, 0) + 1
            analytics["grade_distribution"] = grade_count
            
            # Subject comparison (only students with complete scores)
            analytics["subject_comparison"] = {
                "math_vs_english": self._compare_subjects(students_with_complete_scores, "math_score", "english_score"),
                "math_vs_literature": self._compare_subjects(students_with_complete_scores, "math_score", "literature_score"),
                "english_vs_literature": self._compare_subjects(students_with_complete_scores, "english_score", "literature_score")
            }
        
        self._set_cache(cache_key, analytics)
        return analytics
    
    def _compare_subjects(self, students: List[Student], subject1: str, subject2: str) -> Dict[str, int]:
        better_subject1 = 0
        better_subject2 = 0
        equal = 0
        
        for student in students:
            score1 = getattr(student, subject1)
            score2 = getattr(student, subject2)
            
            if score1 is not None and score2 is not None:
                if score1 > score2:
                    better_subject1 += 1
                elif score2 > score1:
                    better_subject2 += 1
                else:
                    equal += 1
        
        return {
            f"better_{subject1}": better_subject1,
            f"better_{subject2}": better_subject2,
            "equal": equal
        }
    
    def _clear_cache_pattern(self, pattern: str):
        keys_to_remove = [key for key in self.cache.keys() if key.startswith(pattern)]
        for key in keys_to_remove:
            del self.cache[key]

# Create instance
student_crud = StudentCRUD()