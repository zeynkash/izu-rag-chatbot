#!/usr/bin/env python3
"""
Quick RAG System Test
Fast smoke test with 5 sample questions to verify system works
"""

import json
import numpy as np
import faiss
import openai
from dotenv import load_dotenv
import os
import time
from datetime import datetime

# Setup
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

print("=" * 80)
print("QUICK RAG SYSTEM TEST")
print("=" * 80)
print()

# ============================================================================
# LOAD RESOURCES
# ============================================================================

print("Loading RAG system components...")
print("-" * 80)

try:
    # Load chunks
    with open('chunks.json', 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"✓ Chunks: {len(chunks)} loaded")
    
    # Load FAISS index
    index = faiss.read_index('faiss_index.bin')
    print(f"✓ FAISS Index: {index.ntotal} vectors")
    
    # Load embeddings (for verification)
    embeddings = np.load('embeddings_openai_izu.npy')
    print(f"✓ Embeddings: {embeddings.shape}")
    
    print()
    
except Exception as e:
    print(f"✗ Error loading resources: {e}")
    print("\nMake sure you're in the chunking/ directory and all files exist:")
    print("  - chunks.json")
    print("  - faiss_index.bin")
    print("  - embeddings_openai_izu.npy")
    print("  - .env (with OPENAI_API_KEY)")
    exit(1)

# ============================================================================
# RAG FUNCTIONS
# ============================================================================

def get_embedding(text):
    """Get embedding for text"""
    response = openai.embeddings.create(
        input=[text.replace("\n", " ")],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def retrieve_chunks(query, top_k=5):
    """Retrieve most relevant chunks"""
    # Get query embedding
    query_embedding = np.array([get_embedding(query)], dtype='float32')
    faiss.normalize_L2(query_embedding)
    
    # Search
    scores, indices = index.search(query_embedding, top_k)
    
    # Return chunks
    results = []
    for idx, score in zip(indices[0], scores[0]):
        results.append({
            'content': chunks[idx]['content'],
            'metadata': chunks[idx]['metadata'],
            'score': float(score)
        })
    return results

def answer_question(query, top_k=5):
    """Answer question using RAG"""
    start_time = time.time()
    
    # Retrieve
    retrieval_start = time.time()
    retrieved = retrieve_chunks(query, top_k)
    retrieval_time = time.time() - retrieval_start
    
    # Build context
    context = "\n---\n".join([
        f"Kaynak: {c['metadata']['title']}\n{c['content']}"
        for c in retrieved
    ])
    
    # Generate
    generation_start = time.time()
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sen İZÜ (İstanbul Sabahattin Zaim Üniversitesi) için bir asistansın. Sadece verilen bilgileri kullan. Türkçe cevap ver."},
            {"role": "user", "content": f"Context:\n{context}\n\nSoru: {query}"}
        ],
        temperature=0.3,
        max_tokens=500
    )
    generation_time = time.time() - generation_start
    
    total_time = time.time() - start_time
    
    return {
        'answer': response.choices[0].message.content,
        'retrieved_chunks': retrieved,
        'retrieval_time': retrieval_time,
        'generation_time': generation_time,
        'total_time': total_time,
        'tokens_used': response.usage.total_tokens
    }

# ============================================================================
# RUN QUICK TESTS
# ============================================================================

print("Running quick tests (5 questions)...")
print("=" * 80)
print()

# Test questions
test_questions = [
    "İZÜ'de kaç fakülte var?",
    "Yüksek lisans programları nelerdir?",
    "Burs imkanları var mı?",
    "Kampüste yurt var mı?",
    "Erasmus programı var mı?"
]

results = []
total_time = 0
total_tokens = 0

for i, question in enumerate(test_questions, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}/{len(test_questions)}")
    print(f"{'='*80}")
    print(f"Soru: {question}")
    print()
    
    try:
        result = answer_question(question)
        
        print(f"✓ Cevap:")
        print(f"  {result['answer']}")
        print()
        print(f"⏱ Performans:")
        print(f"  Toplam süre: {result['total_time']:.2f}s")
        print(f"  Retrieval: {result['retrieval_time']:.2f}s")
        print(f"  Generation: {result['generation_time']:.2f}s")
        print(f"  Tokens: {result['tokens_used']}")
        print()
        print(f"📊 Bulunan Kaynaklar:")
        for j, chunk in enumerate(result['retrieved_chunks'][:3], 1):
            print(f"  {j}. {chunk['metadata']['title'][:60]}... (score: {chunk['score']:.3f})")
        
        results.append(result)
        total_time += result['total_time']
        total_tokens += result['tokens_used']
        
    except Exception as e:
        print(f"✗ Error: {e}")
        continue

# ============================================================================
# SUMMARY
# ============================================================================

print()
print("=" * 80)
print("QUICK TEST SUMMARY")
print("=" * 80)
print()

if results:
    avg_time = total_time / len(results)
    avg_tokens = total_tokens / len(results)
    
    print(f"✓ Tests Passed: {len(results)}/{len(test_questions)}")
    print(f"✓ Average Response Time: {avg_time:.2f}s")
    print(f"✓ Average Tokens: {avg_tokens:.0f}")
    print(f"✓ Total Tokens Used: {total_tokens}")
    print(f"✓ Estimated Cost: ${total_tokens * 0.0000004:.4f}")
    print()
    
    # Performance check
    if avg_time < 3.0:
        print("✓ Performance: GOOD (< 3 seconds)")
    elif avg_time < 5.0:
        print("⚠ Performance: ACCEPTABLE (3-5 seconds)")
    else:
        print("✗ Performance: SLOW (> 5 seconds)")
    
    print()
    print("=" * 80)
    print("SYSTEM STATUS: ✓ WORKING")
    print("=" * 80)
    print()
    print("Next step: Run full evaluation with all 50 questions")
    print("  python evaluate_rag.py")
    
else:
    print("✗ All tests failed!")
    print("Please check:")
    print("  1. OpenAI API key is valid")
    print("  2. Chunks and index files are correct")
    print("  3. Internet connection is working")

print()
