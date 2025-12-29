#!/usr/bin/env python3
"""
Add English Pages to Existing Vector Database
Integrates newly scraped English pages into the existing FAISS index and chunks
"""

import json
import numpy as np
import faiss
import openai
from dotenv import load_dotenv
import os
from typing import List, Dict
import tiktoken
from tqdm import tqdm

# Load environment
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Paths
NEW_DATA_PATH = "output/izu_english_pages.json"
EXISTING_CHUNKS_PATH = "chunking/chunks.json"
EXISTING_INDEX_PATH = "chunking/faiss_index.bin"
EXISTING_EMBEDDINGS_PATH = "chunking/embeddings_openai_izu.npy"

# Config
EMBEDDING_MODEL = "text-embedding-3-small"
MAX_TOKENS = 400  # Max tokens per chunk


def load_existing_data():
    """Load existing chunks and embeddings"""
    print("📂 Loading existing data...")
    
    with open(EXISTING_CHUNKS_PATH, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    index = faiss.read_index(EXISTING_INDEX_PATH)
    embeddings = np.load(EXISTING_EMBEDDINGS_PATH)
    
    print(f"✓ Loaded {len(chunks)} existing chunks")
    print(f"✓ FAISS index size: {index.ntotal}")
    
    return chunks, index, embeddings


def load_new_pages():
    """Load newly scraped English pages"""
    print(f"\n📄 Loading new English pages from {NEW_DATA_PATH}...")
    
    if not os.path.exists(NEW_DATA_PATH):
        print(f"❌ File not found: {NEW_DATA_PATH}")
        print("Run scrape_english_pages.py first!")
        return []
    
    with open(NEW_DATA_PATH, 'r', encoding='utf-8') as f:
        pages = json.load(f)
    
    print(f"✓ Loaded {len(pages)} new pages")
    return pages


def split_into_chunks(text: str, max_tokens: int = MAX_TOKENS) -> List[str]:
    """Split text into chunks based on token count"""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)
    
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    
    return chunks


def process_new_pages(pages: List[Dict]) -> List[Dict]:
    """Convert pages into chunks with metadata"""
    print("\n✂️ Chunking new pages...")
    
    new_chunks = []
    
    for page in tqdm(pages, desc="Processing pages"):
        content = page['content']
        
        if len(content.strip()) < 100:
            continue
        
        # Chunk the content
        text_chunks = split_into_chunks(content)
        
        # Create chunk entries
        for i, chunk_text in enumerate(text_chunks):
            new_chunks.append({
                'chunk_id': f"en_{page['url'].split('/')[-1]}_{i}",
                'content': chunk_text,
                'metadata': {
                    'title': page['title'],
                    'url': page['url'],
                    'source': 'english_scraper',
                    'chunk_index': i,
                    'total_chunks': len(text_chunks),
                    'language': 'en'
                }
            })
    
    print(f"✓ Created {len(new_chunks)} new chunks from {len(pages)} pages")
    return new_chunks


def generate_embeddings(chunks: List[Dict]) -> np.ndarray:
    """Generate OpenAI embeddings for chunks"""
    print("\n🔢 Generating embeddings...")
    
    texts = [chunk['content'] for chunk in chunks]
    embeddings = []
    
    batch_size = 100
    for i in tqdm(range(0, len(texts), batch_size), desc="Embedding batches"):
        batch = texts[i:i + batch_size]
        
        response = openai.embeddings.create(
            input=batch,
            model=EMBEDDING_MODEL
        )
        
        batch_embeddings = [item.embedding for item in response.data]
        embeddings.extend(batch_embeddings)
    
    embeddings_array = np.array(embeddings, dtype='float32')
    print(f"✓ Generated {len(embeddings)} embeddings, shape: {embeddings_array.shape}")
    
    return embeddings_array


def update_vector_database(existing_chunks, existing_index, existing_embeddings, new_chunks, new_embeddings):
    """Add new chunks and embeddings to existing database"""
    print("\n🔄 Updating vector database...")
    
    # Combine chunks
    all_chunks = existing_chunks + new_chunks
    
    # Combine embeddings
    all_embeddings = np.vstack([existing_embeddings, new_embeddings])
    
    # Normalize for cosine similarity
    faiss.normalize_L2(new_embeddings)
    
    # Add to FAISS index
    existing_index.add(new_embeddings)
    
    print(f"✓ Combined chunks: {len(existing_chunks)} + {len(new_chunks)} = {len(all_chunks)}")
    print(f"✓ FAISS index size: {existing_index.ntotal}")
    
    return all_chunks, existing_index, all_embeddings


def save_updated_database(chunks, index, embeddings):
    """Save updated database"""
    print("\n💾 Saving updated database...")
    
    # Backup old files
    print("Creating backups...")
    os.system(f"cp {EXISTING_CHUNKS_PATH} {EXISTING_CHUNKS_PATH}.backup")
    os.system(f"cp {EXISTING_INDEX_PATH} {EXISTING_INDEX_PATH}.backup")
    os.system(f"cp {EXISTING_EMBEDDINGS_PATH} {EXISTING_EMBEDDINGS_PATH}.backup")
    
    # Save new files
    with open(EXISTING_CHUNKS_PATH, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved chunks.json ({len(chunks)} chunks)")
    
    faiss.write_index(index, EXISTING_INDEX_PATH)
    print(f"✓ Saved FAISS index ({index.ntotal} vectors)")
    
    np.save(EXISTING_EMBEDDINGS_PATH, embeddings)
    print(f"✓ Saved embeddings ({embeddings.shape[0]} vectors)")
    
    print("\n✅ Backups created with .backup extension")


def main():
    print("="*80)
    print("ADD ENGLISH PAGES TO VECTOR DATABASE")
    print("="*80)
    
    # Load existing data
    existing_chunks, existing_index, existing_embeddings = load_existing_data()
    
    # Load new pages
    new_pages = load_new_pages()
    if not new_pages:
        print("No new pages to add. Exiting.")
        return
    
    # Process new pages into chunks
    new_chunks = process_new_pages(new_pages)
    
    # Generate embeddings
    new_embeddings = generate_embeddings(new_chunks)
    
    # Update database
    all_chunks, updated_index, all_embeddings = update_vector_database(
        existing_chunks, existing_index, existing_embeddings,
        new_chunks, new_embeddings
    )
    
    # Save
    save_updated_database(all_chunks, updated_index, all_embeddings)
    
    print("\n" + "="*80)
    print("✅ INTEGRATION COMPLETE")
    print("="*80)
    print(f"Total chunks: {len(all_chunks)}")
    print(f"New chunks added: {len(new_chunks)}")
    print(f"From pages: {len(new_pages)}")
    print("\n🎉 English pages successfully added to your vector database!")


if __name__ == "__main__":
    main()
