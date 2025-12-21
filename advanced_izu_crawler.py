"""
Advanced IZU University Web Crawler
Intelligent web crawler with structured data extraction for university chatbot

Features:
- Automatic content categorization
- Structured data extraction for programs, faculty, fees, events
- Multi-language support (Turkish/English)
- Smart deduplication
- Multiple export formats (JSON, CSV, JSONL)
"""

from requests_html import HTMLSession
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
from collections import deque
import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional, Set
import warnings
warnings.filterwarnings('ignore')

from izu_data_models import PageData, ContentCategory, create_structured_data
from extraction_strategies import get_extractor
from crawler_utils import (
    calculate_content_hash, clean_turkish_text, detect_language,
    extract_emails, extract_phones, similarity_ratio
)


class AdvancedIZUCrawler:
    """Advanced web crawler for IZU university website"""
    
    def __init__(self, base_url: str = "https://www.izu.edu.tr"):
        self.base_url = base_url
        self.visited = set()
        self.content_hashes = set()  # For deduplication
        self.pages_data: List[PageData] = []
        self.queue = deque()
        self.session = HTMLSession()
        
        # Statistics
        self.stats = {
            'pages_crawled': 0,
            'pages_saved': 0,
            'duplicates_skipped': 0,
            'categories': {}
        }
        
        # Noise patterns to remove
        self.noise_patterns = [
            r'Medya\s*Kampüs\s*İnsan Kaynakları\s*İletişim',
            r'Turkish Language Center\s*International Students\s*Erasmus\+\s*Contact',
            r'AKADEMİK\s*ARAŞTIRMA\s*ÖĞRENCİ\s*ULUSLARARASI\s*ADAY ÖĞRENCİ\s*İZÜ HAKKINDA',
            r'Academic\s*Research\s*Students\s*International\s*About IZU',
            r'Search\s*Türkçe\s*English\s*Ara',
            r'E-HİZMETLER\s*KURUMSAL\s*BAĞLANTILAR\s*BİZE ULAŞIN\s*HIZLI ERİŞİM',
            r'Facebook\s*Twitter\s*Instagram\s*Youtube\s*Linkedin',
            r'© IZU \d{4}',
        ]
        
    def categorize_url(self, url: str) -> str:
        """
        Categorize URL based on keywords and patterns
        
        Args:
            url: URL to categorize
            
        Returns:
            Category string
        """
        url_lower = url.lower()
        
        # Academic programs
        if any(kw in url_lower for kw in ['program', 'bolum', 'department', 'lisans', 'master', 'doktora', 'phd']):
            return ContentCategory.ACADEMIC_PROGRAM.value
        
        # Faculty/staff
        if any(kw in url_lower for kw in ['akademisyen', 'faculty', 'staff', 'ogretim-uyesi', 'personel']):
            return ContentCategory.FACULTY_MEMBER.value
        
        # Admission
        if any(kw in url_lower for kw in ['basvuru', 'admission', 'kayit', 'registration', 'kabul']):
            return ContentCategory.ADMISSION.value
        
        # Fees
        if any(kw in url_lower for kw in ['ucret', 'fee', 'tuition', 'harc', 'odeme', 'payment']):
            return ContentCategory.FEE_STRUCTURE.value
        
        # Events
        if any(kw in url_lower for kw in ['etkinlik', 'event', 'takvim', 'calendar', 'seminer', 'seminar']):
            return ContentCategory.EVENT.value
        
        # News
        if any(kw in url_lower for kw in ['haber', 'news', 'duyuru', 'announcement']):
            return ContentCategory.NEWS.value
        
        # Research
        if any(kw in url_lower for kw in ['arastirma', 'research', 'proje', 'project', 'yayin', 'publication']):
            return ContentCategory.RESEARCH.value
        
        # Student services
        if any(kw in url_lower for kw in ['ogrenci', 'student', 'servis', 'service', 'kulupler', 'clubs']):
            return ContentCategory.STUDENT_SERVICE.value
        
        return ContentCategory.GENERAL.value
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for crawling"""
        parsed = urlparse(url)
        domain_ok = 'izu.edu.tr' in parsed.netloc
        
        # Skip file downloads
        extension_ok = not any(ext in url.lower() for ext in 
                              ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', 
                               '.docx', '.zip', '.mp4', '.mp3', '.avi', '.xlsx', '.xml'])
        
        # Skip login/admin pages
        path_ok = not any(kw in url.lower() for kw in 
                         ['login', 'signin', 'logout', 'admin', 'wp-admin'])
        
        return domain_ok and extension_ok and path_ok
    
    def clean_text(self, text: str) -> str:
        """Clean text from noise"""
        if not text:
            return ""
        
        text = re.sub(r'\s+', ' ', text)
        
        for pattern in self.noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        common_words = ['Ara', 'Search', 'English', 'Türkçe', 'Menu', 'Close']
        for word in common_words:
            text = text.replace(word, '')
        
        text = clean_turkish_text(text)
        return text
    
    def extract_content(self, soup: BeautifulSoup, url: str, category: str) -> Optional[PageData]:
        """
        Extract comprehensive content from page
        
        Args:
            soup: BeautifulSoup object
            url: Page URL
            category: Content category
            
        Returns:
            PageData object or None
        """
        # Remove unwanted elements
        for tag in ['script', 'style', 'noscript', 'iframe', 'svg']:
            for element in soup.find_all(tag):
                element.decompose()
        
        for element in soup.find_all(['header', 'footer', 'nav', 'aside']):
            element.decompose()
        
        for element in soup.find_all(class_=re.compile(r'header|footer|nav|menu|sidebar|social|cookie', re.I)):
            element.decompose()
        
        # Extract title
        title = ""
        if soup.title:
            title = self.clean_text(soup.title.string or "")
        if not title and soup.h1:
            title = self.clean_text(soup.h1.get_text())
        
        # Find main content
        main_content = None
        for selector in ['main', 'article', '[role="main"]', '.content', 
                        '.main-content', '#content', '.page-content']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.body if soup.body else soup
        
        # Extract text content
        text_content = ""
        if main_content:
            text_parts = []
            for elem in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                text = elem.get_text(separator=' ', strip=True)
                if text and len(text) > 10:
                    text_parts.append(text)
            text_content = ' '.join(text_parts)
            text_content = self.clean_text(text_content)
        
        # Extract tables
        tables_data = []
        if main_content:
            for table in main_content.find_all('table'):
                rows = []
                for tr in table.find_all('tr'):
                    row = [self.clean_text(cell.get_text()) for cell in tr.find_all(['td', 'th'])]
                    row = [cell for cell in row if cell]
                    if row:
                        rows.append(row)
                if rows and len(rows) > 1:
                    tables_data.append(rows)
        
        # Extract lists
        lists_data = []
        if main_content:
            for lst in main_content.find_all(['ul', 'ol'])[:15]:
                items = [self.clean_text(li.get_text()) for li in lst.find_all('li', recursive=False)]
                items = [item for item in items if len(item) > 10]
                if items and len(items) > 2:
                    lists_data.append(items)
        
        # Extract images
        images = []
        for img in main_content.find_all('img')[:10] if main_content else []:
            img_url = img.get('src', '')
            if img_url:
                img_url = urljoin(url, img_url)
                images.append({
                    'url': img_url,
                    'alt': img.get('alt', ''),
                })
        
        # Extract documents
        documents = []
        for link in soup.find_all('a', href=re.compile(r'\.(pdf|doc|docx|xls|xlsx|ppt|pptx)$', re.I))[:10]:
            doc_url = link.get('href', '')
            if doc_url:
                doc_url = urljoin(url, doc_url)
                documents.append({
                    'url': doc_url,
                    'title': self.clean_text(link.get_text()),
                })
        
        # Extract contact info
        contact_info = {}
        emails = extract_emails(text_content)
        if emails:
            contact_info['emails'] = emails[:5]
        
        phones = extract_phones(text_content)
        if phones:
            contact_info['phones'] = phones[:5]
        
        # Extract breadcrumb
        breadcrumb = []
        breadcrumb_nav = soup.find('nav', class_=re.compile('breadcrumb', re.I))
        if breadcrumb_nav:
            breadcrumb = [self.clean_text(a.get_text()) for a in breadcrumb_nav.find_all('a')]
        
        # Meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        meta_description = meta_desc.get('content', '') if meta_desc else None
        
        # Detect language
        language = detect_language(text_content)
        
        # Calculate content hash for deduplication
        content_hash = calculate_content_hash(text_content)
        
        # Try structured extraction
        structured_data = None
        extractor = get_extractor(url, soup, category)
        if extractor:
            try:
                extracted = extractor.extract()
                if extracted:
                    structured_data = extracted
            except Exception as e:
                print(f"  ⚠ Structured extraction failed: {e}")
        
        # Create PageData object
        page_data = PageData(
            url=url,
            title=title,
            category=category,
            content=text_content,
            language=language,
            word_count=len(text_content.split()),
            tables=tables_data,
            lists=lists_data,
            images=images,
            documents=documents,
            contact_info=contact_info,
            breadcrumb=breadcrumb,
            meta_description=meta_description,
            date_scraped=datetime.now().isoformat(),
            content_hash=content_hash,
            structured_data=structured_data,
        )
        
        return page_data
    
    def get_links(self, soup: BeautifulSoup, current_url: str) -> Set[str]:
        """Extract valid links from page"""
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#', 'whatsapp:')):
                continue
            
            url = urljoin(current_url, href)
            url = url.split('#')[0].rstrip('/')
            
            if self.is_valid_url(url) and url not in self.visited:
                links.add(url)
        return links
    
    def crawl_page(self, url: str) -> Set[str]:
        """Crawl a single page"""
        try:
            response = self.session.get(url, timeout=20)
            
            # Try JavaScript rendering for dynamic content
            try:
                response.html.render(timeout=15, sleep=1)
            except:
                pass
            
            soup = BeautifulSoup(response.html.html, 'html.parser')
            
            # Categorize page
            category = self.categorize_url(url)
            
            # Extract content
            page_data = self.extract_content(soup, url, category)
            
            if page_data and page_data.word_count >= 30:
                # Check for duplicates
                if page_data.content_hash in self.content_hashes:
                    self.stats['duplicates_skipped'] += 1
                    print(f"  ⊘ Duplicate content (skipped)")
                    return self.get_links(soup, url)
                
                self.content_hashes.add(page_data.content_hash)
                self.pages_data.append(page_data)
                self.stats['pages_saved'] += 1
                
                # Update category stats
                if category not in self.stats['categories']:
                    self.stats['categories'][category] = 0
                self.stats['categories'][category] += 1
                
                info = f"{page_data.word_count} words | {category}"
                if page_data.structured_data:
                    info += " | ✓ Structured"
                if page_data.tables:
                    info += f" | {len(page_data.tables)} tables"
                print(f"  ✓ {info}")
            else:
                word_count = page_data.word_count if page_data else 0
                print(f"  ⊘ Only {word_count} words (skipped)")
            
            new_links = self.get_links(soup, url)
            return new_links
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:100]}")
            return set()
    
    def crawl(self, max_pages: int = 500, max_time_minutes: int = 40):
        """Main crawl function"""
        print("=" * 80)
        print("ADVANCED IZU WEBSITE CRAWLER")
        print("=" * 80)
        print(f"Target: {self.base_url}")
        print(f"Max pages: {max_pages}")
        print(f"Max time: {max_time_minutes} minutes")
        print("=" * 80 + "\n")
        
        start_time = time.time()
        max_time_seconds = max_time_minutes * 60
        
        # Starting URLs
        starting_urls = [
            self.base_url,
            self.base_url + "/en",
            self.base_url + "/tr",
            self.base_url + "/en/academic",
            self.base_url + "/en/faculties",
            self.base_url + "/en/students",
            self.base_url + "/en/international",
            self.base_url + "/tr/akademik",
            self.base_url + "/tr/fakulteler",
            self.base_url + "/tr/ogrenci",
        ]
        
        for url in starting_urls:
            if url not in self.visited:
                self.queue.append(url)
        
        while self.queue and self.stats['pages_crawled'] < max_pages:
            elapsed = time.time() - start_time
            if elapsed > max_time_seconds:
                print(f"\n⏱ Time limit reached ({max_time_minutes} minutes)")
                break
            
            url = self.queue.popleft()
            
            if url in self.visited:
                continue
            
            self.visited.add(url)
            self.stats['pages_crawled'] += 1
            
            print(f"\n[{self.stats['pages_crawled']}/{max_pages}] {url[:70]}...")
            
            new_links = self.crawl_page(url)
            
            # Prioritize important links
            priority_keywords = [
                'program', 'faculty', 'fakulte', 'fee', 'ucret', 'admission',
                'basvuru', 'department', 'bolum', 'master', 'phd', 'lisans'
            ]
            
            priority_links = [l for l in new_links if any(kw in l.lower() for kw in priority_keywords)]
            normal_links = [l for l in new_links if l not in priority_links]
            
            for link in priority_links:
                if link not in self.visited and link not in self.queue:
                    self.queue.append(link)
            
            for link in normal_links[:30]:
                if link not in self.visited and link not in self.queue:
                    self.queue.append(link)
            
            time.sleep(0.5)
            
            # Progress update
            if self.stats['pages_crawled'] % 25 == 0:
                self.print_progress(elapsed)
        
        elapsed = time.time() - start_time
        self.print_final_stats(elapsed)
        self.session.close()
    
    def print_progress(self, elapsed: float):
        """Print progress update"""
        print(f"\n{'=' * 80}")
        print("PROGRESS UPDATE")
        print(f"{'=' * 80}")
        print(f"Pages crawled: {self.stats['pages_crawled']}")
        print(f"Pages saved: {self.stats['pages_saved']}")
        print(f"Duplicates skipped: {self.stats['duplicates_skipped']}")
        print(f"Queue size: {len(self.queue)}")
        print(f"Time elapsed: {elapsed / 60:.1f} minutes")
        print(f"\nCategories:")
        for cat, count in sorted(self.stats['categories'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
        print(f"{'=' * 80}\n")
    
    def print_final_stats(self, elapsed: float):
        """Print final statistics"""
        print(f"\n{'=' * 80}")
        print("CRAWLING COMPLETE")
        print(f"{'=' * 80}")
        print(f"Pages crawled: {self.stats['pages_crawled']}")
        print(f"Pages saved: {self.stats['pages_saved']}")
        print(f"Duplicates skipped: {self.stats['duplicates_skipped']}")
        print(f"Total time: {elapsed / 60:.1f} minutes")
        print(f"\nContent Categories:")
        for cat, count in sorted(self.stats['categories'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
        print(f"{'=' * 80}\n")
    
    def export_json(self, filename: str = 'output/izu_advanced_data.json'):
        """Export data to JSON"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        data = [page.to_dict() for page in self.pages_data]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ JSON saved: {filename} ({size_mb:.2f} MB)")
    
    def export_jsonl(self, filename: str = 'output/izu_advanced_data.jsonl'):
        """Export data to JSONL (one JSON object per line)"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            for page in self.pages_data:
                json.dump(page.to_dict(), f, ensure_ascii=False)
                f.write('\n')
        
        size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ JSONL saved: {filename} ({size_mb:.2f} MB)")
    
    def export_csv(self, filename: str = 'output/izu_advanced_data.csv'):
        """Export basic data to CSV"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Title', 'Category', 'Language', 'Word Count', 'Has Structured Data'])
            
            for page in self.pages_data:
                writer.writerow([
                    page.url,
                    page.title,
                    page.category,
                    page.language,
                    page.word_count,
                    'Yes' if page.structured_data else 'No'
                ])
        
        size_kb = os.path.getsize(filename) / 1024
        print(f"✓ CSV saved: {filename} ({size_kb:.1f} KB)")
    
    def save_all(self, base_filename: str = 'izu_advanced'):
        """Save data in all formats"""
        if not self.pages_data:
            print("⚠ No data to save!")
            return
        
        print(f"\n{'=' * 80}")
        print("EXPORTING DATA")
        print(f"{'=' * 80}")
        
        self.export_json(f'output/{base_filename}_data.json')
        self.export_jsonl(f'output/{base_filename}_data.jsonl')
        self.export_csv(f'output/{base_filename}_data.csv')
        
        total_words = sum(page.word_count for page in self.pages_data)
        structured_count = sum(1 for page in self.pages_data if page.structured_data)
        
        print(f"\n{'=' * 80}")
        print("EXPORT STATISTICS")
        print(f"{'=' * 80}")
        print(f"Total pages exported: {len(self.pages_data)}")
        print(f"Total words: {total_words:,}")
        print(f"Pages with structured data: {structured_count}")
        print(f"Average words per page: {total_words / len(self.pages_data):.0f}")
        print(f"{'=' * 80}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced IZU Web Crawler')
    parser.add_argument('--max-pages', type=int, default=500, help='Maximum pages to crawl')
    parser.add_argument('--max-time', type=int, default=40, help='Maximum time in minutes')
    parser.add_argument('--test-mode', action='store_true', help='Test mode (10 pages)')
    
    args = parser.parse_args()
    
    max_pages = 10 if args.test_mode else args.max_pages
    max_time = 5 if args.test_mode else args.max_time
    
    print("\n" + "=" * 80)
    print("REQUIREMENTS CHECK")
    print("=" * 80)
    
    try:
        from requests_html import HTMLSession
        from bs4 import BeautifulSoup
        print("✓ All required packages installed")
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("\nPlease install: pip install requests-html beautifulsoup4 lxml")
        exit(1)
    
    print("\nStarting advanced crawler...\n")
    
    crawler = AdvancedIZUCrawler()
    crawler.crawl(max_pages=max_pages, max_time_minutes=max_time)
    crawler.save_all('izu_advanced')
    
    print("\n✓ Done! Check output/ directory for results")
