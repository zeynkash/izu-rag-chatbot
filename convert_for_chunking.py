#!/usr/bin/env python3
"""
Quick Rechunk Script - Use Merged Data for RAG
Updates your chunking system to use the new merged crawler data
"""

import json
import sys
import os

# Add path to access chunking directory
sys.path.insert(0, '/home/zeynkash/projects/izu_scraper/chunking')

def convert_merged_to_chunking_format():
    """Convert merged data to format expected by chunking.ipynb"""
    
    print("=" * 80)
    print("CONVERTING MERGED DATA FOR CHUNKING")
    print("=" * 80)
    print()
    
    # Load merged data
    merged_file = '/home/zeynkash/projects/izu_scraper/output/izu_merged_data.jsonl'
    output_file = '/home/zeynkash/projects/izu_scraper/chunking/all_data_cleaned.jsonl'
    
    print(f"Reading from: {merged_file}")
    
    converted_data = []
    with open(merged_file, 'r', encoding='utf-8') as f:
        for line in f:
            page = json.loads(line)
            
            # Convert to format expected by chunking notebook
            converted = {
                'url': page.get('url', ''),
                'title': page.get('title', ''),
                'language': page.get('language', 'unknown')[:2],  # 'en' or 'tr'
                'content': page.get('content', ''),
                'section': page.get('category', 'general'),  # Use category as section
                'date_scraped': page.get('date_scraped', ''),
            }
            
            # Only include pages with substantial content
            if converted['content'] and len(converted['content']) > 100:
                converted_data.append(converted)
    
    print(f"✓ Loaded {len(converted_data)} pages")
    print(f"Writing to: {output_file}")
    
    # Save in JSONL format
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in converted_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"✓ Saved {len(converted_data)} documents")
    
    # Show statistics
    total_chars = sum(len(d['content']) for d in converted_data)
    languages = {}
    sections = {}
    
    for doc in converted_data:
        lang = doc['language']
        languages[lang] = languages.get(lang, 0) + 1
        
        section = doc['section']
        sections[section] = sections.get(section, 0) + 1
    
    print()
    print("=" * 80)
    print("CONVERSION COMPLETE")
    print("=" * 80)
    print(f"\nStatistics:")
    print(f"  Total documents: {len(converted_data)}")
    print(f"  Total characters: {total_chars:,}")
    print(f"  Average per document: {total_chars / len(converted_data):.0f}")
    print(f"\nLanguages:")
    for lang, count in sorted(languages.items()):
        print(f"  {lang}: {count} ({count/len(converted_data)*100:.1f}%)")
    print(f"\nSections:")
    for section, count in sorted(sections.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {section}: {count}")
    
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("The merged data has been converted and saved to:")
    print(f"  {output_file}")
    print()
    print("Now you can run your chunking notebook:")
    print("  1. cd /home/zeynkash/projects/izu_scraper/chunking")
    print("  2. jupyter notebook chunking.ipynb")
    print("  3. Run all cells to generate new chunks")
    print()
    print("Or use the automated script:")
    print("  python rechunk_with_merged_data.py")
    print()
    print("=" * 80)


if __name__ == "__main__":
    convert_merged_to_chunking_format()
