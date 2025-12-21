#!/usr/bin/env python3
"""
Example Usage Script for Advanced IZU Crawler
Demonstrates various ways to use the crawler
"""

from advanced_izu_crawler import AdvancedIZUCrawler
import json


def example_basic_crawl():
    """Basic crawl example"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Crawl")
    print("=" * 80)
    
    crawler = AdvancedIZUCrawler()
    crawler.crawl(max_pages=20, max_time_minutes=5)
    crawler.save_all('example_output')
    
    print(f"\nCrawled {len(crawler.pages_data)} pages")
    print(f"Categories found: {list(crawler.stats['categories'].keys())}")


def example_filter_by_category():
    """Filter and process by category"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Filter by Category")
    print("=" * 80)
    
    crawler = AdvancedIZUCrawler()
    crawler.crawl(max_pages=30, max_time_minutes=5)
    
    # Get academic programs
    programs = [p for p in crawler.pages_data if p.category == 'academic_program']
    print(f"\nFound {len(programs)} academic program pages")
    
    for prog in programs[:5]:
        print(f"  - {prog.title}")
        if prog.structured_data:
            print(f"    Degree: {prog.structured_data.get('degree_type', 'N/A')}")
            print(f"    Language: {prog.structured_data.get('teaching_language', 'N/A')}")
    
    # Get fee information
    fees = [p for p in crawler.pages_data if p.category == 'fee_structure']
    print(f"\nFound {len(fees)} fee-related pages")


def example_structured_data():
    """Extract and use structured data"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Structured Data Extraction")
    print("=" * 80)
    
    crawler = AdvancedIZUCrawler()
    crawler.crawl(max_pages=25, max_time_minutes=5)
    
    # Count pages with structured data
    structured = [p for p in crawler.pages_data if p.structured_data]
    print(f"\nPages with structured data: {len(structured)} / {len(crawler.pages_data)}")
    
    # Show examples
    for page in structured[:3]:
        print(f"\n{page.title} ({page.category})")
        print(f"  Structured fields: {list(page.structured_data.keys())}")


def example_load_and_analyze():
    """Load saved data and analyze"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Load and Analyze Saved Data")
    print("=" * 80)
    
    try:
        # Load JSONL file
        with open('output/izu_advanced_data.jsonl', 'r', encoding='utf-8') as f:
            pages = [json.loads(line) for line in f]
        
        print(f"\nLoaded {len(pages)} pages from file")
        
        # Analyze by category
        categories = {}
        for page in pages:
            cat = page['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nPages by category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
        
        # Analyze by language
        languages = {}
        for page in pages:
            lang = page['language']
            languages[lang] = languages.get(lang, 0) + 1
        
        print("\nPages by language:")
        for lang, count in languages.items():
            print(f"  {lang}: {count}")
            
    except FileNotFoundError:
        print("\nNo saved data found. Run a crawl first!")


def example_custom_processing():
    """Custom processing during crawl"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Custom Processing")
    print("=" * 80)
    
    class CustomCrawler(AdvancedIZUCrawler):
        def __init__(self):
            super().__init__()
            self.program_count = 0
            self.faculty_count = 0
        
        def crawl_page(self, url):
            result = super().crawl_page(url)
            
            # Count specific categories
            if self.pages_data:
                last_page = self.pages_data[-1]
                if last_page.category == 'academic_program':
                    self.program_count += 1
                elif last_page.category == 'faculty_member':
                    self.faculty_count += 1
            
            return result
    
    crawler = CustomCrawler()
    crawler.crawl(max_pages=20, max_time_minutes=5)
    
    print(f"\nCustom stats:")
    print(f"  Program pages: {crawler.program_count}")
    print(f"  Faculty pages: {crawler.faculty_count}")


if __name__ == "__main__":
    import sys
    
    examples = {
        '1': ('Basic Crawl', example_basic_crawl),
        '2': ('Filter by Category', example_filter_by_category),
        '3': ('Structured Data', example_structured_data),
        '4': ('Load and Analyze', example_load_and_analyze),
        '5': ('Custom Processing', example_custom_processing),
    }
    
    if len(sys.argv) > 1 and sys.argv[1] in examples:
        # Run specific example
        _, func = examples[sys.argv[1]]
        func()
    else:
        # Show menu
        print("=" * 80)
        print("ADVANCED IZU CRAWLER - EXAMPLES")
        print("=" * 80)
        print("\nAvailable examples:")
        for key, (name, _) in examples.items():
            print(f"  {key}. {name}")
        print(f"\nUsage: python {sys.argv[0]} [1-5]")
        print("   or: python {sys.argv[0]}  (to run all)")
        
        if input("\nRun all examples? (y/n): ").lower() == 'y':
            for key, (name, func) in examples.items():
                if key != '4':  # Skip load example if no data
                    func()
                    input("\nPress Enter to continue...")
