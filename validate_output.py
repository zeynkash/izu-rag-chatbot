#!/usr/bin/env python3
"""
Validation script for IZU scraper output
Checks data quality, completeness, and consistency
"""

import csv
from pathlib import Path
from collections import defaultdict


def validate_csv_file(filepath):
    """Validate a single CSV file"""
    stats = {
        'total_rows': 0,
        'empty_content': 0,
        'short_content': 0,
        'missing_title': 0,
        'missing_url': 0,
        'avg_content_length': 0,
        'urls': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            content_lengths = []
            
            for row in reader:
                stats['total_rows'] += 1
                
                # Check URL
                if not row.get('url'):
                    stats['missing_url'] += 1
                else:
                    stats['urls'].append(row['url'])
                
                # Check title
                if not row.get('title'):
                    stats['missing_title'] += 1
                
                # Check content
                content = row.get('content', '')
                if not content:
                    stats['empty_content'] += 1
                elif len(content) < 100:
                    stats['short_content'] += 1
                
                content_lengths.append(len(content))
            
            # Calculate average
            if content_lengths:
                stats['avg_content_length'] = sum(content_lengths) / len(content_lengths)
    
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    return stats


def main():
    """Main validation function"""
    print("=" * 60)
    print("IZU Scraper Output Validation")
    print("=" * 60)
    print()
    
    output_dir = Path('output')
    
    if not output_dir.exists():
        print("ERROR: Output directory not found!")
        return
    
    # Validate Turkish files
    print("TURKISH FILES:")
    print("-" * 60)
    turkish_dir = output_dir / 'turkish'
    turkish_stats = defaultdict(dict)
    
    if turkish_dir.exists():
        for csv_file in sorted(turkish_dir.glob('*.csv')):
            stats = validate_csv_file(csv_file)
            if stats:
                turkish_stats[csv_file.name] = stats
                print(f"\n{csv_file.name}:")
                print(f"  Total rows: {stats['total_rows']}")
                print(f"  Avg content length: {stats['avg_content_length']:.0f} chars")
                print(f"  Missing title: {stats['missing_title']}")
                print(f"  Empty content: {stats['empty_content']}")
                print(f"  Short content (<100 chars): {stats['short_content']}")
    else:
        print("  No Turkish files found!")
    
    print()
    print("=" * 60)
    
    # Validate English files
    print("\nENGLISH FILES:")
    print("-" * 60)
    english_dir = output_dir / 'english'
    english_stats = defaultdict(dict)
    
    if english_dir.exists():
        for csv_file in sorted(english_dir.glob('*.csv')):
            stats = validate_csv_file(csv_file)
            if stats:
                english_stats[csv_file.name] = stats
                print(f"\n{csv_file.name}:")
                print(f"  Total rows: {stats['total_rows']}")
                print(f"  Avg content length: {stats['avg_content_length']:.0f} chars")
                print(f"  Missing title: {stats['missing_title']}")
                print(f"  Empty content: {stats['empty_content']}")
                print(f"  Short content (<100 chars): {stats['short_content']}")
    else:
        print("  No English files found!")
    
    print()
    print("=" * 60)
    
    # Overall statistics
    print("\nOVERALL STATISTICS:")
    print("-" * 60)
    
    total_tr = sum(s['total_rows'] for s in turkish_stats.values())
    total_en = sum(s['total_rows'] for s in english_stats.values())
    
    print(f"Total Turkish pages: {total_tr}")
    print(f"Total English pages: {total_en}")
    print(f"Total pages scraped: {total_tr + total_en}")
    
    print()
    print("Section Distribution (Turkish):")
    for filename, stats in turkish_stats.items():
        section = filename.replace('_tr.csv', '')
        print(f"  {section}: {stats['total_rows']} pages")
    
    print()
    print("Section Distribution (English):")
    for filename, stats in english_stats.items():
        section = filename.replace('_en.csv', '')
        print(f"  {section}: {stats['total_rows']} pages")
    
    print()
    print("=" * 60)
    print("Validation Complete!")
    print("=" * 60)
    print()
    
    # Check for issues
    issues = []
    
    for name, stats in {**turkish_stats, **english_stats}.items():
        if stats['empty_content'] > 0:
            issues.append(f"{name}: {stats['empty_content']} pages with empty content")
        if stats['missing_title'] > 0:
            issues.append(f"{name}: {stats['missing_title']} pages with missing title")
    
    if issues:
        print("⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ No major issues found!")
    
    print()


if __name__ == '__main__':
    main()
