import io
import csv
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import xml.etree.ElementTree as ET
import time

from app.models.student import Student
from app.core.logging import get_export_logger, get_structured_logger

# Initialize loggers
logger = get_export_logger()
structured_logger = get_structured_logger("export")

class ExportService:
    """Service for exporting student data in various formats"""
    
    @staticmethod
    def students_to_csv(students: List[Student], include_analytics: bool = False) -> io.StringIO:
        """Export students to CSV format"""
        start_time = time.time()
        logger.info(f"Starting CSV export for {len(students)} students")
        
        output = io.StringIO()
        
        if not students:
            logger.warning("No students provided for CSV export")
            return output
        
        # Define fieldnames
        fieldnames = [
            'id', 'student_id', 'first_name', 'last_name', 'email',
            'birth_date', 'hometown', 'math_score', 'literature_score',
            'english_score', 'created_at', 'updated_at'
        ]
        
        if include_analytics:
            fieldnames.extend(['full_name', 'average_score', 'grade'])
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for student in students:
            row = {
                'id': student.id,
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'birth_date': student.birth_date.isoformat() if student.birth_date else None,
                'hometown': student.hometown,
                'math_score': student.math_score,
                'literature_score': student.literature_score,
                'english_score': student.english_score,
                'created_at': student.created_at.isoformat(),
                'updated_at': student.updated_at.isoformat()
            }
            
            if include_analytics:
                row.update({
                    'full_name': student.get_full_name(),
                    'average_score': student.get_average_score(),
                    'grade': student.get_grade()
                })
            
            writer.writerow(row)
        
        output.seek(0)
        duration = time.time() - start_time
        
        # Log export completion
        structured_logger.log_data_export(
            format="csv",
            record_count=len(students),
            file_size=len(output.getvalue()),
            duration=duration
        )
        
        logger.info(f"CSV export completed in {duration:.4f}s - {len(students)} records exported")
        return output
    
    @staticmethod
    def students_to_excel(students: List[Student], include_analytics: bool = False) -> io.BytesIO:
        """Export students to Excel format"""
        start_time = time.time()
        logger.info(f"Starting Excel export for {len(students)} students")
        
        output = io.BytesIO()
        
        # Prepare data for DataFrame
        data = []
        for student in students:
            row = {
                'ID': student.id,
                'Mã số sinh viên': student.student_id,
                'Họ': student.first_name,
                'Tên': student.last_name,
                'Email': student.email,
                'Ngày sinh': student.birth_date,
                'Quê quán': student.hometown,
                'Điểm Toán': student.math_score,
                'Điểm Văn': student.literature_score,
                'Điểm tiếng Anh': student.english_score,
                'Ngày tạo': student.created_at,
                'Ngày cập nhật': student.updated_at
            }
            
            if include_analytics:
                row.update({
                    'Họ tên đầy đủ': student.get_full_name(),
                    'Điểm trung bình': student.get_average_score(),
                    'Xếp loại': student.get_grade()
                })
            
            data.append(row)
        
        # Create DataFrame and write to Excel
        df = pd.DataFrame(data)
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Students', index=False)
            
            if include_analytics and students:
                # Analytics sheet
                analytics_data = ExportService._calculate_export_analytics(students)
                
                # Score statistics
                score_stats_df = pd.DataFrame([analytics_data['score_statistics']])
                score_stats_df.to_excel(writer, sheet_name='Analytics', index=False, startrow=0)
                
                # Hometown distribution
                if analytics_data['hometown_distribution']:
                    hometown_df = pd.DataFrame(
                        list(analytics_data['hometown_distribution'].items()),
                        columns=['Quê quán', 'Số lượng']
                    )
                    hometown_df.to_excel(writer, sheet_name='Analytics', index=False, startrow=5)
                
                # Grade distribution
                if analytics_data['grade_distribution']:
                    grade_df = pd.DataFrame(
                        list(analytics_data['grade_distribution'].items()),
                        columns=['Xếp loại', 'Số lượng']
                    )
                    grade_df.to_excel(writer, sheet_name='Analytics', index=False, startrow=5 + len(hometown_df) + 3)
        
        output.seek(0)
        duration = time.time() - start_time
        
        # Log export completion
        structured_logger.log_data_export(
            format="excel",
            record_count=len(students),
            file_size=len(output.getvalue()),
            duration=duration
        )
        
        logger.info(f"Excel export completed in {duration:.4f}s - {len(students)} records exported")
        return output
    
    @staticmethod
    def students_to_xml(students: List[Student], include_analytics: bool = False) -> str:
        """Export students to XML format"""
        start_time = time.time()
        logger.info(f"Starting XML export for {len(students)} students")
        
        if not students:
            logger.warning("No students provided for XML export")
            return '<?xml version="1.0" encoding="UTF-8"?><students></students>'
        
        # Create root element
        root = ET.Element('students')
        
        # Add analytics if requested
        if include_analytics:
            analytics_data = ExportService._calculate_export_analytics(students)
            analytics_elem = ET.SubElement(root, 'analytics')
            
            # Score statistics
            stats_elem = ET.SubElement(analytics_elem, 'score_statistics')
            score_stats = analytics_data['score_statistics']
            
            ET.SubElement(stats_elem, 'total_students').text = str(score_stats['total_students'])
            
            for subject in ['math', 'literature', 'english', 'overall_average']:
                if subject in score_stats:
                    subj_elem = ET.SubElement(stats_elem, subject)
                    subj_data = score_stats[subject]
                    if isinstance(subj_data, dict):
                        for key, value in subj_data.items():
                            if value is not None:
                                ET.SubElement(subj_elem, key).text = str(value)
            
            # Hometown distribution
            if analytics_data['hometown_distribution']:
                hometown_elem = ET.SubElement(analytics_elem, 'hometown_distribution')
                for hometown, count in analytics_data['hometown_distribution'].items():
                    town_elem = ET.SubElement(hometown_elem, 'hometown')
                    ET.SubElement(town_elem, 'name').text = hometown
                    ET.SubElement(town_elem, 'count').text = str(count)
            
            # Grade distribution
            if analytics_data['grade_distribution']:
                grade_elem = ET.SubElement(analytics_elem, 'grade_distribution')
                for grade, count in analytics_data['grade_distribution'].items():
                    grade_item = ET.SubElement(grade_elem, 'grade')
                    ET.SubElement(grade_item, 'name').text = grade
                    ET.SubElement(grade_item, 'count').text = str(count)
        
        # Add student data
        for student in students:
            student_elem = ET.SubElement(root, 'student')
            
            # Basic info
            ET.SubElement(student_elem, 'id').text = str(student.id)
            ET.SubElement(student_elem, 'student_id').text = student.student_id
            
            # Personal info
            personal_info = ET.SubElement(student_elem, 'personal_info')
            ET.SubElement(personal_info, 'first_name').text = student.first_name
            ET.SubElement(personal_info, 'last_name').text = student.last_name
            ET.SubElement(personal_info, 'full_name').text = student.get_full_name()
            
            if student.email:
                ET.SubElement(personal_info, 'email').text = student.email
            if student.birth_date:
                ET.SubElement(personal_info, 'birth_date').text = student.birth_date.isoformat()
            if student.hometown:
                ET.SubElement(personal_info, 'hometown').text = student.hometown
            
            # Academic info
            academic_info = ET.SubElement(student_elem, 'academic_info')
            
            if student.math_score is not None:
                ET.SubElement(academic_info, 'math_score').text = str(student.math_score)
            if student.literature_score is not None:
                ET.SubElement(academic_info, 'literature_score').text = str(student.literature_score)
            if student.english_score is not None:
                ET.SubElement(academic_info, 'english_score').text = str(student.english_score)
            
            avg_score = student.get_average_score()
            if avg_score is not None:
                ET.SubElement(academic_info, 'average_score').text = str(avg_score)
                
            grade = student.get_grade()
            if grade:
                ET.SubElement(academic_info, 'grade').text = grade
            
            # System info
            system_info = ET.SubElement(student_elem, 'system_info')
            ET.SubElement(system_info, 'created_at').text = student.created_at.isoformat()
            ET.SubElement(system_info, 'updated_at').text = student.updated_at.isoformat()
        
        # Format and return XML
        ET.indent(root, space="  ", level=0)
        result = ET.tostring(root, encoding='unicode', xml_declaration=True)
        
        duration = time.time() - start_time
        
        # Log export completion
        structured_logger.log_data_export(
            format="xml",
            record_count=len(students),
            file_size=len(result),
            duration=duration
        )
        
        logger.info(f"XML export completed in {duration:.4f}s - {len(students)} records exported")
        return result
    
    @staticmethod
    def student_to_xml(student: Student) -> str:
        """Export single student to XML format"""
        # Create root element
        root = ET.Element('student')
        
        # Basic info
        ET.SubElement(root, 'id').text = str(student.id)
        ET.SubElement(root, 'student_id').text = student.student_id
        
        # Personal info
        personal_info = ET.SubElement(root, 'personal_info')
        ET.SubElement(personal_info, 'first_name').text = student.first_name
        ET.SubElement(personal_info, 'last_name').text = student.last_name
        ET.SubElement(personal_info, 'full_name').text = student.get_full_name()
        
        if student.email:
            ET.SubElement(personal_info, 'email').text = student.email
        if student.birth_date:
            ET.SubElement(personal_info, 'birth_date').text = student.birth_date.isoformat()
        if student.hometown:
            ET.SubElement(personal_info, 'hometown').text = student.hometown
        
        # Academic info
        academic_info = ET.SubElement(root, 'academic_info')
        
        if student.math_score is not None:
            ET.SubElement(academic_info, 'math_score').text = str(student.math_score)
        if student.literature_score is not None:
            ET.SubElement(academic_info, 'literature_score').text = str(student.literature_score)
        if student.english_score is not None:
            ET.SubElement(academic_info, 'english_score').text = str(student.english_score)
        
        avg_score = student.get_average_score()
        if avg_score is not None:
            ET.SubElement(academic_info, 'average_score').text = str(avg_score)
            
        grade = student.get_grade()
        if grade:
            ET.SubElement(academic_info, 'grade').text = grade
        
        # System info
        system_info = ET.SubElement(root, 'system_info')
        ET.SubElement(system_info, 'created_at').text = student.created_at.isoformat()
        ET.SubElement(system_info, 'updated_at').text = student.updated_at.isoformat()
        
        # Format and return XML
        ET.indent(root, space="  ", level=0)
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
    
    @staticmethod
    def students_to_json(students: List[Student], include_analytics: bool = False) -> str:
        """Export students to JSON format"""
        data = []
        
        for student in students:
            student_data = {
                'id': student.id,
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'birth_date': student.birth_date.isoformat() if student.birth_date else None,
                'hometown': student.hometown,
                'math_score': student.math_score,
                'literature_score': student.literature_score,
                'english_score': student.english_score,
                'created_at': student.created_at.isoformat(),
                'updated_at': student.updated_at.isoformat()
            }
            
            if include_analytics:
                student_data.update({
                    'full_name': student.get_full_name(),
                    'average_score': student.get_average_score(),
                    'grade': student.get_grade()
                })
            
            data.append(student_data)
        
        result = {'students': data}
        
        if include_analytics and students:
            result['analytics'] = ExportService._calculate_export_analytics(students)
        
        return json.dumps(result, ensure_ascii=False, indent=2, default=str)
    
    @staticmethod
    def _calculate_export_analytics(students: List[Student]) -> Dict[str, Any]:
        """Calculate analytics for export"""
        if not students:
            return {}
        
        # Score statistics
        math_scores = [s.math_score for s in students if s.math_score is not None]
        lit_scores = [s.literature_score for s in students if s.literature_score is not None]
        eng_scores = [s.english_score for s in students if s.english_score is not None]
        avg_scores = [s.get_average_score() for s in students if s.get_average_score() is not None]
        
        score_stats = {
            'total_students': len(students),
            'math': {
                'count': len(math_scores),
                'average': sum(math_scores) / len(math_scores) if math_scores else None,
                'min': min(math_scores) if math_scores else None,
                'max': max(math_scores) if math_scores else None
            },
            'literature': {
                'count': len(lit_scores),
                'average': sum(lit_scores) / len(lit_scores) if lit_scores else None,
                'min': min(lit_scores) if lit_scores else None,
                'max': max(lit_scores) if lit_scores else None
            },
            'english': {
                'count': len(eng_scores),
                'average': sum(eng_scores) / len(eng_scores) if eng_scores else None,
                'min': min(eng_scores) if eng_scores else None,
                'max': max(eng_scores) if eng_scores else None
            },
            'overall_average': {
                'count': len(avg_scores),
                'average': sum(avg_scores) / len(avg_scores) if avg_scores else None,
                'min': min(avg_scores) if avg_scores else None,
                'max': max(avg_scores) if avg_scores else None
            }
        }
        
        # Hometown distribution
        hometown_dist = {}
        for student in students:
            if student.hometown:
                hometown_dist[student.hometown] = hometown_dist.get(student.hometown, 0) + 1
        
        # Grade distribution
        grade_dist = {}
        for student in students:
            grade = student.get_grade()
            if grade:
                grade_dist[grade] = grade_dist.get(grade, 0) + 1
        
        return {
            'score_statistics': score_stats,
            'hometown_distribution': dict(sorted(hometown_dist.items(), key=lambda x: x[1], reverse=True)),
            'grade_distribution': grade_dist
        }