"""
Extraction Strategies for Different Content Types
Specialized methods to extract structured information from IZU pages
"""

from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup, Tag
import re
from crawler_utils import (
    extract_emails, extract_phones, extract_dates, 
    extract_price, extract_program_info, clean_turkish_text
)


class ExtractionStrategy:
    """Base class for extraction strategies"""
    
    def __init__(self, soup: BeautifulSoup, url: str):
        self.soup = soup
        self.url = url
    
    def extract(self) -> Optional[Dict[str, Any]]:
        """Extract data - to be implemented by subclasses"""
        raise NotImplementedError


class AcademicProgramExtractor(ExtractionStrategy):
    """Extract academic program information"""
    
    def extract(self) -> Optional[Dict[str, Any]]:
        data = {'url': self.url}
        
        # Program name
        title = self.soup.find('h1')
        if title:
            data['program_name'] = clean_turkish_text(title.get_text())
        
        # Extract from meta tags
        meta_desc = self.soup.find('meta', {'name': 'description'})
        if meta_desc:
            data['description'] = meta_desc.get('content', '')
        
        # Get all text for analysis
        content_text = self.soup.get_text()
        
        # Extract program info (degree, duration, language)
        program_info = extract_program_info(content_text)
        data.update(program_info)
        
        # Extract faculty/department from breadcrumb or URL
        breadcrumb = self.soup.find('nav', class_=re.compile('breadcrumb', re.I))
        if breadcrumb:
            items = breadcrumb.find_all('a')
            if len(items) >= 2:
                data['faculty'] = clean_turkish_text(items[1].get_text())
            if len(items) >= 3:
                data['department'] = clean_turkish_text(items[2].get_text())
        
        # Extract admission requirements (look for lists)
        for heading in self.soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text().lower()
            if any(kw in heading_text for kw in ['gereklilik', 'şart', 'requirement', 'admission', 'başvuru']):
                # Find next list
                next_list = heading.find_next(['ul', 'ol'])
                if next_list:
                    requirements = [clean_turkish_text(li.get_text()) for li in next_list.find_all('li')]
                    data['admission_requirements'] = [r for r in requirements if r]
        
        # Extract fees
        price_info = extract_price(content_text)
        if price_info:
            data['tuition_fee'] = f"{price_info['amount']} {price_info['currency']}"
        
        # Extract curriculum/courses
        for heading in self.soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text().lower()
            if any(kw in heading_text for kw in ['müfredat', 'ders', 'curriculum', 'course']):
                next_list = heading.find_next(['ul', 'ol', 'table'])
                if next_list:
                    if next_list.name == 'table':
                        courses = []
                        for row in next_list.find_all('tr')[1:]:  # Skip header
                            cells = row.find_all(['td', 'th'])
                            if cells:
                                course = clean_turkish_text(cells[0].get_text())
                                if course:
                                    courses.append(course)
                        data['curriculum'] = courses
                    else:
                        courses = [clean_turkish_text(li.get_text()) for li in next_list.find_all('li')]
                        data['curriculum'] = [c for c in courses if c]
        
        return data if len(data) > 1 else None


