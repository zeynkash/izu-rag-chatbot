# Advanced IZU Web Crawler - Documentation

## Overview

The Advanced IZU Web Crawler is an intelligent web scraping system designed specifically for extracting comprehensive university data from Istanbul Sabahattin Zaim University's website. Unlike basic crawlers, this system automatically categorizes content, extracts structured data, and outputs in multiple formats optimized for RAG chatbot systems.

## Key Features

- **🎯 Intelligent Content Categorization**: Automatically classifies pages into 10+ categories (Academic Programs, Faculty, Admissions, Fees, Events, News, Research, etc.)
- **📊 Structured Data Extraction**: Extracts structured information using specialized extractors for each content type
- **🌐 Multi-Language Support**: Handles both Turkish and English content with language detection
- **🔄 Smart Deduplication**: Uses content hashing to avoid storing duplicate Turkish/English versions
- **📁 Multiple Export Formats**: JSON, JSONL, and CSV outputs
- **⚡ Async & Efficient**: JavaScript rendering support with polite rate limiting
- **📈 Real-time Progress Tracking**: Category-based statistics and progress updates

## Installation

### Prerequisites

```bash
# Python 3.8 or higher required
python --version
```

### Install Dependencies

```bash
cd /home/zeynkash/projects/izu_scraper
pip install requests-html beautifulsoup4 lxml
```

## Quick Start

### Basic Usage

```bash
# Run with default settings (500 pages, 40 minutes max)
python advanced_izu_crawler.py

# Output will be in the output/ directory:
# - izu_advanced_data.json (full data with structure)
# - izu_advanced_data.jsonl (one JSON per line, great for RAG)
# - izu_advanced_data.csv (basic overview)
```

### Test Mode

```bash
# Quick test with only 10 pages
python advanced_izu_crawler.py --test-mode
```

### Custom Configuration

```bash
# Crawl 200 pages with 20 minute limit
python advanced_izu_crawler.py --max-pages 200 --max-time 20
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--max-pages` | 500 | Maximum number of pages to crawl |
| `--max-time` | 40 | Maximum time in minutes |
| `--test-mode` | False | Quick test mode (10 pages, 5 minutes) |

## Output Formats

### 1. JSON Format (`izu_advanced_data.json`)

Complete data with all fields. Best for analysis and browsing.

```json
[
  {
    "url": "https://www.izu.edu.tr/...",
    "title": "Computer Engineering",
    "category": "academic_program",
    "content": "Full text content...",
    "language": "english",
    "word_count": 450,
    "tables": [[["Header1", "Header2"], ["Data1", "Data2"]]],
    "lists": [["Item 1", "Item 2"]],
    "images": [{"url": "...", "alt": "..."}],
    "documents": [{"url": "...", "title": "..."}],
    "contact_info": {"emails": ["..."], "phones": ["..."]},
    "breadcrumb": ["Home", "Faculties", "Engineering"],
    "meta_description": "...",
    "date_scraped": "2025-12-19T10:58:47",
    "content_hash": "abc123...",
    "structured_data": {
      "program_name": "Computer Engineering",
      "degree_type": "bachelor",
      "duration": "4",
      "teaching_language": "english",
      "tuition_fee": "75000 TRY",
      "admission_requirements": [...]
    }
  }
]
```

### 2. JSONL Format (`izu_advanced_data.jsonl`)

One JSON object per line. **Recommended for RAG systems** and chunking.

```jsonl
{"url": "...", "title": "...", "content": "..."}
{"url": "...", "title": "...", "content": "..."}
```

### 3. CSV Format (`izu_advanced_data.csv`)

Quick overview with basic fields.

```csv
URL,Title,Category,Language,Word Count,Has Structured Data
https://...,Computer Engineering,academic_program,english,450,Yes
```

## Data Models

### Content Categories

The crawler automatically categorizes pages into:

- **academic_program**: Degree programs, majors, departments
- **faculty_member**: Professor profiles, staff pages
- **admission**: Application requirements, deadlines
- **fee_structure**: Tuition fees, costs, scholarships
- **event**: Events, seminars, conferences
- **news**: News articles, announcements
- **research**: Research centers, projects
- **student_service**: Campus services, facilities
- **department**: Department information
- **general**: Other university information

### Structured Data Fields

Each category has specialized fields. For **Academic Programs**:

```python
{
  "program_name": str,
  "program_name_en": str,
  "degree_type": str,  # bachelor, master, phd
  "faculty": str,
  "department": str,
  "duration_years": float,
  "teaching_language": str,
  "tuition_fee": str,
  "description": str,
  "admission_requirements": list,
  "curriculum": list,
  "career_opportunities": list,
  "url": str
}
```

