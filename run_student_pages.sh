#!/bin/bash
echo "======================================"
echo "Student Pages Scraper"
echo "Target: All student-related pages"
echo "Output: 2 CSV files (TR + EN)"
echo "======================================"
echo ""

source venv/bin/activate

START=$(date +%s)
scrapy crawl student_pages_spider

END=$(date +%s)
DURATION=$((END - START))

echo ""
echo "======================================"
echo "Complete! Duration: $((DURATION/60))m $((DURATION%60))s"
echo "======================================"
echo ""
echo "Output files:"
ls -lh output/all_student_pages_*.csv
echo ""
echo "Row counts:"
wc -l output/all_student_pages_*.csv
