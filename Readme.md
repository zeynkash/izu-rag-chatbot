# IZU University RAG Chatbot

## 📋 Overview
This is a **Retrieval-Augmented Generation (RAG) chatbot** developed for **Istanbul Sabahattin Zaim University (İZÜ)**.  
It answers questions about **university programs, admissions, tuition fees, scholarships, and campus services** in **Turkish and English**, using real university data.

---

## 🗂️ Project Structure

```text
izu_scraper/
├── chunking/
│   ├── all_data_cleaned_.jsonl      # Original cleaned data
│   ├── chunks.json                 # Chunked data (ready for RAG)
│   ├── embeddings_openai.npy       # Vector embeddings
│   ├── faiss_index.bin             # Vector database
│   ├── rag_config.json             # Configuration
│   ├── .env                        # API keys (DO NOT COMMIT!)
│   ├── chunking.ipynb              # Data preparation notebook
│   └── rag_system.ipynb            # RAG system notebook
└── README.md
```

---

## 🚀 Quick Start

### Step 1: Prerequisites

```bash
# Python 3.8+ required
python --version

# Activate virtual environment
source ~/rag-venv/bin/activate
```

---

### Step 2: Install Dependencies

```bash
pip install openai faiss-cpu numpy python-dotenv jupyter
```

---

### Step 3: Setup OpenAI API Key

```bash
cd ~/projects/izu_scraper/chunking
nano .env
```

```env
OPENAI_API_KEY=sk-your-api-key-here
```

---

## 💬 How to Use

### Option 1: Jupyter Notebook (Recommended)

```bash
cd ~/projects/izu_scraper/chunking
jupyter notebook rag_system.ipynb
```
Run the notebook cells in order:

1. Cell 1: Load chunks and setup
2. Cell 8: Test the answer_question() function

### Example usage in notebook:
```python
result = answer_question("Yüksek lisans programları neler?")
print(result["answer"])
```

---

### Option 2: Python Script

Create a file chat.py:
```python
import json
import numpy as np
import faiss
import openai
from dotenv import load_dotenv
import os

# Setup
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load resources
with open('chunks.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)

index = faiss.read_index('faiss_index.bin')

def get_embedding(text):
    response = openai.embeddings.create(
        input=[text.replace("\n", " ")],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def retrieve_chunks(query, top_k=5):
    query_embedding = np.array([get_embedding(query)], dtype='float32')
    faiss.normalize_L2(query_embedding)
    scores, indices = index.search(query_embedding, top_k)
    
    results = []
    for idx, score in zip(indices[0], scores[0]):
        results.append({
            'content': chunks[idx]['content'],
            'metadata': chunks[idx]['metadata'],
            'score': float(score)
        })
    return results

def answer_question(query):
    # Retrieve
    retrieved = retrieve_chunks(query, top_k=3)
    
    # Build context
    context = "\n---\n".join([
        f"Kaynak: {c['metadata']['title']}\n{c['content']}" 
        for c in retrieved
    ])
    
    # Generate
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sen İZÜ için bir asistansın. Sadece verilen bilgileri kullan."},
            {"role": "user", "content": f"Context:\n{context}\n\nSoru: {query}"}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

# Use it
if __name__ == "__main__":
    question = input("Sorunuz: ")
    answer = answer_question(question)
    print(f"\nCevap:\n{answer}")
```

### Run it:
```bash
python chat.py
```

