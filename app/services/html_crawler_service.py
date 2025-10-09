"""
HTML Crawler Service

Parses HTML files to extract student data structure and information.
Uses BeautifulSoup for HTML parsing.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import re

class HTMLCrawlerService:
    """
    Service for crawling and parsing HTML files
    
    Methods:
        parse_html_table_structure(): Extract table structure from HTML
        extract_student_data(): Extract actual student data from HTML tables
        clean_text(): Clean and normalize text data
    """
    
    def __init__(self):
        """Initialize HTML crawler service"""
        self.soup = None
        
    def parse_html_table_structure(self, html_file_path: str) -> Dict[str, Any]:
        """
        Parse HTML file to understand table structure
        
        Extracts column headers and table structure from the students table
        in the frontend HTML file.
        
        Args:
            html_file_path: Path to the HTML file
        
        Returns:
            Dict containing table structure info:
                - columns: List of column headers
                - table_id: ID of the table element
                - has_pagination: Whether table has pagination
                - has_filters: Whether table has filters
        
        Example:
            structure = parser.parse_html_table_structure("index.html")
            print(structure['columns'])  # ['Mã SV', 'Họ tên', ...]
        """
        # Read HTML file
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML
        self.soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find students table
        table = self.soup.find('table', {'id': 'studentsTable'})
        
        if not table:
            raise ValueError("Students table not found in HTML")
        
        # Extract column headers
        headers = []
        thead = table.find('thead')
        if thead:
            header_row = thead.find('tr')
            if header_row:
                for th in header_row.find_all('th'):
                    # Get text content, strip whitespace
                    header_text = th.get_text(strip=True)
                    # Skip checkbox and action columns
                    if header_text and header_text not in ['', 'Thao tác']:
                        # Extract sort attribute if exists
                        sort_attr = th.get('data-sort', None)
                        headers.append({
                            'label': header_text,
                            'field': sort_attr,
                            'sortable': 'sortable' in th.get('class', [])
                        })
        
        # Check for pagination
        pagination = self.soup.find('div', {'id': 'pagination'}) is not None
        
        # Check for filters
        search_input = self.soup.find('input', {'id': 'searchInput'}) is not None
        hometown_filter = self.soup.find('select', {'id': 'hometownFilter'}) is not None
        grade_filter = self.soup.find('select', {'id': 'gradeFilter'}) is not None
        
        structure = {
            'table_id': 'studentsTable',
            'columns': headers,
            'has_pagination': pagination,
            'has_search': search_input,
            'has_filters': hometown_filter or grade_filter,
            'features': {
                'search': search_input,
                'hometown_filter': hometown_filter,
                'grade_filter': grade_filter,
                'sorting': any(h['sortable'] for h in headers)
            }
        }
        
        return structure
    
    def extract_stat_cards(self, html_file_path: str) -> List[Dict[str, str]]:
        """
        Extract stat card structure from HTML
        
        Args:
            html_file_path: Path to HTML file
        
        Returns:
            List of stat card configurations
        """
        if not self.soup:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.soup = BeautifulSoup(html_content, 'html.parser')
        
        stat_cards = []
        stats_grid = self.soup.find('div', class_='stats-grid')
        
        if stats_grid:
            for card in stats_grid.find_all('div', class_='stat-card'):
                icon_elem = card.find('i')
                icon_class = icon_elem.get('class', []) if icon_elem else []
                
                heading = card.find('h3')
                paragraph = card.find('p')
                
                stat_cards.append({
                    'icon': ' '.join(icon_class) if icon_class else '',
                    'id': heading.get('id', '') if heading else '',
                    'label': paragraph.get_text(strip=True) if paragraph else ''
                })
        
        return stat_cards
    
    def extract_chart_configs(self, html_file_path: str) -> List[Dict[str, str]]:
        """
        Extract chart canvas IDs from analytics section
        
        Args:
            html_file_path: Path to HTML file
        
        Returns:
            List of chart configurations
        """
        if not self.soup:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.soup = BeautifulSoup(html_content, 'html.parser')
        
        charts = []
        analytics_section = self.soup.find('section', {'id': 'analytics-section'})
        
        if analytics_section:
            for canvas in analytics_section.find_all('canvas'):
                canvas_id = canvas.get('id', '')
                if canvas_id:
                    # Find parent card to get title
                    parent_card = canvas.find_parent('div', class_='analytics-card')
                    title = ''
                    if parent_card:
                        h3 = parent_card.find('h3')
                        if h3:
                            title = h3.get_text(strip=True)
                    
                    charts.append({
                        'canvas_id': canvas_id,
                        'title': title
                    })
        
        return charts
    
    def clean_text(self, text: Optional[str]) -> str:
        """
        Clean and normalize text data
        
        Args:
            text: Raw text to clean
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Strip whitespace
        text = text.strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Vietnamese
        # text = re.sub(r'[^\w\s\u00C0-\u1EF9@.-]', '', text)
        
        return text
    
    def validate_table_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate extracted table data
        
        Args:
            data: List of data dictionaries
        
        Returns:
            True if data is valid
        """
        if not data:
            return False
        
        # Check if all rows have required fields
        required_fields = ['student_id', 'full_name']
        
        for row in data:
            if not all(field in row for field in required_fields):
                return False
        
        return True
