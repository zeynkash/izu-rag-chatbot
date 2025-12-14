import re

with open('izu_scraper/spiders/izu_spider.py', 'r') as f:
    content = f.read()

# New extract_content method that excludes style and script
new_method = '''    def extract_content(self, response):
        """Extract main content, excluding scripts and styles"""
        content_selectors = [
            'article.main-content',
            'div.content',
            'div#content',
            'main',
            'div.page-content',
            'div.icerik',
            'article',
            'div.container',
        ]
        
        content = ""
        for selector in content_selectors:
            # Use XPath to exclude script and style tags
            elements = response.css(selector).xpath('.//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::noscript)]').getall()
            if elements:
                content = ' '.join(elements)
                break
        
        if not content:
            # Fallback: get body text but exclude script/style/noscript
            elements = response.xpath('//body//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::noscript)]').getall()
            content = ' '.join(elements)
        
        # Clean content
        content = re.sub(r'\s+', ' ', content)
        # Remove any remaining CSS/JS artifacts
        content = re.sub(r'[{}]', '', content)
        return content.strip()'''

# Find and replace the method
pattern = r'    def extract_content\(self, response\):.*?return content\.strip\(\)'
content = re.sub(pattern, new_method, content, flags=re.DOTALL)

with open('izu_scraper/spiders/izu_spider.py', 'w') as f:
    f.write(content)

print("✓ Spider updated!")
