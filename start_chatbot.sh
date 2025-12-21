#!/bin/bash
# Quick Start Script for IZU Chatbot

echo "======================================================================"
echo "IZU CHATBOT - QUICK START"
echo "======================================================================"
echo ""

# Activate virtual environment
echo "1. Activating virtual environment..."
source /home/zeynkash/rag-venv/bin/activate

# Start FastAPI server
echo "2. Starting FastAPI server..."
echo ""
echo "Server starting at: http://localhost:8000"
echo "Open chatbot_ui.html in your browser to use the chatbot"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================================================"
echo ""

cd /home/zeynkash/projects/izu_scraper
python chatbot_api.py
