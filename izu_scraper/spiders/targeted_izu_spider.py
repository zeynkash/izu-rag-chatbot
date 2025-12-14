import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from datetime import datetime
from urllib.parse import urlparse
import re
from izu_scraper.items import IzuScraperItem


class TargetedIzuSpider(CrawlSpider):
    name = "targeted_izu_spider"
    allowed_domains = ["izu.edu.tr"]
    
    # Specific start URLs for missing sections
    start_urls = [
        # About section - English
        "https://www.izu.edu.tr/en/about-izu/history/history-and-foundation",
        "https://www.izu.edu.tr/en/about-izu/history/about-izu",
        "https://www.izu.edu.tr/en/about-izu",
        
        # About section - Turkish
        "https://www.izu.edu.tr/kurumsal/tarihce",
        "https://www.izu.edu.tr/hakkimizda",
        
        # Admissions - English & Turkish
        "https://www.izu.edu.tr/en/admissions",
        "https://www.izu.edu.tr/ogrenci/kayit-kabul",
        "https://www.izu.edu.tr/basvuru",
        
        # Career - English & Turkish
        "https://www.izu.edu.tr/en/career",
        "https://www.izu.edu.tr/kariyer",
        "https://www.izu.edu.tr/mezun",
        
        # Departments - English & Turkish
        "https://www.izu.edu.tr/en/academics/departments",
        "https://www.izu.edu.tr/akademik/bolumler",
        
        # Student Services - English & Turkish
        "https://www.izu.edu.tr/en/student-services",
        "https://www.izu.edu.tr/ogrenci",
        "https://www.izu.edu.tr/ogrenci-hizmetleri",
    ]
    
    custom_settings = {
        'DEPTH_LIMIT': 3,
        'CLOSESPIDER_PAGECOUNT': 0,  # No limit
    }
    
    # Link extraction rules - only follow links in these sections
    rules = (
        Rule(
            LinkExtractor(
                allow_domains=['izu.edu.tr'],
                allow=[
                    r'/en/about-izu/',
                    r'/hakkimizda/',
                    r'/kurumsal/',
                    r'/en/admissions/',
                    r'/basvuru/',
                    r'/kayit-kabul/',
                    r'/en/career/',
                    r'/kariyer/',
                    r'/mezun/',
                    r'/en/academics/departments/',
                    r'/akademik/bolumler/',
                    r'/bolum/',
                    r'/department/',
                    r'/en/student-services/',
                    r'/ogrenci/',
                    r'/ogrenci-hizmetleri/',
                ],
                deny=[
                    r'login', r'signin', r'giris',
                    r'logout', r'signout', r'cikis',
                    r'mailto:', r'tel:',
                    r'javascript:',
                    r'/print/', r'/yazdir/',
                    r'\.(jpg|jpeg|png|gif|pdf|doc|docx|xls|xlsx|zip|rar)$',
                ],
                unique=True,
            ),
            callback='parse_page',
            follow=True
        ),
    )
    
    def __init__(self, *args, **kwargs):
        super(TargetedIzuSpider, self).__init__(*args, **kwargs)
        self.failed_urls = []
    
    def parse_page(self, response):
        """Parse individual pages"""
        
        if 'text/html' not in response.headers.get('Content-Type', b'').decode():
            return
        
        self.logger.info(f'Parsing: {response.url}')
        
        item = IzuScraperItem()
        
        item['url'] = response.url
        item['date_scraped'] = datetime.now().isoformat()
        item['response_status'] = response.status
        
        item['title'] = self.extract_title(response)
        item['content'] = self.extract_content(response)
        item['meta_description'] = self.extract_meta_description(response)
        item['breadcrumb'] = self.extract_breadcrumb(response)
        item['images'] = self.extract_images(response)
        item['documents'] = self.extract_documents(response)
        item['contact_info'] = self.extract_contact_info(response)
        item['last_updated'] = self.extract_date(response)
        item['content_length'] = len(item['content']) if item['content'] else 0
        item['subsection'] = self.extract_subsection(response)
        
        yield item
    
    def extract_title(self, response):
        """Extract page title"""
        title = (
            response.css('h1::text').get() or
            response.css('title::text').get() or
            response.css('meta[property="og:title"]::attr(content)').get() or
            response.css('div.page-title::text').get() or
            response.css('div.baslik::text').get() or
            ""
        )
        return title.strip() if title else ""
    
    def extract_content(self, response):
        """Extract main content, excluding scripts and styles"""
        content_selectors = [
            'article.main-content',
            'div.content',
            'div#content',
            'main',
            'div.page-content',
            'div.icerik',
            'article',
        ]
        
        content = ""
        for selector in content_selectors:
            elements = response.css(selector).xpath('.//text()[not(ancestor::script) and not(ancestor::style)]').getall()
            if elements:
                content = ' '.join(elements)
                break
        
        if not content:
            elements = response.xpath('//body//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::head)]').getall()
            content = ' '.join(elements)
        
        # Remove CSS patterns
        content = re.sub(r'\{[^}]*\}', ' ', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def extract_meta_description(self, response):
        """Extract meta description"""
        return (
            response.css('meta[name="description"]::attr(content)').get() or
            response.css('meta[property="og:description"]::attr(content)').get() or
            ""
        )
    
    def extract_breadcrumb(self, response):
        """Extract breadcrumb navigation"""
        breadcrumbs = response.css(
            'nav.breadcrumb *::text, '
            'div.breadcrumb *::text, '
            'ol.breadcrumb *::text, '
            'ul.breadcrumb *::text'
        ).getall()
        
        if breadcrumbs:
            return ' > '.join([b.strip() for b in breadcrumbs if b.strip()])
        return ""
    
    def extract_images(self, response):
        """Extract image URLs and alt text"""
        images = []
        for img in response.css('img'):
            img_url = img.css('::attr(src)').get()
            alt_text = img.css('::attr(alt)').get() or ""
            
            if img_url:
                img_url = response.urljoin(img_url)
                images.append(f"{img_url}|{alt_text}")
        
        return '; '.join(images) if images else ""
    
    def extract_documents(self, response):
        """Extract links to PDF and document files"""
        documents = []
        doc_links = response.css('a[href*=".pdf"], a[href*=".doc"], a[href*=".docx"], '
                                 'a[href*=".xls"], a[href*=".xlsx"], a[href*=".ppt"], '
                                 'a[href*=".pptx"]')
        
        for link in doc_links:
            doc_url = link.css('::attr(href)').get()
            doc_text = link.css('::text').get() or ""
            
            if doc_url:
                doc_url = response.urljoin(doc_url)
                documents.append(f"{doc_url}|{doc_text.strip()}")
        
        return '; '.join(documents) if documents else ""
    
    def extract_contact_info(self, response):
        """Extract contact information (emails, phones)"""
        contact = []
        
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 
                           response.text)
        if emails:
            contact.extend([f"email:{e}" for e in set(emails)])
        
        phones = re.findall(r'\+?\d{1,3}[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}', 
                           response.text)
        if phones:
            contact.extend([f"phone:{p}" for p in set(phones)])
        
        return '; '.join(contact) if contact else ""
    
    def extract_date(self, response):
        """Extract last updated date if available"""
        date_selectors = [
            'meta[name="date"]::attr(content)',
            'time::attr(datetime)',
            'span.date::text',
            'div.tarih::text',
        ]
        
        for selector in date_selectors:
            date = response.css(selector).get()
            if date:
                return date.strip()
        
        return ""
    
    def extract_subsection(self, response):
        """Extract subsection from URL path"""
        path = urlparse(response.url).path
        parts = [p for p in path.split('/') if p and p != 'en']
        
        if len(parts) > 1:
            return parts[1]
        return ""
    
    def closed(self, reason):
        """Called when spider closes"""
        self.logger.info(f'Spider closed: {reason}')
        
        if self.failed_urls:
            failed_file = self.settings.get('FAILED_URLS_FILE', 'logs/failed_urls_targeted.txt')
            with open(failed_file, 'w') as f:
                for url in self.failed_urls:
                    f.write(f"{url}\n")
            self.logger.info(f'Saved {len(self.failed_urls)} failed URLs to {failed_file}')
