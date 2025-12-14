#!/bin/bash

echo "======================================"
echo "IZU Targeted Spider - Missing Sections"
echo "======================================"
echo ""
echo "Targeting:"
echo "  - About/History pages"
echo "  - Admissions"
echo "  - Career"
echo "  - Departments"
echo "  - Student Services"
echo ""

# Activate virtual environment
source venv/bin/activate

# Start time
START_TIME=$(date +%s)
echo "Start Time: $(date)"
echo ""

# Run the targeted spider
echo "Starting targeted crawl..."
scrapy crawl targeted_izu_spider

# End time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo ""
echo "======================================"
echo "Targeted Crawl Complete!"
echo "======================================"
echo ""
echo "Duration: ${MINUTES}m ${SECONDS}s"
echo ""

# Show new files
echo "New/Updated Files:"
for file in output/turkish/*.csv output/english/*.csv; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        size=$(du -h "$file" | cut -f1)
        echo "  $(basename $file): $lines lines, $size"
    fi
done

echo ""
echo "Check specific sections:"
echo "  - About: cat output/english/about_en.csv | grep -i history"
echo "  - Admissions: wc -l output/*/admissions*.csv"
echo "  - Career: wc -l output/*/career*.csv"
echo "  - Departments: wc -l output/*/departments*.csv"
echo "  - Student Services: wc -l output/*/student_services*.csv"
echo ""
