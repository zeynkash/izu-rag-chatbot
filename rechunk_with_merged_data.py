#!/usr/bin/env python3
"""
Automated Rechunking Script
Runs the chunking process on merged data and generates embeddings
"""

import json
import pandas as pd
import tiktoken
import re
from tqdm import tqdm
import statistics
import os

print("=" * 80)
print("AUTOMATED RAG DATA PREPARATION")
print("=" * 80)
print()

# Change to chunking directory
os.chdir('/home/zeynkash/projects/izu_scraper/chunking')

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================

print("STEP 1: Loading merged data...")
print("-" * 80)

data = []
with open('all_data_cleaned.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

print(f"✓ Loaded {len(data)} documents")
print(f"  Average content length: {sum(len(d['content']) for d in data) / len(data):.0f} characters")

# ============================================================================
# STEP 2: INITIALIZE TOKENIZER
# ============================================================================

print("\nSTEP 2: Initializing tokenizer...")
print("-" * 80)

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def count_tokens(text):
    """Count tokens in text"""
    if not text:
        return 0
    return len(encoding.encode(text))

print("✓ Tokenizer ready")

# ============================================================================
# STEP 3: CHUNKING FUNCTION
# ============================================================================

print("\nSTEP 3: Preparing chunking functions...")
print("-" * 80)

def smart_split_into_chunks(text, chunk_size=800, chunk_overlap=150):
    """Split text into chunks with sentence boundary awareness"""
    if not text or not text.strip():
        return []
    
    # Split into sentences
    sentence_endings = r'[.!?]\s+'
    sentences = re.split(sentence_endings, text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        
        # If single sentence exceeds chunk_size, split it
        if sentence_tokens > chunk_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_tokens = 0
            
            # Split long sentence
            tokens = encoding.encode(sentence)
            for i in range(0, len(tokens), chunk_size - chunk_overlap):
                chunk_tokens = tokens[i:i + chunk_size]
                chunks.append(encoding.decode(chunk_tokens))
            continue
        
        # Check if adding this sentence exceeds chunk_size
        if current_tokens + sentence_tokens > chunk_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            # Start new chunk with overlap
            overlap_sentences = []
            overlap_tokens = 0
            
            for sent in reversed(current_chunk):
                sent_tokens = count_tokens(sent)
                if overlap_tokens + sent_tokens <= chunk_overlap:
                    overlap_sentences.insert(0, sent)
                    overlap_tokens += sent_tokens
                else:
                    break
            
            current_chunk = overlap_sentences
            current_tokens = overlap_tokens
        
        current_chunk.append(sentence)
        current_tokens += sentence_tokens
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def chunk_document(doc, chunk_size=800, chunk_overlap=150):
    """Chunk a single document with metadata"""
    content = doc.get('content', '')
    title = doc.get('title', 'Untitled')
    url = doc.get('url', '')
    
    # Add context header
    header = f"Title: {title}\nURL: {url}\n\n"
    full_content = header + content
    
    # Split into chunks
    text_chunks = smart_split_into_chunks(full_content, chunk_size, chunk_overlap)
    
    # Create chunk objects
    chunk_objects = []
    for i, chunk_text in enumerate(text_chunks):
        chunk_obj = {
            'chunk_id': f"{hash(url)}_{i}",
            'document_id': hash(url),
            'chunk_index': i,
            'total_chunks': len(text_chunks),
            'content': chunk_text,
            'tokens': count_tokens(chunk_text),
            'metadata': {
                'url': url,
                'title': title,
                'language': doc.get('language', 'unknown'),
                'section': doc.get('section', 'general'),
                'category': doc.get('section', 'general'),  # Add category
                'date_scraped': doc.get('date_scraped', ''),
            }
        }
        chunk_objects.append(chunk_obj)
    
    return chunk_objects

print("✓ Chunking functions ready")

# ============================================================================
# STEP 4: CHUNK ALL DOCUMENTS
# ============================================================================

print("\nSTEP 4: Chunking all documents...")
print("-" * 80)

all_chunks = []

for doc in tqdm(data, desc="Chunking"):
    try:
        chunks = chunk_document(doc, chunk_size=800, chunk_overlap=150)
        all_chunks.extend(chunks)
    except Exception as e:
        print(f"\nError chunking {doc.get('url', 'unknown')}: {e}")
        continue

print(f"\n✓ Chunking complete!")
print(f"  Original documents: {len(data)}")
print(f"  Total chunks: {len(all_chunks)}")
print(f"  Average chunks per doc: {len(all_chunks) / len(data):.1f}")

# ============================================================================
# STEP 5: STATISTICS
# ============================================================================

print("\nSTEP 5: Calculating statistics...")
print("-" * 80)

chunk_tokens = [c['tokens'] for c in all_chunks]

print(f"\nToken Distribution:")
print(f"  Mean: {statistics.mean(chunk_tokens):.0f} tokens")
print(f"  Median: {statistics.median(chunk_tokens):.0f} tokens")
print(f"  Min: {min(chunk_tokens)} tokens")
print(f"  Max: {max(chunk_tokens)} tokens")

# Language distribution
lang_dist = {}
for chunk in all_chunks:
    lang = chunk['metadata']['language']
    lang_dist[lang] = lang_dist.get(lang, 0) + 1

print(f"\nLanguage Distribution:")
for lang, count in sorted(lang_dist.items()):
    print(f"  {lang}: {count} chunks ({count/len(all_chunks)*100:.1f}%)")

# Category distribution
category_dist = {}
for chunk in all_chunks:
    cat = chunk['metadata'].get('category', 'general')
    category_dist[cat] = category_dist.get(cat, 0) + 1

print(f"\nCategory Distribution:")
for cat, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cat}: {count} chunks ({count/len(all_chunks)*100:.1f}%)")

# Quality check
optimal_chunks = [c for c in all_chunks if 300 <= c['tokens'] <= 900]
print(f"\n✓ Optimal chunks (300-900 tokens): {len(optimal_chunks)} ({len(optimal_chunks)/len(all_chunks)*100:.1f}%)")

# ============================================================================
# STEP 6: SAVE CHUNKS
# ============================================================================

print("\nSTEP 6: Saving chunks...")
print("-" * 80)

# Save as JSON
with open('chunks.json', 'w', encoding='utf-8') as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)
print("✓ Saved: chunks.json")

