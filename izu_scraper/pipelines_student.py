import csv
from pathlib import Path

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
