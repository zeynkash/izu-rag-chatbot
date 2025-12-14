import re

with open('izu_scraper/pipelines.py', 'r') as f:
    content = f.read()

new_clean_text = '''    def clean_text(self, text):
        """Clean text by removing CSS, JS, and extra whitespace"""
        if not text:
            return ""
        
        # Remove CSS blocks and patterns
        text = re.sub(r'\\{[^}]*\\}', ' ', text)
        text = re.sub(r'@media[^{]*\\{[^}]*\\}', ' ', text)
        text = re.sub(r'#[\\w-]+\\s*\\{', ' ', text)
        text = re.sub(r'\\.[\\w-]+\\s*\\{', ' ', text)
        text = re.sub(r'position\\s*:\\s*\\w+', ' ', text)
        text = re.sub(r'margin\\s*:\\s*[\\d\\s\\w%]+', ' ', text)
        text = re.sub(r'padding\\s*:\\s*[\\d\\s\\w%]+', ' ', text)
        text = re.sub(r'width\\s*:\\s*[\\d\\s\\w%]+', ' ', text)
        
        # Remove JS patterns
        text = re.sub(r'function\\s*\\([^)]*\\)\\s*\\{', ' ', text)
        text = re.sub(r'var\\s+\\w+\\s*=', ' ', text)
        
        # Remove HTML entities
        text = re.sub(r'&[a-z]+;', ' ', text)
        
        # Remove multiple spaces
        text = re.sub(r'\\s+', ' ', text)
        
        text = text.strip()
        return text'''

pattern = r'    def clean_text\(self, text\):.*?return text'
content = re.sub(pattern, new_clean_text, content, flags=re.DOTALL)

with open('izu_scraper/pipelines.py', 'w') as f:
    f.write(content)

print("✓ Pipeline updated!")