# Save as JSONL
with open('chunks.jsonl', 'w', encoding='utf-8') as f:
    for chunk in all_chunks:
        f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
print("✓ Saved: chunks.jsonl")

# Save metadata
metadata = {
    'total_documents': len(data),
    'total_chunks': len(all_chunks),
    'avg_chunks_per_doc': len(all_chunks) / len(data),
    'chunk_size': 800,
    'chunk_overlap': 150,
    'avg_tokens_per_chunk': statistics.mean(chunk_tokens),
    'languages': lang_dist,
    'categories': category_dist,
}

with open('chunks_metadata.json', 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
print("✓ Saved: chunks_metadata.json")

# Save preview CSV
chunks_df = pd.DataFrame([
    {
        'chunk_id': c['chunk_id'],
        'tokens': c['tokens'],
        'language': c['metadata']['language'],
        'category': c['metadata'].get('category', 'general'),
        'title': c['metadata']['title'],
        'content_preview': c['content'][:200] + '...'
    }
    for c in all_chunks
])

chunks_df.to_csv('chunks_preview.csv', index=False)
print("✓ Saved: chunks_preview.csv")

# ============================================================================
# SUMMARY
# ============================================================================

print()
print("=" * 80)
print("CHUNKING SUMMARY")
print("=" * 80)
print()
print(f"📊 Input:")
print(f"   Documents: {len(data)}")
print()
print(f"📦 Output:")
print(f"   Total chunks: {len(all_chunks)}")
print(f"   Avg chunks/doc: {len(all_chunks) / len(data):.1f}")
print()
print(f"🎯 Quality:")
print(f"   Avg tokens/chunk: {statistics.mean(chunk_tokens):.0f}")
print(f"   Optimal chunks: {len(optimal_chunks)/len(all_chunks)*100:.1f}%")
print()
print(f"🌍 Content:")
for lang, count in sorted(lang_dist.items(), key=lambda x: x[1], reverse=True)[:3]:
    print(f"   {lang}: {count} chunks")
print()
print(f"📁 Files created:")
print(f"   - chunks.json")
print(f"   - chunks.jsonl")
print(f"   - chunks_metadata.json")
print(f"   - chunks_preview.csv")
print()
print("=" * 80)
print("✅ CHUNKING COMPLETE!")
print("=" * 80)
print()
print("Next step: Generate embeddings")
print("  Run the rag_system.ipynb notebook to create embeddings and FAISS index")
print()
