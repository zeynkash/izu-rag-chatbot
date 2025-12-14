#!/bin/bash

# Test Spider Script for IZU Scraper
# This script runs a limited test crawl

echo "======================================"
echo "IZU Spider Test Run"
echo "======================================"
echo ""

# Activate virtual environment
source venv/bin/activate


# Run spider with limited pages for testing
echo "Starting test crawl (limited to 20 pages)..."
scrapy crawl izu_spider \
    -s CLOSESPIDER_PAGECOUNT=20 \
    -s DEPTH_LIMIT=2 \
    -s LOG_LEVEL=INFO

echo ""
echo "======================================"
echo "Test Complete!"
echo "======================================"
echo ""

# Show statistics
echo "Output Files Created:"
find output -name "*.csv" -type f -exec echo "  - {}" \; -exec wc -l {} \;

echo ""
echo "Log File:"
ls -lh logs/*.log | tail -1

echo ""
echo "To view a sample CSV:"
echo "  head -20 output/turkish/general_tr.csv"
echo ""
echo "To run full crawl:"
echo "  ./run_spider.sh"
