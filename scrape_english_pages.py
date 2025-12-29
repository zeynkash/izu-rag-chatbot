#!/usr/bin/env python3
"""
Targeted IZU English Page Scraper
Scrapes specific English pages and their important child URLs
Removes headers, footers, and sidebars for clean content
"""

import json
import time
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import hashlib


class TargetedIZUScraper:
    def __init__(self):
        self.session = HTMLSession()
        self.visited_urls: Set[str] = set()
        self.data: List[Dict] = []
        
        # Target starting URLs
        self.seed_urls = [
            "https://www.izu.edu.tr/en/international/admissions/application-requirements",
            "https://www.izu.edu.tr/en/academics/institute/graduate-education-institute/programs",
            "https://www.izu.edu.tr/en/academics/faculties"
        ]
        
        # Allowed path prefixes for child pages
        self.allowed_prefixes = [
            "/en/international/admissions/",
            "/en/academics/institute/",
            "/en/academics/faculties/"
        ]
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL should be crawled"""
        if not url.startswith("https://www.izu.edu.tr"):
            return False
        
        parsed = urlparse(url)
        path = parsed.path
        
        # Check if path matches allowed prefixes
        return any(path.startswith(prefix) for prefix in self.allowed_prefixes)
    
    def clean_content(self, soup: BeautifulSoup) -> str:
        """Remove headers, footers, sidebars, and extract main content"""
        
        # Remove unwanted elements
        unwanted_selectors = [
            'header', 'footer', 'nav',
            '.header', '.footer', '.sidebar', '.menu',
            '#header', '#footer', '#sidebar', '#menu',
            '.breadcrumb', '.social-media', '.share',
            'script', 'style', 'iframe', 'noscript',
            '.advertisement', '.ads', '.cookie-notice'
        ]
        
        for selector in unwanted_selectors:
            for elem in soup.select(selector):
                elem.decompose()
        
        # Try to find main content area
        main_content = None
        
        # Common main content selectors
        main_selectors = [
            'main',
            'article',
            '.main-content',
            '.content',
            '#content',
            '.page-content',
            '[role="main"]'
        ]
        
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return ""
        
        # Extract text
        text = main_content.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        return text
    
    def extract_child_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract child page links"""
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(current_url, href)
            
            # Remove fragments and query params for deduplication
            parsed = urlparse(full_url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            if self.is_valid_url(clean_url) and clean_url not in self.visited_urls:
                links.append(clean_url)
        
        return list(set(links))
    
    def scrape_page(self, url: str) -> Dict:
        """Scrape a single page"""
        print(f"\n📄 Scraping: {url}")
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract title
            title = soup.find('title')
            title = title.get_text(strip=True) if title else ""
            
            # Also try h1
            if not title:
                h1 = soup.find('h1')
                title = h1.get_text(strip=True) if h1 else "Untitled"
            
            # Clean content
            content = self.clean_content(soup)
            
            # Extract child links
            child_links = self.extract_child_links(soup, url)
            
            # Create content hash for deduplication
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            page_data = {
                "url": url,
                "title": title,
                "content": content,
                "content_hash": content_hash,
                "word_count": len(content.split()),
                "char_count": len(content),
                "child_links_found": len(child_links),
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print(f"✓ Title: {title[:60]}...")
            print(f"✓ Content: {len(content)} chars, {len(content.split())} words")
            print(f"✓ Child links: {len(child_links)}")
            
            return page_data, child_links
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None, []
    
    def scrape_all(self, max_pages: int = 50, delay: float = 1.0):
        """Scrape seed URLs and their children"""
        print("="*80)
        print("IZU ENGLISH PAGE SCRAPER - TARGETED CRAWL")
        print("="*80)
        
        to_visit = self.seed_urls.copy()
        pages_scraped = 0
        
        while to_visit and pages_scraped < max_pages:
            url = to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            page_data, child_links = self.scrape_page(url)
            
            if page_data:
                self.data.append(page_data)
                pages_scraped += 1
                
                # Add new child links to queue
                for link in child_links:
                    if link not in self.visited_urls and link not in to_visit:
                        to_visit.append(link)
                        print(f"  → Added to queue: {link}")
            
            # Polite delay
            time.sleep(delay)
        
        print("\n" + "="*80)
        print("SCRAPING COMPLETE")
        print("="*80)
        print(f"✓ Pages scraped: {pages_scraped}")
        print(f"✓ Total data collected: {len(self.data)} pages")
    
    def save_results(self, output_file: str = "izu_english_pages.json"):
        """Save results to JSON"""
        print(f"\n💾 Saving to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Saved {len(self.data)} pages")
        
        # Also save summary
        summary_file = output_file.replace('.json', '_summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("IZU ENGLISH PAGES SCRAPING SUMMARY\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total pages: {len(self.data)}\n\n")
            
            for i, page in enumerate(self.data, 1):
                f.write(f"{i}. {page['title']}\n")
                f.write(f"   URL: {page['url']}\n")
                f.write(f"   Words: {page['word_count']}, Chars: {page['char_count']}\n\n")
        
        print(f"✓ Summary saved to {summary_file}")
    
    def get_statistics(self) -> Dict:
        """Get scraping statistics"""
        if not self.data:
            return {}
        
        return {
            "total_pages": len(self.data),
            "total_words": sum(p['word_count'] for p in self.data),
            "total_chars": sum(p['char_count'] for p in self.data),
            "avg_words_per_page": sum(p['word_count'] for p in self.data) / len(self.data),
            "urls_scraped": [p['url'] for p in self.data]
        }


def main():
    scraper = TargetedIZUScraper()
    
    # Scrape pages (max 50 pages, 1 second delay)
    scraper.scrape_all(max_pages=50, delay=1.0)
    
    # Save results
    scraper.save_results("output/izu_english_pages.json")
    
    # Print statistics
    stats = scraper.get_statistics()
    print("\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    print(f"Total pages: {stats.get('total_pages', 0)}")
    print(f"Total words: {stats.get('total_words', 0):,}")
    print(f"Total characters: {stats.get('total_chars', 0):,}")
    print(f"Average words per page: {stats.get('avg_words_per_page', 0):.0f}")
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
