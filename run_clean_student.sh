#!/bin/bash
echo "======================================"
echo "Clean Student Pages Scraper"
echo "======================================"
echo "Features:"
echo "  ✓ Removes headers, footers, sidebars"
echo "  ✓ Extracts sidebar URLs separately"
echo "  ✓ Clean content only"
echo "  ✓ Fast: 20 concurrent, 0.3s delay"
echo ""
START=$(date +%s)
scrapy crawl clean_student_spider
END=$(date +%s)
DURATION=$((END - START))
echo ""
echo "======================================"
echo "Complete! Duration: $((DURATION/60))m $((DURATION%60))s"
echo "======================================"
echo ""
echo "Output:"
ls -lh output/clean_student_*.csv
wc -l output/clean_student_*.csv
echo ""
echo "Preview English:"
head -2 output/clean_student_english.csv
echo ""
echo "Preview Turkish:"
head -2 output/clean_student_turkish.csv