## Integration with RAG Chatbot

### Step 1: Run the Crawler

```bash
python advanced_izu_crawler.py
```

### Step 2: Use JSONL Output

The JSONL format is perfect for chunking systems:

```python
import json

# Load data
with open('output/izu_advanced_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        page = json.loads(line)
        
        # Create chunks from content
        chunk = {
            'content': page['content'],
            'metadata': {
                'title': page['title'],
                'url': page['url'],
                'category': page['category'],
                'language': page['language']
            }
        }
        
        # Add to your RAG system
        # your_rag_system.add_chunk(chunk)
```

### Step 3: Enhanced Queries

Use structured data for better responses:

```python
# Find all programs
programs = [p for p in pages if p['category'] == 'academic_program']

# Find all fees
fees = [p for p in pages if p['category'] == 'fee_structure']
```

## Architecture

```
advanced_izu_crawler.py      # Main crawler
├── izu_data_models.py       # Data structures (PageData, AcademicProgram, etc.)
├── extraction_strategies.py  # Specialized extractors for each category
└── crawler_utils.py         # Helper functions (text cleaning, detection, etc.)
```

### Flow

1. **URL Discovery**: Start from seed URLs, discover links
2. **Categorization**: Classify URL based on keywords
3. **Content Extraction**: Extract text, tables, lists, images
4. **Specialized Extraction**: Apply category-specific extractor
5. **Deduplication**: Check content hash against seen content
6. **Storage**: Save PageData object with structured data
7. **Export**: Output in JSON, JSONL, CSV formats

## Performance

- **Speed**: ~2-5 seconds per page (with JS rendering)
- **Rate**: 0.5 second delay between requests (polite crawling)
- **Typical Run**: 500 pages in 30-40 minutes
- **Output Size**: 50-200 MB depending on content

## Troubleshooting

### Error: Missing packages

```bash
pip install requests-html beautifulsoup4 lxml
```

### Error: JavaScript rendering fails

This is normal. The crawler will fall back to static HTML parsing.

### Warning: Duplicate content

This is expected for Turkish/English versions. The crawler automatically skips duplicates.

### Slow crawling

- Normal: 2-5 seconds per page with JS rendering
- Each page needs time to render JavaScript
- Rate limiting ensures polite crawling

## Advanced Usage

### Programmatic Usage

```python
from advanced_izu_crawler import AdvancedIZUCrawler

# Create crawler
crawler = AdvancedIZUCrawler(base_url="https://www.izu.edu.tr")

# Crawl
crawler.crawl(max_pages=100, max_time_minutes=15)

# Access data
for page in crawler.pages_data:
    print(f"{page.title} - {page.category}")
    if page.structured_data:
        print(f"  Structured: {page.structured_data}")

# Export
crawler.save_all('my_custom_output')
```

### Filter by Category

```python
# Get only academic programs
programs = [p for p in crawler.pages_data if p.category == 'academic_program']

# Get pages with structured data
structured = [p for p in crawler.pages_data if p.structured_data is not None]
```

### Custom Processing

```python
# Process each page during crawling
class MyCustomCrawler(AdvancedIZUCrawler):
    def crawl_page(self, url):
        result = super().crawl_page(url)
        
        # Custom processing
        if self.pages_data:
            last_page = self.pages_data[-1]
            # Do something with the page data
            
        return result
```

## Comparison with Basic Crawler

| Feature | Basic Crawler | Advanced Crawler |
|---------|--------------|------------------|
| Content Extraction | ✓ | ✓ |
| JavaScript Support | ✓ | ✓ |
| **Content Categorization** | ✗ | ✓ |
| **Structured Data** | ✗ | ✓ |
| **Deduplication** | ✗ | ✓ |
| **Language Detection** | ✗ | ✓ |
| **Multi-format Export** | Basic | JSON, JSONL, CSV |
| **Specialized Extractors** | ✗ | ✓ |

## Best Practices

1. **Run during off-peak hours**: Less load on university servers
2. **Use test mode first**: Verify everything works before full crawl
3. **Check output files**: Ensure data quality before integration
4. **Regular updates**: Re-crawl monthly for fresh data
5. **Save backups**: Keep previous crawl results for comparison

## Support

For issues or questions:

1. Check this documentation
2. Review error messages in terminal
3. Test with `--test-mode` flag
4. Check output files are created in `output/` directory

## License

Part of IZU RAG Chatbot Project
