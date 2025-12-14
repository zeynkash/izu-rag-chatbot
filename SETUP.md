## 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/izu-rag-chatbot.git
cd izu-rag-chatbot
```
## 2. Create Virtual Environment
```bash
python3 -m venv rag-venv
source rag-venv/bin/activate  # On Windows: rag-venv\Scripts\activate
```

## 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 4. Setup OpenAI API Key

Create `.env` file in `chunking/` folder:
```bash
cd chunking
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

⚠️ **Get your API key from**: https://platform.openai.com/api-keys

## 5. Prepare Data

Since large files are not included, you need to either:

**Option A**: Run the scraper to collect fresh data
```bash
cd ..
./run_spider.sh
```

**Option B**: Download pre-processed data (if available)
- Contact repository owner for `chunks.json`
- Place in `chunking/` folder

## 6. Generate Embeddings
```bash
cd chunking
jupyter notebook rag_system.ipynb
```

Run cells 1-4 to generate embeddings and FAISS index.

## 7. Test the System
```bash
python chat.py
```

## Done! 🎉