class FacultyMemberExtractor(ExtractionStrategy):
    """Extract faculty member profile information"""
    
    def extract(self) -> Optional[Dict[str, Any]]:
        data = {'url': self.url}
        
        # Name from h1 or title
        name_elem = self.soup.find('h1')
        if name_elem:
            data['name'] = clean_turkish_text(name_elem.get_text())
        
        # Title and department
        content_text = self.soup.get_text()
        
        # Extract title (Prof., Dr., Doç., etc.)
        title_patterns = [
            r'(Prof\.?\s*Dr\.?)',
            r'(Doç\.?\s*Dr\.?)',
            r'(Dr\.?\s*Öğr\.?\s*Üyesi)',
            r'(Öğr\.?\s*Gör\.?)',
            r'(Arş\.?\s*Gör\.?)',
        ]
        for pattern in title_patterns:
            match = re.search(pattern, content_text, re.IGNORECASE)
            if match:
                data['title'] = match.group(1)
                break
        
        # Extract email
        emails = extract_emails(content_text)
        if emails:
            data['email'] = emails[0]
        
        # Extract phone
        phones = extract_phones(content_text)
        if phones:
            data['phone'] = phones[0]
        
        # Extract research areas
        for heading in self.soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text().lower()
            if any(kw in heading_text for kw in ['araştırma alan', 'research area', 'uzmanlık', 'expertise']):
                next_list = heading.find_next(['ul', 'ol'])
                if next_list:
                    areas = [clean_turkish_text(li.get_text()) for li in next_list.find_all('li')]
                    data['research_areas'] = [a for a in areas if a]
        
        # Extract education
        for heading in self.soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text().lower()
            if any(kw in heading_text for kw in ['eğitim', 'education', 'öğrenim']):
                next_list = heading.find_next(['ul', 'ol'])
                if next_list:
                    education = [clean_turkish_text(li.get_text()) for li in next_list.find_all('li')]
                    data['education'] = [e for e in education if e]
        
        # Extract courses
        for heading in self.soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text().lower()
            if any(kw in heading_text for kw in ['verdiği ders', 'course', 'ders']):
                next_list = heading.find_next(['ul', 'ol'])
                if next_list:
                    courses = [clean_turkish_text(li.get_text()) for li in next_list.find_all('li')]
                    data['courses'] = [c for c in courses if c]
        
        return data if 'name' in data else None


class AdmissionExtractor(ExtractionStrategy):
    """Extract admission and application information"""
    
    def extract(self) -> Optional[Dict[str, Any]]:
        data = {'url': self.url}
        
        content_text = self.soup.get_text()
        
        # Extract deadlines
        dates = extract_dates(content_text)
        if dates:
            data['application_deadline'] = dates[0]
        
        # Extract requirements
        for heading in self.soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text().lower()
            if any(kw in heading_text for kw in ['gerekli belgeler', 'required document', 'başvuru belge']):
                next_list = heading.find_next(['ul', 'ol'])
                if next_list:
                    docs = [clean_turkish_text(li.get_text()) for li in next_list.find_all('li')]
                    data['required_documents'] = [d for d in docs if d]
            
            if any(kw in heading_text for kw in ['başvuru koşul', 'admission requirement', 'koşul']):
                next_list = heading.find_next(['ul', 'ol'])
                if next_list:
                    reqs = [clean_turkish_text(li.get_text()) for li in next_list.find_all('li')]
                    data['requirements'] = [r for r in reqs if r]
            
            if any(kw in heading_text for kw in ['başvuru süreci', 'application process', 'nasıl başvuru']):
                next_list = heading.find_next(['ul', 'ol'])
                if next_list:
                    steps = [clean_turkish_text(li.get_text()) for li in next_list.find_all('li')]
                    data['application_process'] = [s for s in steps if s]
        
        # Extract exam information
        exam_keywords = ['yks', 'ales', 'gmat', 'gre', 'toefl', 'ielts', 'ydil']
        for keyword in exam_keywords:
            if re.search(rf'\b{keyword}\b', content_text, re.IGNORECASE):
                if 'entrance_exams' not in data:
                    data['entrance_exams'] = []
                data['entrance_exams'].append(keyword.upper())
        
        return data if len(data) > 1 else None


class FeeExtractor(ExtractionStrategy):
    """Extract fee and cost information"""
    
    def extract(self) -> Optional[Dict[str, Any]]:
        data = {'url': self.url}
        
        content_text = self.soup.get_text()
        
        # Extract tuition fees
        price_info = extract_price(content_text)
        if price_info:
            data['tuition_fee'] = f"{price_info['amount']} {price_info['currency']}"
        
        # Look for fee tables
        tables = self.soup.find_all('table')
        for table in tables:
            header_text = ''
            for th in table.find_all('th'):
                header_text += th.get_text().lower()
            
            # Check if it's a fee table
            if any(kw in header_text for kw in ['ücret', 'fee', 'tuition', 'harç', 'fee']):
                rows = table.find_all('tr')
                data['other_fees'] = {}
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        fee_name = clean_turkish_text(cells[0].get_text())
                        fee_amount = clean_turkish_text(cells[1].get_text())
                        if fee_name and fee_amount:
                            data['other_fees'][fee_name] = fee_amount
        
        # Extract scholarship info
        for heading in self.soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text().lower()
            if any(kw in heading_text for kw in ['burs', 'scholarship', 'indirim', 'discount']):
                data['scholarship_available'] = True
                next_elem = heading.find_next(['p', 'ul', 'ol'])
                if next_elem:
                    if next_elem.name in ['ul', 'ol']:
                        scholarships = [clean_turkish_text(li.get_text()) for li in next_elem.find_all('li')]
                        data['scholarship_details'] = [s for s in scholarships if s]
                    else:
                        data['scholarship_details'] = [clean_turkish_text(next_elem.get_text())]
        
        return data if 'tuition_fee' in data or 'other_fees' in data else None


