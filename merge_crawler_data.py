#!/usr/bin/env python3
"""
Merge Old and New Crawler Data
Combines data from basic crawler and advanced crawler, removing duplicates
"""

import json
import os
from typing import List, Dict, Any, Set
from datetime import datetime
from crawler_utils import calculate_content_hash, similarity_ratio


def load_old_data(filepath: str) -> List[Dict[str, Any]]:
    """Load data from old crawler format"""
    print(f"Loading old data from: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ⚠ File not found: {filepath}")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    print(f"  ✓ Loaded {len(old_data)} pages from old crawler")
    return old_data


def load_new_data(filepath: str) -> List[Dict[str, Any]]:
    """Load data from advanced crawler format"""
    print(f"Loading new data from: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ⚠ File not found: {filepath}")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    print(f"  ✓ Loaded {len(new_data)} pages from new crawler")
    return new_data


def convert_old_to_new_format(old_page: Dict[str, Any]) -> Dict[str, Any]:
    """Convert old crawler format to new advanced crawler format"""
    
    # Calculate content hash if not present
    content = old_page.get('content', '')
    content_hash = calculate_content_hash(content)
    
    # Detect language (simple heuristic)
    language = 'unknown'
    if 'language' in old_page:
        language = old_page['language']
    elif '/en/' in old_page.get('url', ''):
        language = 'english'
    elif '/tr/' in old_page.get('url', ''):
        language = 'turkish'
    
    # Convert to new format
    new_page = {
        'url': old_page.get('url', ''),
        'title': old_page.get('title', ''),
        'category': 'general',  # Old crawler didn't categorize
        'content': content,
        'language': language,
        'word_count': old_page.get('word_count', len(content.split())),
        'tables': old_page.get('tables', []),
        'lists': old_page.get('lists', []),
        'images': [],  # Convert if needed
        'documents': [],
        'contact_info': {},
        'breadcrumb': [],
        'meta_description': None,
        'date_scraped': old_page.get('date_scraped', datetime.now().isoformat()),
        'content_hash': content_hash,
        'structured_data': None
    }
    
    return new_page


def merge_data(old_data: List[Dict], new_data: List[Dict]) -> List[Dict]:
    """
    Merge old and new data, removing duplicates
    
    Deduplication strategy:
    1. First check by URL (exact match)
    2. Then check by content hash
    3. Keep the newer/more complete version
    """
    print("\nMerging data and removing duplicates...")
    
    # Track seen URLs and content hashes
    seen_urls: Set[str] = set()
    seen_hashes: Set[str] = set()
    merged_data: List[Dict] = []
    
    stats = {
        'new_kept': 0,
        'old_kept': 0,
        'duplicates_skipped': 0,
        'url_duplicates': 0,
        'content_duplicates': 0
    }
    
    # First, add all new data (prioritize new crawler data)
    print("  Processing new crawler data...")
    for page in new_data:
        url = page.get('url', '')
        content_hash = page.get('content_hash', '')
        
        if not url:
            continue
        
        seen_urls.add(url)
        if content_hash:
            seen_hashes.add(content_hash)
        
        merged_data.append(page)
        stats['new_kept'] += 1
    
    # Then add old data that doesn't duplicate
    print("  Processing old crawler data...")
    for old_page in old_data:
        url = old_page.get('url', '')
        
        if not url:
            continue
        
        # Check URL duplicate
        if url in seen_urls:
            stats['duplicates_skipped'] += 1
            stats['url_duplicates'] += 1
            continue
        
        # Convert to new format
        converted_page = convert_old_to_new_format(old_page)
        content_hash = converted_page.get('content_hash', '')
        
        # Check content hash duplicate
        if content_hash and content_hash in seen_hashes:
            stats['duplicates_skipped'] += 1
            stats['content_duplicates'] += 1
            continue
        
        # Add unique page
        seen_urls.add(url)
        if content_hash:
            seen_hashes.add(content_hash)
        
        merged_data.append(converted_page)
        stats['old_kept'] += 1
    
    print(f"\n  ✓ Merge complete!")
    print(f"    - Kept from new crawler: {stats['new_kept']}")
    print(f"    - Kept from old crawler: {stats['old_kept']}")
    print(f"    - Duplicates skipped: {stats['duplicates_skipped']}")
    print(f"      (URL duplicates: {stats['url_duplicates']}, "
          f"Content duplicates: {stats['content_duplicates']})")
    print(f"    - Total merged pages: {len(merged_data)}")
    
    return merged_data


def save_merged_data(data: List[Dict], output_dir: str = 'output'):
    """Save merged data in multiple formats"""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nSaving merged data...")
    
    # JSON
    json_file = os.path.join(output_dir, 'izu_merged_data.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size_mb = os.path.getsize(json_file) / (1024 * 1024)
    print(f"  ✓ JSON: {json_file} ({size_mb:.2f} MB)")
    
    # JSONL
    jsonl_file = os.path.join(output_dir, 'izu_merged_data.jsonl')
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for page in data:
            json.dump(page, f, ensure_ascii=False)
            f.write('\n')
    size_mb = os.path.getsize(jsonl_file) / (1024 * 1024)
    print(f"  ✓ JSONL: {jsonl_file} ({size_mb:.2f} MB)")
    
    # Statistics
    total_words = sum(page.get('word_count', 0) for page in data)
    categories = {}
    for page in data:
        cat = page.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n  Statistics:")
    print(f"    - Total pages: {len(data)}")
    print(f"    - Total words: {total_words:,}")
    print(f"    - Average words/page: {total_words / len(data):.0f}")
    print(f"\n  Categories:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {cat}: {count}")


def main():
    """Main merge function"""
    print("=" * 80)
    print("MERGE OLD AND NEW CRAWLER DATA")
    print("=" * 80)
    print()
    
    # File paths
    old_file = '/home/zeynkash/projects/izu_scraper/chunking/full_izu_clean_data.json'
    new_file = '/home/zeynkash/projects/izu_scraper/output/izu_advanced_data.json'
    output_dir = '/home/zeynkash/projects/izu_scraper/output'
    
    # Load data
    old_data = load_old_data(old_file)
    new_data = load_new_data(new_file)
    
    if not old_data and not new_data:
        print("\n⚠ No data to merge!")
        return
    
    # Merge
    merged_data = merge_data(old_data, new_data)
    
    # Save
    save_merged_data(merged_data, output_dir)
    
    print("\n" + "=" * 80)
    print("MERGE COMPLETE!")
    print("=" * 80)
    print(f"\nMerged files saved in: {output_dir}/")
    print("  - izu_merged_data.json")
    print("  - izu_merged_data.jsonl (recommended for RAG)")
    print("\nYou can now use the merged data for your chatbot!")
    print("=" * 80)


if __name__ == "__main__":
    main()
