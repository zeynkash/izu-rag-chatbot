#!/bin/bash

# Full Production Spider Run Script
# This will crawl the entire IZU website

echo "======================================"
echo "IZU Spider - Full Production Run"
echo "======================================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Clean previous outputs (optional - comment out to keep)
# echo "Cleaning previous outputs..."
# rm -rf output/turkish/*.csv output/english/*.csv
# echo "Previous outputs cleaned."
# echo ""

# Start time
START_TIME=$(date +%s)
echo "Start Time: $(date)"
echo ""

# Run the spider
echo "Starting full crawl..."
echo "This may take 2-4 hours depending on website size."
echo "Press Ctrl+C to stop at any time."
echo ""

scrapy crawl izu_spider

# End time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
HOURS=$((DURATION / 3600))
MINUTES=$(((DURATION % 3600) / 60))
SECONDS=$((DURATION % 60))

echo ""
echo "======================================"
echo "Crawl Complete!"
echo "======================================"
echo ""
echo "End Time: $(date)"
echo "Duration: ${HOURS}h ${MINUTES}m ${SECONDS}s"
echo ""

# Show statistics
echo "======================================"
echo "Output Statistics"
echo "======================================"
echo ""

echo "Turkish Files:"
for file in output/turkish/*.csv; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        size=$(du -h "$file" | cut -f1)
        echo "  $(basename $file): $lines lines, $size"
    fi
done

echo ""
echo "English Files:"
for file in output/english/*.csv; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        size=$(du -h "$file" | cut -f1)
        echo "  $(basename $file): $lines lines, $size"
    fi
done

echo ""
echo "Total Output Size:"
du -sh output/

echo ""
echo "Latest Log File:"
ls -lht logs/*.log | head -1

echo ""
echo "======================================"
echo "Next Steps"
echo "======================================"
echo ""
echo "1. Review the logs: tail -100 logs/\$(ls -t logs/ | head -1)"
echo "2. Check for failed URLs: cat logs/failed_urls.txt"
echo "3. Inspect CSV files: head output/turkish/academics_tr.csv"
echo "4. Run validation: python validate_output.py"
echo ""
