import pandas as pd
import io
from typing import List, Dict, Any, Optional
from datetime import datetime, date

from app.models.student import Student, StudentCreate, StudentBulkImportResult

class DataService:
    """Service for data processing and cleaning"""
    
    @staticmethod
    def parse_excel_file(file_content: bytes) -> pd.DataFrame:
        """Parse Excel file to DataFrame"""
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            return df
        except Exception as e:
            raise ValueError(f"Failed to parse Excel file: {str(e)}")
    
    @staticmethod
    def parse_csv_file(file_content: bytes, encoding: str = 'utf-8') -> pd.DataFrame:
        """Parse CSV file to DataFrame"""
        try:
            content = file_content.decode(encoding)
            df = pd.read_csv(io.StringIO(content))
            return df
        except UnicodeDecodeError:
            # Try different encodings
            for enc in ['latin1', 'cp1252', 'utf-8-sig']:
                try:
                    content = file_content.decode(enc)
                    df = pd.read_csv(io.StringIO(content))
                    return df
                except:
                    continue
            raise ValueError("Failed to decode CSV file with any supported encoding")
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize DataFrame"""
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # Standardize column names
        column_mapping = {
            # Vietnamese columns
            'mã số sinh viên': 'student_id',
            'ma so sinh vien': 'student_id',
            'masv': 'student_id',
            'họ': 'first_name',
            'ho': 'first_name',
            'tên': 'last_name',
            'ten': 'last_name',
            'họ tên': 'full_name',
            'ho ten': 'full_name',
            'họ và tên': 'full_name',
            'ngày sinh': 'birth_date',
            'ngay sinh': 'birth_date',
            'quê quán': 'hometown',
            'que quan': 'hometown',
            'điểm toán': 'math_score',
            'diem toan': 'math_score',
            'toán': 'math_score',
            'toan': 'math_score',
            'điểm văn': 'literature_score',
            'diem van': 'literature_score',
            'văn': 'literature_score',
            'van': 'literature_score',
            'điểm tiếng anh': 'english_score',
            'diem tieng anh': 'english_score',
            'tiếng anh': 'english_score',
            'tieng anh': 'english_score',
            'english': 'english_score',
            # English columns
            'student_id': 'student_id',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email',
            'birth_date': 'birth_date',
            'hometown': 'hometown',
            'math_score': 'math_score',
            'literature_score': 'literature_score',
            'english_score': 'english_score'
        }
        
        # Normalize column names (lowercase, remove extra spaces)
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        # Rename columns
        df_clean = df_clean.rename(columns=column_mapping)
        
        # Handle full_name column if present
        if 'full_name' in df_clean.columns and 'first_name' not in df_clean.columns:
            # Split full name into first and last name
            name_parts = df_clean['full_name'].str.split(' ', n=1, expand=True)
            df_clean['first_name'] = name_parts[0] if len(name_parts.columns) > 0 else ''
            df_clean['last_name'] = name_parts[1] if len(name_parts.columns) > 1 else ''
            df_clean = df_clean.drop(columns=['full_name'])
        
        # Clean string fields
        string_columns = ['student_id', 'first_name', 'last_name', 'email', 'hometown']
        for col in string_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].replace(['nan', 'NaN', 'None', ''], None)
        
        # Clean numeric fields (scores)
        score_columns = ['math_score', 'literature_score', 'english_score']
        for col in score_columns:
            if col in df_clean.columns:
                # Convert to numeric, coerce errors to NaN
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                # Clamp scores to 0-10 range
                df_clean[col] = df_clean[col].clip(0, 10)
        
        # Clean date field
        if 'birth_date' in df_clean.columns:
            df_clean['birth_date'] = pd.to_datetime(df_clean['birth_date'], errors='coerce')
            # Convert to date only (remove time component)
            df_clean['birth_date'] = df_clean['birth_date'].dt.date
        
        # Remove rows where student_id is missing
        df_clean = df_clean.dropna(subset=['student_id'])
        
        # Remove duplicate student_ids, keep first occurrence
        df_clean = df_clean.drop_duplicates(subset=['student_id'], keep='first')
        
        return df_clean
    
    @staticmethod
    def dataframe_to_students(df: pd.DataFrame) -> tuple[List[StudentCreate], List[str]]:
        """Convert DataFrame to StudentCreate objects"""
        students = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Prepare student data
                student_data = {}
                
                # Required fields
                if pd.isna(row.get('student_id')) or not row.get('student_id'):
                    errors.append(f"Row {index + 1}: Student ID is required")
                    continue
                student_data['student_id'] = str(row['student_id']).strip()
                
                if pd.isna(row.get('first_name')) or not row.get('first_name'):
                    errors.append(f"Row {index + 1}: First name is required")
                    continue
                student_data['first_name'] = str(row['first_name']).strip()
                
                if pd.isna(row.get('last_name')) or not row.get('last_name'):
                    errors.append(f"Row {index + 1}: Last name is required")
                    continue
                student_data['last_name'] = str(row['last_name']).strip()
                
                # Optional fields
                for field in ['email', 'hometown']:
                    if field in row and not pd.isna(row[field]) and row[field]:
                        student_data[field] = str(row[field]).strip()
                
                # Date field
                if 'birth_date' in row and not pd.isna(row['birth_date']):
                    if isinstance(row['birth_date'], date):
                        student_data['birth_date'] = row['birth_date']
                    elif isinstance(row['birth_date'], datetime):
                        student_data['birth_date'] = row['birth_date'].date()
                    else:
                        try:
                            student_data['birth_date'] = pd.to_datetime(row['birth_date']).date()
                        except:
                            pass
                
                # Score fields
                for field in ['math_score', 'literature_score', 'english_score']:
                    if field in row and not pd.isna(row[field]):
                        score = float(row[field])
                        if 0 <= score <= 10:
                            student_data[field] = score
                
                # Create StudentCreate object
                student = StudentCreate(**student_data)
                students.append(student)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        return students, errors
    
    @staticmethod
    def generate_sample_data(count: int = 100) -> List[StudentCreate]:
        """Generate sample student data"""
        import random
        
        students = []
        
        # Sample Vietnamese names and hometowns
        first_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng']
        last_names = ['Văn Hùng', 'Thị Lan', 'Đức Anh', 'Thị Hoa', 'Văn Nam', 'Thị Mai', 'Đức Bảo', 'Thị Linh']
        hometowns = ['Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ', 'An Giang', 'Bắc Giang', 'Bình Dương']
        
        for i in range(count):
            student_id = f"SV{2020 + random.randint(0, 4)}{str(i+1).zfill(4)}"
            
            # Generate fake birth date
            year = random.randint(2000, 2005)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            birth_date = date(year, month, day)
            
            student_data = {
                'student_id': student_id,
                'first_name': random.choice(first_names),
                'last_name': random.choice(last_names),
                'email': f"{student_id.lower()}@university.edu.vn" if random.random() > 0.1 else None,
                'birth_date': birth_date if random.random() > 0.1 else None,
                'hometown': random.choice(hometowns) if random.random() > 0.1 else None,
                'math_score': round(random.uniform(3, 10), 1) if random.random() > 0.15 else None,
                'literature_score': round(random.uniform(3, 10), 1) if random.random() > 0.15 else None,
                'english_score': round(random.uniform(3, 10), 1) if random.random() > 0.15 else None
            }
            
            students.append(StudentCreate(**student_data))
        
        return students