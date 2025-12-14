from datetime import datetime

BOT_NAME = "izu_scraper"

SPIDER_MODULES = ["izu_scraper.spiders"]
NEWSPIDER_MODULE = "izu_scraper.spiders"

USER_AGENT = "IZU-Chatbot-DataCollector/1.0 (Educational Purpose)"

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 8

DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

COOKIES_ENABLED = False

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 408, 429]

RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

ITEM_PIPELINES = {
    "izu_scraper.pipelines.CleaningPipeline": 100,
    "izu_scraper.pipelines.LanguageDetectionPipeline": 200,
    "izu_scraper.pipelines.CategorizationPipeline": 300,
    "izu_scraper.pipelines.DuplicatesPipeline": 400,
    "izu_scraper.pipelines.CSVExportPipeline": 500,
}

LOG_LEVEL = "INFO"
LOG_FILE = f'logs/izu_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"

STATS_DUMP = True
DOWNLOAD_TIMEOUT = 30
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 3

CSV_OUTPUT_DIR = "output"
FAILED_URLS_FILE = "logs/failed_urls.txt"

SECTION_PATTERNS = {
    'admissions': ['basvuru', 'admission', 'kayit', 'registration', 'ogrenci-isleri'],
    'academics': ['akademik', 'academic', 'egitim', 'education', 'ogretim'],
    'faculties': ['fakulte', 'faculty', 'fakulteler', 'faculties'],
    'departments': ['bolum', 'department', 'bolumler', 'departments'],
    'graduate': ['lisansustu', 'graduate', 'yuksek-lisans', 'master', 'doktora', 'phd'],
    'research': ['arastirma', 'research', 'yayin', 'publication', 'proje', 'project'],
    'student_services': ['ogrenci', 'student', 'hizmet', 'service', 'yurt', 'dormitory'],
    'campus_life': ['kampus', 'campus', 'sosyal', 'social', 'kulup', 'club', 'spor', 'sport'],
    'news_events': ['haber', 'news', 'etkinlik', 'event', 'duyuru', 'announcement'],
    'about': ['hakkimizda', 'about', 'kurumsal', 'institutional', 'tarihce', 'history'],
    'library': ['kutuphane', 'library', 'katalog', 'catalog'],
    'career': ['kariyer', 'career', 'mezun', 'alumni', 'is-ilanlari', 'jobs']
}

EXCLUDE_URL_PATTERNS = [
    'login', 'signin', 'giris',
    'logout', 'signout', 'cikis',
    'mailto:', 'tel:',
    'javascript:',
    '/print/', '/yazdir/',
    '#', '?print=',
    '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx'
]
STUDENT_PAGES_PIPELINE = {
    "izu_scraper.pipelines.CleaningPipeline": 100,
    "izu_scraper.pipelines.LanguageDetectionPipeline": 200,
    "izu_scraper.pipelines_student.StudentPagesPipeline": 500,
}
