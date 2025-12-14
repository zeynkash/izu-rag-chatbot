# Project Structure
```
izu-rag-chatbot/
├── README.md                    # Main documentation
├── SETUP.md                     # Setup instructions
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
│
├── izu_scraper/                 # Scrapy project
│   ├── settings.py              # Scrapy settings
│   ├── items.py                 # Data structures
│   ├── pipelines.py             # Data processing
│   └── spiders/                 # Web scrapers
│       ├── izu_spider.py        # Main spider
│       └── clean_student_spider.py  # Student pages spider
│
├── chunking/                    # RAG system
│   ├── chunking.ipynb           # Data chunking notebook
│   ├── rag_system.ipynb         # RAG system notebook
│   ├── chat.py                  # Simple chat script
│   ├── interactive_chat.py      # Interactive chat
│   ├── .env.example             # Example environment file
│   └── rag_config.json          # System configuration
│
├── output/                      # Scraped data (not in git)
├── logs/                        # Logs (not in git)
└── scripts/                     # Utility scripts
    ├── run_spider.sh            # Run scraper
    └── test_rag.py              # Test RAG system
```

## Large Files (Not in Git)

These files are generated during setup:
- `embeddings_openai.npy` (~100-200 MB)
- `faiss_index.bin` (~100-200 MB)
- `chunks.json` (~10-50 MB)
- `output/*.csv` (Scraped data)

Download from: [Release Page] or generate them using setup instructions.
