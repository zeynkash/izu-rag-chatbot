import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from datetime import datetime
from urllib.parse import urlparse
import re
from izu_scraper.items import IzuScraperItem


class StudentPagesSpider(CrawlSpider):
    name = "student_pages_spider"
    allowed_domains = ["izu.edu.tr"]
    
    start_urls = [
        # International Students
        "https://www.izu.edu.tr/en/international/international-students/student-guide",
        "https://www.izu.edu.tr/en/international/international-student",
        
        # News & Announcements
        "https://www.izu.edu.tr/en/news/-in-category/categories/announcements",
        
        # Student Services
        "https://www.izu.edu.tr/izu-hakkinda/kurumsal-bilgiler/idari-birimler/daire-baskanliklari/ogrenci-isleri-daire-baskanligi",
        "https://www.izu.edu.tr/izu-hakkinda/kurumsal-bilgiler/idari-birimler/daire-baskanliklari/destek-hizmetleri-mudurlugu/hizmetler",
        
        # Fees & Scholarships
        "https://www.izu.edu.tr/ogrenci/kayit-kabul/ucretler-odemeler",
        "https://www.izu.edu.tr/akademik/enstitu/lisansustu-egitim-enstitusu/ucretler-burs/ucretler-ve-odeme",
        "https://izu.edu.tr/izu-hakkinda/mevzuat/yonergeler/burs-yonergesi",
        
        # E-Services
        "https://www.izu.edu.tr/bt/e-hizmetler",
    ]
    
    custom_settings = {
        'DEPTH_LIMIT': 3,
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 0.5,
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'AUTOTHROTTLE_ENABLED': False,
        'HTTPCACHE_ENABLED': True,
        
        # Custom pipelines - separate files for TR/EN
        'ITEM_PIPELINES': {
            'izu_scraper.pipelines.CleaningPipeline': 100,
            'izu_scraper.pipelines.LanguageDetectionPipeline': 200,
            'izu_scraper.pipelines.StudentPagesPipeline': 500,  # New custom pipeline
        },
    }
    
    rules = (
        Rule(
            LinkExtractor(
                allow_domains=['izu.edu.tr'],
                allow=[
                    r'/en/international/',
                    r'/en/news/',
                    r'/ogrenci/',
                    r'/student',
                    r'/ucretler',
                    r'/fees',
                    r'/burs',
                    r'/scholarship',
                    r'/kayit-kabul',
                    r'/admissions',
                    r'/e-hizmetler',
                    r'/services',
                    r'/destek-hizmetleri',
                    r'/idari-birimler',
                    r'/announcements',
                    r'/duyuru',
                ],
                deny=[r'login', r'logout', r'mailto:', r'/print/', r'\.(pdf|jpg|png)$'],
                unique=True,
            ),
            callback='parse_page',
            follow=True
        ),
    )
    
    def parse_page(self, response):
        if 'text/html' not in response.headers.get('Content-Type', b'').decode():
            return
        
        self.logger.info(f'Parsing: {response.url}')
        
        item = IzuScraperItem()
        item['url'] = response.url
        item['date_scraped'] = datetime.now().isoformat()
        item['response_status'] = response.status
        item['title'] = self.extract_title(response)
        item['content'] = self.extract_clean_content(response)
        item['meta_description'] = self.extract_meta_description(response)
        item['breadcrumb'] = self.extract_breadcrumb(response)
        item['images'] = self.extract_images(response)
        item['documents'] = self.extract_documents(response)
        item['contact_info'] = self.extract_contact_info(response)
        item['last_updated'] = self.extract_date(response)
        item['content_length'] = len(item['content']) if item['content'] else 0
        item['subsection'] = self.extract_subsection(response)
        item['section'] = 'student_services'  # All go to student services
        
        yield item
    
    def extract_title(self, response):
        title = response.css('h1::text, title::text').get() or ""
        return title.strip()
    
    def extract_clean_content(self, response):
        """Extract ONLY main content, excluding header/footer/nav"""
        
        # Remove header, footer, nav elements first
        for element in response.xpath('//header | //footer | //nav | //script | //style | //noscript'):
            element.extract()
        
        # Target only main content area
        content_selectors = [
            'main',
            'article',
            'div#content',
            'div.content',
            'div.main-content',
            'div.page-content',
            'section.content',
        ]
        
        content = ""
        for selector in content_selectors:
            elements = response.css(selector).xpath('.//text()').getall()
            if elements:
                content = ' '.join(elements)
                break
        
        # Fallback: Get body but exclude known header/footer containers
        if not content:
            elements = response.xpath('''
                //body//text()[
                    not(ancestor::header) and
                    not(ancestor::footer) and
                    not(ancestor::nav) and
                    not(ancestor::script) and
                    not(ancestor::style) and
                    not(ancestor::*[contains(@class, "header")]) and
                    not(ancestor::*[contains(@class, "footer")]) and
                    not(ancestor::*[contains(@class, "navigation")]) and
                    not(ancestor::*[contains(@class, "menu")]) and
                    not(ancestor::*[contains(@id, "header")]) and
                    not(ancestor::*[contains(@id, "footer")])
                ]
            ''').getall()
            content = ' '.join(elements)
        
        # Clean the content
        content = self.clean_navigation_text(content)
        content = re.sub(r'\{[^}]*\}', ' ', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def clean_navigation_text(self, text):
        """Remove navigation menu patterns"""
        
        # Turkish header menu patterns
        patterns = [
            r'Fakülteler\s+Eğitim\s+Fakültesi.*?(?=(İstanbul|Kampüs|[A-Z][a-zğüşıöç]{5,}))',
            r'Enstitü\s+Lisansüstü.*?Başvuru.*?(?=(İstanbul|Kampüs|[A-Z]))',
            r'Diller\s+Okulu.*?Koordinatörlüğü.*?(?=(İstanbul|[A-Z]))',
            
            # English header menu patterns
            r'Faculties\s+Faculty\s+of\s+Education.*?Application.*?(?=(Istanbul|Campus|[A-Z]{3,}))',
            r'Institute\s+Graduate.*?Application.*?(?=(Istanbul|[A-Z]{3,}))',
            r'School\s+of\s+Languages.*?Coordinator.*?(?=(Istanbul|[A-Z]{3,}))',
            
            # Footer patterns
            r'E-HİZMETLER.*?KURUMSAL.*?BAĞLANTILAR.*?BİZE ULAŞIN.*?HIZLI ERİŞİM',
            r'E-SERVICES.*?CORPORATE.*?LINKS.*?CONTACT\s+US.*?QUICK\s+ACCESS',
            r'Kampüs\s+Bilgi\s+Sistemi.*?İZÜ\s+Webmail.*?(?=(İstanbul|©))',
            r'Campus\s+Information\s+System.*?IZU\s+Webmail.*?(?=(Istanbul|©))',
            
            # Social media footer
            r'Facebook\s+Twitter\s+Instagram\s+LinkedIn',
            
            # Copyright
            r'©\s*İZÜ\s*\d{4}',
            r'İstanbul\s+Sabahattin\s+Zaim\s+Üniversitesi.*?Türkiye',
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove repeated words (navigation items)
        words = text.split()
        word_counts = {}
        for word in words:
            if len(word) > 2:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        filtered = [w for w in words if word_counts.get(w, 0) <= 7 or len(w) <= 2]
        text = ' '.join(filtered)
        
        return text
    
    def extract_meta_description(self, response):
        return response.css('meta[name="description"]::attr(content)').get() or ""
    
    def extract_breadcrumb(self, response):
        breadcrumbs = response.css('nav.breadcrumb *::text, div.breadcrumb *::text').getall()
        return ' > '.join([b.strip() for b in breadcrumbs if b.strip()]) if breadcrumbs else ""
    
    def extract_images(self, response):
        images = []
        for img in response.css('main img, article img, div.content img'):
            img_url = img.css('::attr(src)').get()
            if img_url:
                images.append(response.urljoin(img_url))
        return '; '.join(images) if images else ""
    
    def extract_documents(self, response):
        docs = []
        for link in response.css('a[href*=".pdf"]'):
            doc_url = link.css('::attr(href)').get()
            if doc_url:
                docs.append(response.urljoin(doc_url))
        return '; '.join(docs) if docs else ""
    
    def extract_contact_info(self, response):
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
        return '; '.join([f"email:{e}" for e in set(emails)]) if emails else ""
    
    def extract_date(self, response):
        return response.css('time::attr(datetime)').get() or ""
    
    def extract_subsection(self, response):
        parts = [p for p in urlparse(response.url).path.split('/') if p and p != 'en']
        return parts[1] if len(parts) > 1 else ""
