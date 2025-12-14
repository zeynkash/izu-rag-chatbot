import re
import csv
import hashlib
from datetime import datetime
from pathlib import Path
from scrapy.exceptions import DropItem
from langdetect import detect, LangDetectException


class CleaningPipeline:
    """Clean and normalize text content"""
    
    def process_item(self, item, spider):
        if item.get('title'):
            item['title'] = self.clean_text(item['title'])
        
        if item.get('content'):
            item['content'] = self.clean_text(item['content'])
            
            if len(item['content']) < 100:
                raise DropItem(f"Content too short: {item['url']}")
        
        if item.get('meta_description'):
            item['meta_description'] = self.clean_text(item['meta_description'])
        
        return item
    
    def clean_text(self, text):
        """Clean text by removing CSS, JS, and extra whitespace"""
        if not text:
            return ""
        
        # Remove CSS/JS patterns
        text = re.sub(r'\{[^}]*\}', ' ', text)
        text = re.sub(r'@media[^{]*', ' ', text)
        text = re.sub(r'position\s*:\s*\w+', ' ', text)
        text = re.sub(r'margin\s*:\s*[\w\s%]+', ' ', text)
        text = re.sub(r'padding\s*:\s*[\w\s%]+', ' ', text)
        text = re.sub(r'width\s*:\s*[\w\s%]+', ' ', text)
        text = re.sub(r'overflow\s*:\s*\w+', ' ', text)
        text = re.sub(r'#[\w-]+\s*\{', ' ', text)
        
        # Remove HTML entities
        text = re.sub(r'&[a-z]+;', ' ', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()


class LanguageDetectionPipeline:
    """Detect and validate content language"""
    
    def process_item(self, item, spider):
        if not item.get('content'):
            return item
        
        try:
            detected_lang = detect(item['content'])
            
            if detected_lang in ['tr', 'en']:
                item['language'] = detected_lang
            else:
                if '/en/' in item['url']:
                    item['language'] = 'en'
                else:
                    item['language'] = 'tr'
                    
        except LangDetectException:
            if '/en/' in item['url']:
                item['language'] = 'en'
            else:
                item['language'] = 'tr'
        
        return item


class CategorizationPipeline:
    """Categorize content based on URL patterns"""
    
    def process_item(self, item, spider):
        url = item['url'].lower()
        section_patterns = spider.settings.get('SECTION_PATTERNS')
        
        item['section'] = 'general'
        
        for section, patterns in section_patterns.items():
            for pattern in patterns:
                if pattern in url:
                    item['section'] = section
                    break
            if item['section'] != 'general':
                break
        
        return item


class DuplicatesPipeline:
    """Remove duplicate content using content hashing"""
    
    def __init__(self):
        self.seen_hashes = set()
        self.seen_urls = set()
    
    def process_item(self, item, spider):
        if item['url'] in self.seen_urls:
            raise DropItem(f"Duplicate URL: {item['url']}")
        
        if item.get('content'):
            content_hash = hashlib.md5(item['content'].encode()).hexdigest()
            
            if content_hash in self.seen_hashes:
                raise DropItem(f"Duplicate content: {item['url']}")
            
            self.seen_hashes.add(content_hash)
        
        self.seen_urls.add(item['url'])
        return item


class CSVExportPipeline:
    """Export items to CSV files by section and language"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.files = {}
        self.writers = {}
        self.csv_headers = [
            'url', 'title', 'language', 'content', 'meta_description',
            'breadcrumb', 'section', 'subsection', 'images', 'documents',
            'contact_info', 'last_updated', 'date_scraped', 'response_status',
            'content_length'
        ]
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            output_dir=crawler.settings.get('CSV_OUTPUT_DIR', 'output')
        )
    
    def open_spider(self, spider):
        """Create output directories"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'turkish').mkdir(exist_ok=True)
        (self.output_dir / 'english').mkdir(exist_ok=True)
    
    def close_spider(self, spider):
        """Close all open CSV files"""
        for f in self.files.values():
            f.close()
    
    def process_item(self, item, spider):
        """Write item to appropriate CSV file"""
        section = item.get('section', 'general')
        language = item.get('language', 'tr')
        
        lang_dir = 'turkish' if language == 'tr' else 'english'
        lang_suffix = 'tr' if language == 'tr' else 'en'
        file_key = f"{section}_{lang_suffix}"
        file_path = self.output_dir / lang_dir / f"{section}_{lang_suffix}.csv"
        
        if file_key not in self.files:
            file_exists = file_path.exists()
            self.files[file_key] = open(file_path, 'a', newline='', encoding='utf-8')
            self.writers[file_key] = csv.DictWriter(
                self.files[file_key],
                fieldnames=self.csv_headers,
                extrasaction='ignore'
            )
            
            if not file_exists:
                self.writers[file_key].writeheader()
        
        self.writers[file_key].writerow(dict(item))
        
        return item
class StudentPagesPipeline:
    """Export all pages to single CSV per language"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.files = {}
        self.writers = {}
        self.csv_headers = [
            'url', 'title', 'language', 'content', 'meta_description',
            'breadcrumb', 'section', 'subsection', 'images', 'documents',
            'contact_info', 'last_updated', 'date_scraped', 'response_status',
            'content_length'
        ]
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(output_dir=crawler.settings.get('CSV_OUTPUT_DIR', 'output'))
    
    def open_spider(self, spider):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Open single file for each language
        for lang, filename in [('tr', 'all_student_pages_turkish.csv'), 
                                ('en', 'all_student_pages_english.csv')]:
            filepath = self.output_dir / filename
            self.files[lang] = open(filepath, 'w', newline='', encoding='utf-8')
            self.writers[lang] = csv.DictWriter(
                self.files[lang],
                fieldnames=self.csv_headers,
                extrasaction='ignore'
            )
            self.writers[lang].writeheader()
    
    def close_spider(self, spider):
        for f in self.files.values():
            f.close()
    
    def process_item(self, item, spider):
        language = item.get('language', 'tr')
        lang_key = 'en' if language == 'en' else 'tr'
        
        if lang_key in self.writers:
            self.writers[lang_key].writerow(dict(item))
        
        return item
class CleanStudentPipeline:
    """Export clean student pages to single CSV per language"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.files = {}
        self.writers = {}
        self.csv_headers = [
            'url', 'title', 'language', 'content', 'meta_description',
            'breadcrumb', 'sidebar_urls', 'images', 'documents',
            'contact_info', 'last_updated', 'date_scraped',
            'content_length'
        ]
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(output_dir=crawler.settings.get('CSV_OUTPUT_DIR', 'output'))
    
    def open_spider(self, spider):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        for lang, filename in [('tr', 'clean_student_turkish.csv'), 
                                ('en', 'clean_student_english.csv')]:
            filepath = self.output_dir / filename
            self.files[lang] = open(filepath, 'w', newline='', encoding='utf-8')
            self.writers[lang] = csv.DictWriter(
                self.files[lang],
                fieldnames=self.csv_headers,
                extrasaction='ignore'
            )
            self.writers[lang].writeheader()
    
    def close_spider(self, spider):
        for f in self.files.values():
            f.close()
    
    def process_item(self, item, spider):
        language = item.get('language', 'tr')
        lang_key = 'en' if language == 'en' else 'tr'
        
        # Rename subsection to sidebar_urls for CSV
        csv_item = dict(item)
        csv_item['sidebar_urls'] = csv_item.pop('subsection', '')
        csv_item.pop('section', None)
        csv_item.pop('response_status', None)
        
        if lang_key in self.writers:
            self.writers[lang_key].writerow(csv_item)
        
        return item
