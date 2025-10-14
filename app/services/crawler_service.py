# -*- coding: utf-8 -*-
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
    
    def crawl_frontend_page(self, url: str) -> List[Dict[str, Any]]:
        """Crawl student data from frontend page on http://127.0.0.1:5500 (HTML first, API fallback)"""
        try:
            # Fixed URLs
            FRONTEND_URL = "http://127.0.0.1:5500/"
            API_BASE_URL = "http://127.0.0.1:8000"
            
            # Method 1: Parse HTML from frontend URL first (priority)
            try:
                # Use fixed frontend URL or provided URL
                html_url = FRONTEND_URL if not url.startswith('http') else url
                
                # Get HTML content
                if html_url.startswith('file://'):
                    import os
                    file_path = html_url.replace('file:///', '').replace('/', os.sep)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                else:
                    response = self.session.get(html_url, timeout=10)
                    response.raise_for_status()
                    html_content = response.content
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract student data from HTML table
                students_data = self._extract_student_data_from_soup(soup)
                
                if students_data:
                    return students_data
                    
            except Exception as html_error:
                pass  # Fall back to API
            
            # Method 2: Fallback to API if HTML parsing fails or returns no data
            try:
                students_data = []
                api_url = f"{API_BASE_URL}/api/v1/students?limit=1000"
                
                api_response = self.session.get(api_url, timeout=10)
                if api_response.status_code == 200:
                    # Handle XML response (our API returns XML)
                    if 'xml' in api_response.headers.get('content-type', '').lower():
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(api_response.content)
                        
                        for student_elem in root.findall('student'):
                            student_data = {}
                            for child in student_elem:
                                student_data[child.tag] = child.text
                            
                            if student_data.get('student_id') and student_data.get('first_name'):
                                students_data.append(student_data)
                    
                    if students_data:
                        return students_data
                        
            except Exception as api_error:
                pass
            
            # If both methods fail, return empty list
            return []
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch frontend URL {url}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse frontend HTML: {str(e)}")
    
    def _extract_student_data_from_soup(self, soup) -> List[Dict[str, Any]]:
        """Helper method to extract student data from BeautifulSoup object"""
        students_data = []
        
        # Look for student table - try multiple selectors
        student_table = (
            soup.find('table', {'id': 'studentsTable'}) or 
            soup.find('table', class_='students-table') or
            soup.find('table', class_='table') or
            soup.find('table')  # Any table as fallback
        )
        
        if not student_table:
            return []
        
        rows = student_table.find_all('tr')
        if not rows:
            return []
        
        # Try to detect header row and data rows
        headers = []
        data_start_row = 0
        
        # Check first few rows for headers
        for i, row in enumerate(rows[:3]):
            cells = row.find_all(['th', 'td'])
            row_text = [cell.get_text(strip=True).lower() for cell in cells]
            
            # Look for header indicators
            if any(indicator in ' '.join(row_text) for indicator in ['mã sv', 'họ tên', 'email', 'điểm', 'student_id', 'name']):
                headers = row_text
                data_start_row = i + 1
                break
        
        # Create dynamic field mapping based on headers
        field_mapping = {}
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if any(term in header_lower for term in ['mã sv', 'student_id', 'id']):
                field_mapping[i] = 'student_id'
            elif any(term in header_lower for term in ['họ tên', 'name', 'tên']):
                field_mapping[i] = 'full_name'
            elif 'email' in header_lower:
                field_mapping[i] = 'email'
            elif any(term in header_lower for term in ['toán', 'math']):
                field_mapping[i] = 'math_score'
            elif any(term in header_lower for term in ['văn', 'literature']):
                field_mapping[i] = 'literature_score'
            elif any(term in header_lower for term in ['anh', 'english']):
                field_mapping[i] = 'english_score'
        
        # Use positional mapping if no headers detected
        if not field_mapping:
            field_mapping = {
                0: 'student_id', 1: 'student_id', 2: 'full_name', 3: 'email',
                4: 'birth_date', 5: 'hometown', 6: 'math_score', 
                7: 'literature_score', 8: 'english_score'
            }
            data_start_row = 1
        
        # Extract data from rows (skip headers)
        for row in rows[data_start_row:]:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            
            student_data = {}
            
            # Extract cell data using field mapping
            for col_idx, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # Skip checkbox or empty cells
                if not cell_text or cell_text in ['☐', '☑', '', ' ']:
                    continue
                    
                if col_idx in field_mapping:
                    field_name = field_mapping[col_idx]
                    
                    # Handle full name splitting for first_name/last_name compatibility
                    if field_name == 'full_name' and cell_text:
                        name_parts = cell_text.split()
                        if len(name_parts) >= 2:
                            student_data['first_name'] = name_parts[-1]
                            student_data['last_name'] = ' '.join(name_parts[:-1])
                        else:
                            student_data['first_name'] = cell_text
                            student_data['last_name'] = ''
                        student_data['full_name'] = cell_text
                    else:
                        student_data[field_name] = cell_text
            
            # Validate and clean student data
            if student_data and (student_data.get('student_id') or student_data.get('full_name')):
                # Clean numeric scores
                for score_field in ['math_score', 'literature_score', 'english_score']:
                    if score_field in student_data:
                        try:
                            score_str = student_data[score_field]
                            numeric_match = re.search(r'\d+(\.\d+)?', score_str)
                            if numeric_match:
                                student_data[score_field] = float(numeric_match.group())
                            else:
                                del student_data[score_field]
                        except:
                            if score_field in student_data:
                                del student_data[score_field]
                
                students_data.append(student_data)
        
        return students_data

    def auto_detect_student_data(self, url: str) -> List[Dict[str, Any]]:
        """Automatically detect and extract student data from a webpage"""
        try:
            # First, try our specific frontend crawler for any local URLs or HTML files
            # This includes localhost, 127.0.0.1, file://, or any URL containing our frontend patterns
            if any(pattern in url for pattern in ['localhost', '127.0.0.1', 'index.html', 'file://', ':3000', ':8080', ':5000']):
                result = self.crawl_frontend_page(url)
                return result
            
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