### Option 3: Interactive Chat Script
Create interactive_chat.py:
```python
import json
import numpy as np
import faiss
import openai
from dotenv import load_dotenv
import os

# Setup (same as above)
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

with open('chunks.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)
index = faiss.read_index('faiss_index.bin')

def get_embedding(text):
    response = openai.embeddings.create(
        input=[text.replace("\n", " ")],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def answer_question(query):
    # Retrieve
    query_embedding = np.array([get_embedding(query)], dtype='float32')
    faiss.normalize_L2(query_embedding)
    scores, indices = index.search(query_embedding, 3)
    
    retrieved = [chunks[idx] for idx in indices[0]]
    
    # Context
    context = "\n---\n".join([
        f"[{c['metadata']['title']}]\n{c['content']}" 
        for c in retrieved
    ])
    
    # Generate
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "İZÜ asistanısın. Nazik ve profesyonel ol. Sadece verilen context'i kullan."},
            {"role": "user", "content": f"Context:\n{context}\n\nSoru: {query}"}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

# Interactive loop
print("=" * 70)
print("İZÜ Chatbot - Hoş Geldiniz!")
print("=" * 70)
print("Çıkmak için 'exit' yazın\n")

while True:
    question = input("💬 Siz: ")
    
    if question.lower() in ['exit', 'quit', 'çıkış']:
        print("Görüşmek üzere! 👋")
        break
    
    if not question.strip():
        continue
    
    print("🤖 Asistan: ", end="", flush=True)
    answer = answer_question(question)
    print(answer)
    print()
```
### Run it:
```bash
python interactive_chat.py
```

---

## 📝 Example Questions

**Turkish**
"Yüksek lisans programları neler?"
"Üniversite ücretleri ne kadar?"
"Burs imkanları var mı?"
"Kampüste yurt var mı?"
"Yabancı öğrenci başvurusu nasıl yapılır?"

**English**
"What are the graduate programs?"
"What are the tuition fees?"
"Are there scholarships available?"
"How to apply as an international student?"

---

## 🔧 Troubleshooting

### Error: No module named 'openai'

```bash
pip install openai
```
### Error: Invalid API key

Check your .env file has the correct key
Make sure .env is in the chunking/ folder
Verify key format: OPENAI_API_KEY=sk-...

### Error: File not found

```bash
# Make sure you're in the right directory
cd ~/projects/izu_scraper/chunking
ls  # Should see: chunks.json, faiss_index.bin, embeddings_openai.npy
```

# Make sure you're in the right directory
```bash
cd ~/projects/izu_scraper/chunking
ls  # Should see: chunks.json, faiss_index.bin, embeddings_openai.npy
```

### **Slow responses**
- Normal first time (loading models)
- Embeddings API: ~1-2 seconds
- GPT-4o-mini: ~2-5 seconds
- Total: ~3-7 seconds per question

---

## 💰 Cost Estimates

**Per 1000 questions (assuming avg 3 chunks retrieved):**
- Embeddings: ~$0.02
- GPT-4o-mini: ~$0.30
- **Total: ~$0.32 per 1000 questions**

Very affordable! 🎉

---

## 📊 System Performance

- **Retrieval time**: ~0.5 seconds
- **Generation time**: ~2-5 seconds
- **Total response time**: ~3-7 seconds
- **Accuracy**: High (uses actual university data)
- **Languages**: Turkish & English

---

## 🔐 Security Notes

⚠️ **NEVER commit `.env` file to Git!**

Add to `.gitignore`:
```
.env
*.npy
faiss_index.bin

---

## 📚 Files Explanation

| File | Purpose | Size |
|------|--------|------|
| chunks.json | Processed university data | ~5–20 MB |
| embeddings_openai.npy | Vector embeddings | ~50–200 MB |
| faiss_index.bin | Vector database | ~50–200 MB |
| rag_config.json | Configuration | <1 KB |
| .env | API keys | <1 KB |

---

## 🎯 Next Steps

- Build a web interface (Streamlit / Gradio)
- Deploy to cloud (Railway, AWS, Heroku)
- Add conversation history
- Add citation links
- Add analytics and feedback system

---

## 🆘 Support
Issues? Check:

Virtual environment activated?
API key set correctly in .env?
All files present in chunking/ folder?
OpenAI account has credits?

Still stuck? Check OpenAI API status: https://status.openai.com/

---


## ✅ Success Checklist

- [ ] Virtual environment activated  
- [ ] Dependencies installed  
- [ ] `.env` file created  
- [ ] Required files present  
- [ ] `python chat.py` runs successfully  
- [ ] Chatbot answers test questions  

---

🎉 You are ready to use the IZU University RAG Chatbot.

### Quick test:
```bash
cd ~/projects/izu_scraper/chunking
python interactive_chat.py
```

Ask: "Üniversite hakkında bilgi ver" and see the magic! ✨
