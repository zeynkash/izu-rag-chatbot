import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from datetime import datetime
from urllib.parse import urlparse
import re
from izu_scraper.items import IzuScraperItem


class FastProgramsSpider(CrawlSpider):
    name = "fast_programs_spider"
    allowed_domains = ["izu.edu.tr"]
    
    start_urls = [
        # Graduate Institute
        "https://www.izu.edu.tr/en/academics/institute/graduate-education-institute/home",
        "https://www.izu.edu.tr/en/academics/institute/graduate-education-institute/programs",
        "https://www.izu.edu.tr/akademik/enstitu/lisansustu-egitim-enstitusu",
        "https://www.izu.edu.tr/akademik/enstitu/lisansustu-egitim-enstitusu/programlar",
        
        # All Programs
        "https://www.izu.edu.tr/en/institutional/all-programs",
        "https://www.izu.edu.tr/icerik/tum-programlar",
        
        # Regulations
        "https://www.izu.edu.tr/en/about-izu/instruction-regulations/regulations",
        "https://www.izu.edu.tr/en/about-izu/instruction-regulations/regulations/istanbul-sabahattin-zaim-university-undergraduate-education-and-teaching-regulation",
        
        # Programs pages
        "https://www.izu.edu.tr/en/academics/institute/graduate-education-institute/programs/masters-degree-with-thesis",
        "https://www.izu.edu.tr/en/academics/institute/graduate-education-institute/programs/masters-degree-without-thesis",
        "https://www.izu.edu.tr/en/academics/institute/graduate-education-institute/programs/doctorate",
    ]
    
    custom_settings = {
        'DEPTH_LIMIT': 4,
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'DOWNLOAD_DELAY': 0.5,
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'AUTOTHROTTLE_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 15,
        'HTTPCACHE_ENABLED': True,
    }
    
    rules = (
        Rule(
            LinkExtractor(
                allow_domains=['izu.edu.tr'],
                allow=[
                    r'/en/academics/institute/', r'/akademik/enstitu/',
                    r'/lisansustu', r'/graduate', r'/programs?/', r'/programlar/',
                    r'/yuksek-lisans', r'/master', r'/doktora', r'/doctorate',
                    r'/all-programs', r'/tum-programlar',
                    r'/faculties/', r'/fakulteler/', r'/bolum/', r'/department/',
                    r'/regulations?/', r'/yonetmelik',
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
        title = response.css('h1::text, title::text').get() or ""
        return title.strip()
    
    def extract_content(self, response):
        content_selectors = ['article', 'main', 'div.content', 'div#content']
        content = ""
        for sel in content_selectors:
            elements = response.css(sel).xpath('.//text()[not(ancestor::script) and not(ancestor::style)]').getall()
            if elements:
                content = ' '.join(elements)
                break
        if not content:
            elements = response.xpath('//body//text()[not(ancestor::script) and not(ancestor::style)]').getall()
            content = ' '.join(elements)
        content = re.sub(r'\{[^}]*\}', ' ', content)
        content = re.sub(r'\s+', ' ', content)
        return content.strip()
    
    def extract_meta_description(self, response):
        return response.css('meta[name="description"]::attr(content)').get() or ""
    
    def extract_breadcrumb(self, response):
        breadcrumbs = response.css('nav.breadcrumb *::text, div.breadcrumb *::text').getall()
        return ' > '.join([b.strip() for b in breadcrumbs if b.strip()]) if breadcrumbs else ""
    
    def extract_images(self, response):
        images = [response.urljoin(img.css('::attr(src)').get()) for img in response.css('img') if img.css('::attr(src)').get()]
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
