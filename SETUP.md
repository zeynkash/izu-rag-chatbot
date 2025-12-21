# Setup Instructions - İZÜ RAG Chatbot

Complete setup guide for the production-ready chatbot system.

## Prerequisites

- Python 3.12+
- Git
- OpenAI API key
- 2GB+ free disk space

---

## Quick Start (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/zeynkash/izu-rag-chatbot.git
cd izu-rag-chatbot
```

### 2. Create Virtual Environment
```bash
python3 -m venv rag-venv
source rag-venv/bin/activate  # Windows: rag-venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# Advanced crawler (if you need to crawl)
pip install -r requirements_advanced.txt

# Chatbot API (recommended)
pip install -r requirements_chatbot.txt
```

### 4. Configure API Key
```bash
# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

⚠️ **Get API key**: https://platform.openai.com/api-keys

### 5. Download/Generate Data

**Option A - Use Existing Data** (Recommended):
Data files should already be in the repository:
- `chunking/chunks.json`
- `chunking/faiss_index.bin`
- `chunking/embeddings_openai_izu.npy`

If missing, contact repository owner or generate (see below).

**Option B - Generate New Data**:
```bash
# Run advanced crawler
python advanced_izu_crawler.py --max-pages 1000

# Process and chunk
python merge_crawler_data.py
python rechunk_with_merged_data.py

# Generate embeddings (in chunking/)
cd chunking
jupyter notebook rag_system.ipynb  # Run cells 1-4
```

### 6. Start Chatbot
```bash
# Quick start
./start_chatbot.sh

# Or manually
python chatbot_api.py
```

Then open `chatbot_ui.html` in your browser!

---

## Full Setup Guide

### Step 1: System Requirements

**Hardware**:
- CPU: 2+ cores
- RAM: 4GB+ (8GB recommended)
- Disk: 2GB free space

**Software**:
- Python 3.12 or higher
- pip package manager
- Git
- (Optional) Jupyter for notebooks

### Step 2: Installation

**Clone & Navigate**:
```bash
git clone https://github.com/zeynkash/izu-rag-chatbot.git
cd izu-rag-chatbot
```

**Virtual Environment**:
```bash
python3 -m venv rag-venv
source rag-venv/bin/activate

# Verify Python version
python --version  # Should be 3.12+
```

**Dependencies**:
```bash
# Install all packages
pip install -r requirements.txt
pip install -r requirements_advanced.txt  
pip install -r requirements_chatbot.txt

# Verify installations
pip list | grep -E "openai|faiss|fastapi"
```

### Step 3: Configuration

**OpenAI API Key**:
```bash
# Create .env in project root
cat > .env << EOF
OPENAI_API_KEY=sk-your-actual-key-here
EOF

# Verify
cat .env  # Should show your key
```

**Permissions**:
```bash
# Make scripts executable
chmod +x start_chatbot.sh advanced_izu_crawler.py
```

### Step 4: Data Preparation

**If Data Exists** (Check first):
```bash
ls -lh chunking/chunks.json
ls -lh chunking/faiss_index.bin
ls -lh chunking/embeddings_openai_izu.npy
```

✅ If all exist, skip to Step 5!

**If Data Missing**:

```bash
# Option 1: Quick test with sample data
cd chunking
python quick_test.py  # Will show if data is valid

# Option 2: Generate from scratch
# 1. Crawl university website
python advanced_izu_crawler.py --max-pages 1000

# 2. Merge with existing data
python merge_crawler_data.py

# 3. Chunk for RAG
python rechunk_with_merged_data.py

# 4. Generate embeddings
cd chunking
jupyter notebook rag_system.ipynb
# Run cells 1-4, wait ~5-10 minutes
```

### Step 5: Testing

**Quick Test** (2 minutes):
```bash
cd chunking
python quick_test.py
```

Expected output:
- ✓ 5/5 tests passed
- ✓ avg ~2-4 seconds response
- ✓ $0.0005 per question

**Full Evaluation** (15 minutes):
```bash
cd chunking
jupyter notebook evaluation.ipynb
# Run all cells
```

Expected output:
- ✓ 0.65+ semantic similarity
- ✓ 96%+ success rate
- ✓ <3s response time

### Step 6: Launch Chatbot

**Method 1 - Quick Start**:
```bash
./start_chatbot.sh
```

**Method 2 - Manual**:
```bash
python chatbot_api.py
# Server starts at http://localhost:8000
# Open chatbot_ui.html in browser
```

**Method 3 - Production**:
```bash
gunicorn chatbot_api:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

### Step 7: Verify

**Check API**:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","chunks_loaded":1154,...}
```

**Test Chat**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hangi fakülteler var?","language":"tr"}'
```

**Web UI**:
- Open `chatbot_ui.html`
- Type: "Burs imkanları var mı?"
- Should get answer in ~3 seconds

---

## Troubleshooting

### "No module named 'openai'"
```bash
pip install openai
```

### "OPENAI_API_KEY not found"
```bash
# Create .env file
echo "OPENAI_API_KEY=your-key" > .env
```

### "chunks.json not found"
```bash
# Generate chunks
python rechunk_with_merged_data.py
```

### "Port 8000 already in use"
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

### Slow responses
- First query is slower (cold start)
- Check internet connection
- Verify OpenAI API status

---

## Optional: Advanced Crawler

To collect fresh data:

```bash
# Basic crawl
python advanced_izu_crawler.py

# Custom options
python advanced_izu_crawler.py \
    --max-pages 2000 \
    --output-dir output/ \
    --categories academic_program news events \
    --export-formats json jsonl csv
```

See `ADVANCED_CRAWLER_README.md` for details.

---

## File Locations

After setup, you should have:

```
✓ .env                                    # Your API key
✓ chunking/chunks.json                    # 1,154 chunks
✓ chunking/faiss_index.bin                # Vector index
✓ chunking/embeddings_openai_izu.npy      # Embeddings
✓ chatbot_api.py                          # API server
✓ chatbot_ui.html                         # Web interface
```

---

## Next Steps

1. ✅ Test chatbot with sample questions
2. 📊 Review evaluation results
3. 🎨 Customize UI (chatbot_ui.html)
4. 🚀 Deploy to production
5. 📈 Monitor usage and costs

---

## Support

- **Issues**: GitHub Issues page
- **Docs**: README.md, ADVANCED_CRAWLER_README.md
- **API Docs**: http://localhost:8000/docs

---

**Setup complete!** 🎉 Your RAG chatbot is ready to use.
