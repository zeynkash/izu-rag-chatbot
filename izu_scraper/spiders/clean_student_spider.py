import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from datetime import datetime
from urllib.parse import urlparse
import re
from izu_scraper.items import IzuScraperItem


class CleanStudentSpider(CrawlSpider):
    name = "clean_student_spider"
    allowed_domains = ["izu.edu.tr"]
    
    start_urls = [
        "https://www.izu.edu.tr/en/international/international-students/student-guide",
        "https://www.izu.edu.tr/en/news/-in-category/categories/announcements",
        "https://www.izu.edu.tr/en/international/international-student",
        "https://www.izu.edu.tr/izu-hakkinda/kurumsal-bilgiler/idari-birimler/daire-baskanliklari/ogrenci-isleri-daire-baskanligi",
        "https://izu.edu.tr/izu-hakkinda/mevzuat/yonergeler/burs-yonergesi",
        "https://www.izu.edu.tr/ogrenci/kayit-kabul/ucretler-odemeler",
        "https://www.izu.edu.tr/akademik/enstitu/lisansustu-egitim-enstitusu/ucretler-burs/ucretler-ve-odeme",
        "https://www.izu.edu.tr/izu-hakkinda/kurumsal-bilgiler/idari-birimler/daire-baskanliklari/destek-hizmetleri-mudurlugu/hizmetler",
        "https://www.izu.edu.tr/bt/e-hizmetler",
    ]
    
    custom_settings = {
        'DEPTH_LIMIT': 3,
        'CONCURRENT_REQUESTS': 20,
        'DOWNLOAD_DELAY': 0.3,
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'AUTOTHROTTLE_ENABLED': False,
        'HTTPCACHE_ENABLED': True,
        'DOWNLOAD_TIMEOUT': 20,
        
        'ITEM_PIPELINES': {
            'izu_scraper.pipelines.CleaningPipeline': 100,
            'izu_scraper.pipelines.LanguageDetectionPipeline': 200,
            'izu_scraper.pipelines.CleanStudentPipeline': 500,
        },
    }
    
    rules = (
        Rule(
            LinkExtractor(
                allow_domains=['izu.edu.tr'],
                allow=[
                    r'/en/international/', r'/en/news/', r'/ogrenci/', r'/student',
                    r'/ucretler', r'/fees', r'/burs', r'/scholarship',
                    r'/kayit-kabul', r'/e-hizmetler', r'/services',
                    r'/destek-hizmetleri', r'/announcements', r'/duyuru',
                    r'/yonerge', r'/regulation',
                ],
                deny=[r'login', r'logout', r'mailto:', r'/print/', r'\.(pdf|jpg|png|doc|xls)$'],
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
        item['subsection'] = self.extract_sidebar_urls(response)  # NEW: sidebar URLs
        item['section'] = 'student_info'
        
        yield item
    
    def extract_title(self, response):
        title = response.css('h1::text, title::text').get() or ""
        return title.strip()
    
    def extract_clean_content(self, response):
        """Extract ONLY main content - EXCLUDE header, footer, nav, sidebar"""
        
        # Create a copy of response to manipulate
        from scrapy.http import HtmlResponse
        
        # Get the body
        body = response.body
        
        # Parse with lxml to remove unwanted elements
        from lxml import html
        tree = html.fromstring(body)
        
        # Remove unwanted elements
        for element in tree.xpath('//header | //footer | //nav | //script | //style | //noscript'):
            element.getparent().remove(element)
        
        # Remove elements by class/id patterns (header/footer/sidebar)
        remove_patterns = [
            "//*[contains(@class, 'header')]",
            "//*[contains(@class, 'footer')]",
            "//*[contains(@class, 'navigation')]",
            "//*[contains(@class, 'nav')]",
            "//*[contains(@class, 'menu')]",
            "//*[contains(@class, 'sidebar')]",
            "//*[contains(@class, 'side-menu')]",
            "//*[contains(@id, 'header')]",
            "//*[contains(@id, 'footer')]",
            "//*[contains(@id, 'nav')]",
            "//*[contains(@id, 'sidebar')]",
        ]
        
        for pattern in remove_patterns:
            for element in tree.xpath(pattern):
                try:
                    element.getparent().remove(element)
                except:
                    pass
        
        # Get main content area only
        main_selectors = [
            '//main//text()',
            '//article//text()',
            "//*[@id='content']//text()",
            "//*[@class='content']//text()",
            "//*[@class='main-content']//text()",
            "//*[@class='page-content']//text()",
        ]
        
        content = ""
        for selector in main_selectors:
            texts = tree.xpath(selector)
            if texts:
                content = ' '.join(text.strip() for text in texts if text.strip())
                break
        
        # Fallback: get body text (already cleaned above)
        if not content:
            content = ' '.join(tree.xpath('//body//text()'))
        
        # Additional cleaning
        content = self.final_content_cleaning(content)
        
        return content
    
    def final_content_cleaning(self, text):
        """Final cleanup to remove any remaining navigation/repeated text"""
        if not text:
            return ""
        
        # Remove CSS/JS artifacts
        text = re.sub(r'\{[^}]*\}', ' ', text)
        
        # Remove specific repeated sidebar phrases
        sidebar_terms = [
            'BİLGİ TEKNOLOJİLERİ DAİRE BAŞKANLIĞI',
            'INFORMATION TECHNOLOGIES DEPARTMENT',
            'Organizasyon Şeması', 'Organization Chart',
            'İdari Birimler', 'Administrative Units',
            'E-Hizmetler', 'E-Services',
            'Kampüs Bilgi Sistemi', 'Campus Information System',
            'İZÜ Webmail', 'IZU Webmail',
            'Elektronik Belge Yönetim', 'Electronic Document Management',
            'Eduroam',
        ]
        
        for term in sidebar_terms:
            text = text.replace(term, ' ')
        
        # Remove repeated words (navigation items)
        words = text.split()
        word_counts = {}
        for word in words:
            if len(word) > 2:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Keep words that don't repeat excessively
        filtered = [w for w in words if word_counts.get(w, 0) <= 8 or len(w) <= 2]
        text = ' '.join(filtered)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_sidebar_urls(self, response):
        """Extract URLs from sidebar as comma-separated list"""
        sidebar_urls = []
        
        # Find sidebar elements
        sidebar_selectors = [
            '//aside//a/@href',
            "//*[contains(@class, 'sidebar')]//a/@href",
            "//*[contains(@class, 'side-menu')]//a/@href",
            "//*[contains(@class, 'left-menu')]//a/@href",
        ]
        
        for selector in sidebar_selectors:
            urls = response.xpath(selector).getall()
            if urls:
                # Make absolute URLs and add titles
                for url in urls:
                    abs_url = response.urljoin(url)
                    # Get link text
                    link_text = response.xpath(f'//a[@href="{url}"]/text()').get()
                    if link_text:
                        link_text = link_text.strip()
                        sidebar_urls.append(f"{link_text}: {abs_url}")
                    else:
                        sidebar_urls.append(abs_url)
                break
        
        return ' | '.join(set(sidebar_urls))  # Remove duplicates
    
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
            doc_text = link.css('::text').get() or "Document"
            if doc_url:
                docs.append(f"{doc_text.strip()}: {response.urljoin(doc_url)}")
        return ' | '.join(docs) if docs else ""
    
    def extract_contact_info(self, response):
        # Only from main content area
        main_text = ' '.join(response.css('main, article, div.content').xpath('.//text()').getall())
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', main_text)
        return '; '.join([f"email:{e}" for e in set(emails)]) if emails else ""
    
    def extract_date(self, response):
        return response.css('time::attr(datetime)').get() or ""
