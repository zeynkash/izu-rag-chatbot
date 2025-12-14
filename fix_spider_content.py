import re

with open('izu_scraper/spiders/izu_spider.py', 'r') as f:
    content = f.read()

new_method = '''    def extract_content(self, response):
        """Extract main content, excluding scripts, styles, and CSS"""
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
            elements = response.css(selector).xpath('.//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::noscript)]').getall()
            if elements:
                content = ' '.join(elements)
                break
        
        if not content:
            elements = response.xpath('//body//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::noscript) and not(ancestor::head)]').getall()
            content = ' '.join(elements)
        
        content = re.sub(r'\\{[^}]*\\}', ' ', content)
        content = re.sub(r'@media[^{{]*\\{{[^}}]*\\}}', ' ', content)
        content = re.sub(r'#[\\w-]+\\s*\\{{[^}}]*\\}}', ' ', content)
        content = re.sub(r'\\.[\\w-]+\\s*\\{{[^}}]*\\}}', ' ', content)
        content = re.sub(r'function\\s*\\([^)]*\\)\\s*\\{{[^}}]*\\}}', ' ', content)
        content = re.sub(r'\\s+', ' ', content)
        
        return content.strip()'''

pattern = r'    def extract_content\(self, response\):.*?return content\.strip\(\)'
if re.search(pattern, content, flags=re.DOTALL):
    content = re.sub(pattern, new_method, content, flags=re.DOTALL)
    
    with open('izu_scraper/spiders/izu_spider.py', 'w') as f:
        f.write(content)
    print("✓ Spider updated successfully!")
else:
    print("✗ Could not find extract_content method")