class EventExtractor(ExtractionStrategy):
    """Extract event information"""
    
    def extract(self) -> Optional[Dict[str, Any]]:
        data = {'url': self.url}
        
        # Event title
        title_elem = self.soup.find('h1')
        if title_elem:
            data['title'] = clean_turkish_text(title_elem.get_text())
        
        content_text = self.soup.get_text()
        
        # Extract date
        dates = extract_dates(content_text)
        if dates:
            data['date'] = dates[0]
        
        # Extract time
        time_pattern = r'\b(\d{1,2}:\d{2})\b'
        time_match = re.search(time_pattern, content_text)
        if time_match:
            data['time'] = time_match.group(1)
        
        # Extract location
        location_indicators = ['konum', 'yer', 'location', 'venue', 'mekan']
        for indicator in location_indicators:
            pattern = rf'{indicator}\s*:?\s*([^\n\.]+)'
            match = re.search(pattern, content_text, re.IGNORECASE)
            if match:
                data['location'] = clean_turkish_text(match.group(1))
                break
        
        # Extract description
        meta_desc = self.soup.find('meta', {'name': 'description'})
        if meta_desc:
            data['description'] = meta_desc.get('content', '')
        elif self.soup.find('p'):
            # First paragraph as description
            first_p = self.soup.find('p')
            data['description'] = clean_turkish_text(first_p.get_text())
        
        return data if 'title' in data else None


class NewsExtractor(ExtractionStrategy):
    """Extract news article information"""
    
    def extract(self) -> Optional[Dict[str, Any]]:
        data = {'url': self.url}
        
        # Article title
        title_elem = self.soup.find('h1')
        if title_elem:
            data['title'] = clean_turkish_text(title_elem.get_text())
        
        # Date
        date_elem = self.soup.find('time')
        if date_elem:
            data['date'] = date_elem.get('datetime', date_elem.get_text())
        else:
            content_text = self.soup.get_text()
            dates = extract_dates(content_text)
            if dates:
                data['date'] = dates[0]
        
        # Category from breadcrumb or meta
        breadcrumb = self.soup.find('nav', class_=re.compile('breadcrumb', re.I))
        if breadcrumb:
            items = breadcrumb.find_all('a')
            if items:
                data['category'] = clean_turkish_text(items[-1].get_text())
        
        # Content
        article = self.soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            content = ' '.join([clean_turkish_text(p.get_text()) for p in paragraphs])
            data['content'] = content
            # First paragraph as summary
            if paragraphs:
                data['summary'] = clean_turkish_text(paragraphs[0].get_text())
        
        # Image
        img = self.soup.find('img', class_=re.compile('featured|main|article', re.I))
        if img:
            data['image_url'] = img.get('src', '')
        
        return data if 'title' in data else None


def get_extractor(url: str, soup: BeautifulSoup, category: str) -> Optional[ExtractionStrategy]:
    """
    Get appropriate extractor based on content category
    
    Args:
        url: Page URL
        soup: BeautifulSoup object
        category: Content category
        
    Returns:
        Appropriate extractor instance or None
    """
    extractors = {
        'academic_program': AcademicProgramExtractor,
        'faculty_member': FacultyMemberExtractor,
        'admission': AdmissionExtractor,
        'fee_structure': FeeExtractor,
        'event': EventExtractor,
        'news': NewsExtractor,
    }
    
    extractor_class = extractors.get(category)
    return extractor_class(soup, url) if extractor_class else None
