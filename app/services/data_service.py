import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, date

from app.models.student import Student, StudentCreate

class DataService:
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # Remove completely empty rows and columns using pandas
        df_clean = df_clean.dropna(how='all')  # Remove rows where all values are NaN
        df_clean = df_clean.loc[:, ~df_clean.columns.str.contains('^Unnamed')]  # Remove unnamed columns
        
        # Standardize column names (convert to lowercase and replace spaces)
        df_clean.columns = df_clean.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '_')
        
        # Enhanced column mapping for Vietnamese and English
        column_mapping = {
            # Student ID variations
            'mã_số_sinh_viên': 'student_id',
            'ma_so_sinh_vien': 'student_id', 
            'mssv': 'student_id',
            'masv': 'student_id',
            'id': 'student_id',
            'student_id': 'student_id',
            
            # Name columns
            'họ_và_tên': 'full_name',
            'ho_va_ten': 'full_name',
            'họ_tên': 'full_name',
            'ho_ten': 'full_name',
            'full_name': 'full_name',
            'name': 'full_name',
            
            'tên': 'first_name',
            'ten': 'first_name', 
            'first_name': 'first_name',
            'fname': 'first_name',
            
            'họ': 'last_name',
            'ho': 'last_name',
            'last_name': 'last_name',
            'lname': 'last_name',
            'surname': 'last_name',
            
            # Email columns
            'thư_điện_tử': 'email',
            'thu_dien_tu': 'email',
            'email': 'email',
            'e_mail': 'email',
            'mail': 'email',
            
            # Birth date columns
            'ngày_sinh': 'birth_date',
            'ngay_sinh': 'birth_date',
            'birth_date': 'birth_date',
            'date_of_birth': 'birth_date',
            'dob': 'birth_date',
            
            # Hometown columns
            'quê_quán': 'hometown',
            'que_quan': 'hometown',
            'nơi_sinh': 'hometown',
            'noi_sinh': 'hometown',
            'hometown': 'hometown',
            'address': 'hometown',
            
            # Math score columns
            'điểm_toán': 'math_score',
            'diem_toan': 'math_score',
            'toán': 'math_score',
            'toan': 'math_score',
            'math': 'math_score',
            'math_score': 'math_score',
            'mathematics': 'math_score',
            
            # Literature score columns
            'điểm_văn': 'literature_score',
            'diem_van': 'literature_score',
            'văn': 'literature_score',
            'van': 'literature_score',
            'ngữ_văn': 'literature_score',
            'ngu_van': 'literature_score',
            'literature': 'literature_score',
            'literature_score': 'literature_score',
            
            # English score columns
            'điểm_tiếng_anh': 'english_score',
            'diem_tieng_anh': 'english_score',
            'tiếng_anh': 'english_score',
            'tieng_anh': 'english_score',
            'anh': 'english_score',
            'english': 'english_score',
            'english_score': 'english_score'
        }
        
        # Apply column mapping
        df_clean = df_clean.rename(columns=column_mapping)
        
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
    
    @staticmethod
    def create_analytics_dataframe(students: List[Student]) -> pd.DataFrame:
        data = []
        for student in students:
            data.append({
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'full_name': student.get_full_name(),
                'email': student.email,
                'birth_date': student.birth_date,
                'hometown': student.hometown,
                'math_score': student.math_score,
                'literature_score': student.literature_score,
                'english_score': student.english_score,
                'average_score': student.get_average_score(),
                'grade': student.get_grade(),
                'created_at': student.created_at,
                'updated_at': student.updated_at
            })
        
        df = pd.DataFrame(data)
        
        # Add computed columns using pandas
        if not df.empty:
            # Age calculation
            df['age'] = pd.to_datetime('today').year - pd.to_datetime(df['birth_date']).dt.year
            
            # Score analysis columns
            df['has_all_scores'] = df[['math_score', 'literature_score', 'english_score']].notna().all(axis=1)
            df['missing_scores_count'] = df[['math_score', 'literature_score', 'english_score']].isna().sum(axis=1)
            
            # Best subject for each student
            score_cols = ['math_score', 'literature_score', 'english_score']
            df['best_subject'] = df[score_cols].idxmax(axis=1)
            df['best_score'] = df[score_cols].max(axis=1)
            df['worst_subject'] = df[score_cols].idxmin(axis=1)
            df['worst_score'] = df[score_cols].min(axis=1)
            
            # Score variance (how consistent are the scores)
            df['score_variance'] = df[score_cols].var(axis=1)
            df['score_std'] = df[score_cols].std(axis=1)
            
            # Performance categories
            df['performance_category'] = pd.cut(
                df['average_score'], 
                bins=[0, 5, 6.5, 8, 10], 
                labels=['Poor', 'Fair', 'Good', 'Excellent'],
                include_lowest=True
            )
        
        return df
    
    @staticmethod
    def get_advanced_statistics(df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {}
        
        stats = {}
        
        # Basic statistics
        stats['total_students'] = len(df)
        stats['students_with_complete_data'] = df[['math_score', 'literature_score', 'english_score']].notna().all(axis=1).sum()
        
        # Score statistics using pandas describe()
        score_columns = ['math_score', 'literature_score', 'english_score', 'average_score']
        for col in score_columns:
            if col in df.columns and not df[col].isna().all():
                col_stats = df[col].describe()
                stats[f'{col}_statistics'] = {
                    'count': int(col_stats['count']),
                    'mean': round(col_stats['mean'], 2),
                    'std': round(col_stats['std'], 2),
                    'min': round(col_stats['min'], 2),
                    'q1': round(col_stats['25%'], 2),
                    'median': round(col_stats['50%'], 2),
                    'q3': round(col_stats['75%'], 2),
                    'max': round(col_stats['max'], 2)
                }
        
        # Grade distribution using value_counts()
        if 'grade' in df.columns:
            grade_counts = df['grade'].value_counts().to_dict()
            # Convert numpy types to Python native types
            stats['grade_distribution'] = {str(k): int(v) for k, v in grade_counts.items()}
            
            # Grade percentages
            total = int(df['grade'].count())
            stats['grade_percentages'] = {str(grade): round(float(count/total*100), 1) for grade, count in grade_counts.items()}
        
        # Hometown analysis using groupby()
        if 'hometown' not in df.columns or df['hometown'].isna().all():
            stats['hometown_analysis'] = {}
        else:
            hometown_df = df.groupby('hometown').agg({
                'student_id': 'count',
                'average_score': ['mean', 'std', 'min', 'max']
            }).round(2)
            
            hometown_df.columns = ['student_count', 'avg_score_mean', 'avg_score_std', 'avg_score_min', 'avg_score_max']
            # Convert to native Python types
            hometown_dict = hometown_df.to_dict('index')
            stats['hometown_analysis'] = {
                str(k): {str(sub_k): float(sub_v) if pd.notna(sub_v) else None for sub_k, sub_v in v.items()}
                for k, v in hometown_dict.items()
            }
        
        # Subject comparison using correlation
        score_cols = ['math_score', 'literature_score', 'english_score']
        available_scores = [col for col in score_cols if col in df.columns and not df[col].isna().all()]
        
        if len(available_scores) >= 2:
            correlation_matrix = df[available_scores].corr()
            # Convert correlation matrix to native Python types
            corr_dict = correlation_matrix.to_dict()
            stats['score_correlations'] = {
                str(k): {str(sub_k): round(float(sub_v), 4) if pd.notna(sub_v) else None for sub_k, sub_v in v.items()}
                for k, v in corr_dict.items()
            }
        
        # Performance trends (if age is available)
        if 'age' in df.columns and not df['age'].isna().all():
            age_performance = df.groupby('age')['average_score'].agg(['count', 'mean', 'std']).round(2)
            # Convert to native Python types
            age_dict = age_performance.to_dict('index')
            stats['age_performance'] = {
                int(k): {str(sub_k): float(sub_v) if pd.notna(sub_v) else None for sub_k, sub_v in v.items()}
                for k, v in age_dict.items()
            }
        
        # Outlier detection using IQR method
        if 'average_score' in df.columns and not df['average_score'].isna().all():
            Q1 = df['average_score'].quantile(0.25)
            Q3 = df['average_score'].quantile(0.75)
            IQR = Q3 - Q1
            
            # Students with outlier performance
            outliers = df[(df['average_score'] < Q1 - 1.5*IQR) | (df['average_score'] > Q3 + 1.5*IQR)]
            stats['outlier_analysis'] = {
                'outlier_count': int(len(outliers)),
                'high_performers': int(len(outliers[outliers['average_score'] > Q3 + 1.5*IQR])),
                'low_performers': int(len(outliers[outliers['average_score'] < Q1 - 1.5*IQR])),
                'outlier_threshold_low': round(float(Q1 - 1.5*IQR), 2),
                'outlier_threshold_high': round(float(Q3 + 1.5*IQR), 2)
            }
        
        return stats