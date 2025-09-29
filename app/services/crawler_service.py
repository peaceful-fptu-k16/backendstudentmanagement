import requests
import time
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse
import re

from app.core.config import settings
from app.models.student import StudentCreate

class CrawlerService:
    """Service for crawling student data from websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.CRAWLER_USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def crawl_student_list(self, url: str, parser_config: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Crawl a list of students from a webpage"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            students_data = []
            
            # Default parser configuration
            if not parser_config:
                parser_config = {
                    'table_selector': 'table',
                    'row_selector': 'tr',
                    'header_row_index': 0,
                    'data_start_row': 1,
                    'column_mapping': {
                        0: 'student_id',
                        1: 'first_name',
                        2: 'last_name',
                        3: 'email',
                        4: 'birth_date',
                        5: 'hometown',
                        6: 'math_score',
                        7: 'literature_score',
                        8: 'english_score'
                    }
                }
            
            # Find the table
            table = soup.select_one(parser_config['table_selector'])
            if not table:
                raise ValueError(f"No table found with selector: {parser_config['table_selector']}")
            
            rows = table.select(parser_config['row_selector'])
            
            # Extract headers if available
            headers = []
            if parser_config['header_row_index'] is not None and len(rows) > parser_config['header_row_index']:
                header_row = rows[parser_config['header_row_index']]
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            # Extract data rows
            data_rows = rows[parser_config['data_start_row']:]
            
            for row in data_rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) == 0:
                    continue
                
                student_data = {}
                
                for i, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    
                    # Map column index to field name
                    if i in parser_config['column_mapping']:
                        field_name = parser_config['column_mapping'][i]
                        student_data[field_name] = text if text else None
                
                if student_data and 'student_id' in student_data:
                    students_data.append(student_data)
            
            time.sleep(settings.CRAWLER_DELAY)  # Rate limiting
            return students_data
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL {url}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse HTML: {str(e)}")
    
    def crawl_student_detail(self, url: str, parser_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Crawl detailed information for a single student"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Default parser configuration for detail pages
            if not parser_config:
                parser_config = {
                    'field_selectors': {
                        'student_id': ['#student-id', '.student-id', '[data-field="student_id"]'],
                        'first_name': ['#first-name', '.first-name', '[data-field="first_name"]'],
                        'last_name': ['#last-name', '.last-name', '[data-field="last_name"]'],
                        'email': ['#email', '.email', '[data-field="email"]'],
                        'birth_date': ['#birth-date', '.birth-date', '[data-field="birth_date"]'],
                        'hometown': ['#hometown', '.hometown', '[data-field="hometown"]'],
                        'math_score': ['#math-score', '.math-score', '[data-field="math_score"]'],
                        'literature_score': ['#literature-score', '.literature-score', '[data-field="literature_score"]'],
                        'english_score': ['#english-score', '.english-score', '[data-field="english_score"]']
                    }
                }
            
            student_data = {}
            
            for field_name, selectors in parser_config['field_selectors'].items():
                value = None
                for selector in selectors:
                    element = soup.select_one(selector)
                    if element:
                        value = element.get_text(strip=True)
                        break
                
                if value:
                    student_data[field_name] = value
            
            time.sleep(settings.CRAWLER_DELAY)  # Rate limiting
            return student_data
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL {url}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse HTML: {str(e)}")
    
    def auto_detect_student_data(self, url: str) -> List[Dict[str, Any]]:
        """Automatically detect and extract student data from a webpage"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            students_data = []
            
            # Look for tables that might contain student data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 2:  # Skip tables with less than 2 rows
                    continue
                
                # Try to identify header row
                header_row = rows[0]
                headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
                
                # Check if this looks like a student table
                student_indicators = ['student', 'id', 'name', 'score', 'sinh viên', 'điểm', 'tên']
                if not any(indicator in ' '.join(headers) for indicator in student_indicators):
                    continue
                
                # Map headers to our fields
                field_mapping = {}
                for i, header in enumerate(headers):
                    if any(term in header for term in ['id', 'mã', 'msv']):
                        field_mapping[i] = 'student_id'
                    elif any(term in header for term in ['họ', 'first', 'surname']):
                        field_mapping[i] = 'first_name'
                    elif any(term in header for term in ['tên', 'last', 'given']):
                        field_mapping[i] = 'last_name'
                    elif 'email' in header:
                        field_mapping[i] = 'email'
                    elif any(term in header for term in ['sinh', 'birth', 'date']):
                        field_mapping[i] = 'birth_date'
                    elif any(term in header for term in ['quê', 'home', 'town']):
                        field_mapping[i] = 'hometown'
                    elif any(term in header for term in ['toán', 'math']):
                        field_mapping[i] = 'math_score'
                    elif any(term in header for term in ['văn', 'literature']):
                        field_mapping[i] = 'literature_score'
                    elif any(term in header for term in ['anh', 'english']):
                        field_mapping[i] = 'english_score'
                
                # Extract data rows
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) == 0:
                        continue
                    
                    student_data = {}
                    for i, cell in enumerate(cells):
                        if i in field_mapping:
                            text = cell.get_text(strip=True)
                            student_data[field_mapping[i]] = text if text else None
                    
                    if student_data and len(student_data) >= 3:  # At least 3 fields
                        students_data.append(student_data)
                
                if students_data:  # If we found data in this table, break
                    break
            
            time.sleep(settings.CRAWLER_DELAY)  # Rate limiting
            return students_data
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL {url}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse HTML: {str(e)}")
    
    def clean_crawled_data(self, raw_data: List[Dict[str, Any]]) -> List[StudentCreate]:
        """Clean and validate crawled student data"""
        students = []
        
        for data in raw_data:
            try:
                # Clean and validate each field
                cleaned_data = {}
                
                # Student ID
                if 'student_id' in data and data['student_id']:
                    student_id = re.sub(r'[^\w]', '', str(data['student_id']))
                    if len(student_id) >= 6:
                        cleaned_data['student_id'] = student_id.upper()
                
                # Names
                if 'first_name' in data and data['first_name']:
                    cleaned_data['first_name'] = str(data['first_name']).strip()
                if 'last_name' in data and data['last_name']:
                    cleaned_data['last_name'] = str(data['last_name']).strip()
                
                # Email
                if 'email' in data and data['email']:
                    email = str(data['email']).strip()
                    if '@' in email and '.' in email:
                        cleaned_data['email'] = email
                
                # Hometown
                if 'hometown' in data and data['hometown']:
                    cleaned_data['hometown'] = str(data['hometown']).strip()
                
                # Birth date
                if 'birth_date' in data and data['birth_date']:
                    try:
                        birth_date = pd.to_datetime(data['birth_date']).date()
                        cleaned_data['birth_date'] = birth_date
                    except:
                        pass
                
                # Scores
                for score_field in ['math_score', 'literature_score', 'english_score']:
                    if score_field in data and data[score_field]:
                        try:
                            score = float(str(data[score_field]).replace(',', '.'))
                            if 0 <= score <= 10:
                                cleaned_data[score_field] = score
                            elif 0 <= score <= 100:  # Convert from 100 scale
                                cleaned_data[score_field] = score / 10
                        except:
                            pass
                
                # Create student if we have minimum required fields
                if ('student_id' in cleaned_data and 
                    'first_name' in cleaned_data and 
                    'last_name' in cleaned_data):
                    
                    student = StudentCreate(**cleaned_data)
                    students.append(student)
                    
            except Exception:
                continue  # Skip invalid records
        
        return students
    
    def save_to_excel(self, students_data: List[Dict[str, Any]], filename: str) -> str:
        """Save crawled data to Excel file"""
        df = pd.DataFrame(students_data)
        
        # Clean column names
        df.columns = [col.replace(' ', '_').lower() for col in df.columns]
        
        filepath = f"{settings.UPLOAD_DIR}/{filename}"
        df.to_excel(filepath, index=False)
        
        return filepath