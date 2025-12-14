#!/bin/bash
echo "======================================"
echo "FAST Programs Scraper"
echo "Target: Graduate, Undergraduate, Regulations"
echo "Speed: 16 concurrent, 0.5s delay"
echo "Max time: ~1 hour"
echo "======================================"
echo ""

source venv/bin/activate

START=$(date +%s)
echo "Start: $(date)"
echo ""

scrapy crawl fast_programs_spider

END=$(date +%s)
DURATION=$((END - START))
MIN=$((DURATION / 60))
SEC=$((DURATION % 60))

echo ""
echo "======================================"
echo "Complete! Duration: ${MIN}m ${SEC}s"
echo "======================================"
echo ""
echo "Check results:"
wc -l output/*/graduate*.csv output/*/academics*.csv output/*/departments*.csv 2>/dev/null
echo ""
