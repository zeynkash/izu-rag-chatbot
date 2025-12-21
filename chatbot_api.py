#!/usr/bin/env python3
"""
IZU RAG Chatbot - FastAPI Backend
Production-ready API for the university chatbot
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import numpy as np
import faiss
import openai
from dotenv import load_dotenv
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize FastAPI
app = FastAPI(
    title="IZU RAG Chatbot API",
    description="AI-powered chatbot for Istanbul Sabahattin Zaim University",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "tr"  # tr or en
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    response_time_ms: float
    conversation_id: str

class HealthResponse(BaseModel):
    status: str
    chunks_loaded: int
    index_size: int
    timestamp: str

# Global variables (loaded on startup)
chunks = None
faiss_index = None
embeddings = None

def load_rag_system():
    """Load chunks, embeddings, and FAISS index"""
    global chunks, faiss_index, embeddings
    
    logger.info("Loading RAG system...")
    
    # Load chunks
    chunks_path = '/home/zeynkash/projects/izu_scraper/chunking/chunks.json'
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    logger.info(f"✓ Loaded {len(chunks)} chunks")
    
    # Load FAISS index
    index_path = '/home/zeynkash/projects/izu_scraper/chunking/faiss_index.bin'
    faiss_index = faiss.read_index(index_path)
    logger.info(f"✓ Loaded FAISS index: {faiss_index.ntotal} vectors")
    
    # Load embeddings (optional, for verification)
    emb_path = '/home/zeynkash/projects/izu_scraper/chunking/embeddings_openai_izu.npy'
    embeddings = np.load(emb_path)
    logger.info(f"✓ Loaded embeddings: {embeddings.shape}")
    
    logger.info("✓ RAG system ready!")

@app.on_event("startup")
async def startup_event():
    """Load RAG system on startup"""
    try:
        load_rag_system()
    except Exception as e:
        logger.error(f"Failed to load RAG system: {e}")
        raise

def get_embedding(text: str) -> List[float]:
    """Get OpenAI embedding for text"""
    response = openai.embeddings.create(
        input=[text.replace("\n", " ")],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def retrieve_chunks(query: str, top_k: int = 5) -> List[dict]:
    """Retrieve most relevant chunks using FAISS"""
    # Get query embedding
    query_embedding = np.array([get_embedding(query)], dtype='float32')
    faiss.normalize_L2(query_embedding)
    
    # Search
    scores, indices = faiss_index.search(query_embedding, top_k)
    
    # Get chunks
    results = []
    for idx, score in zip(indices[0], scores[0]):
        if idx < len(chunks):
            results.append({
                'content': chunks[idx]['content'],
                'metadata': chunks[idx]['metadata'],
                'score': float(score)
            })
    
    return results

def generate_answer(query: str, retrieved_chunks: List[dict], language: str = "tr") -> str:
    """Generate answer using GPT-4o-mini"""
    
    # Build context from retrieved chunks
    context = "\n---\n".join([
        f"Kaynak: {chunk['metadata']['title']}\n{chunk['content']}"
        for chunk in retrieved_chunks
    ])
    
    # System prompt based on language
    if language == "tr":
        system_prompt = """Sen İstanbul Sabahattin Zaim Üniversitesi (İZÜ) için bir yardımcı asistansın. 
Sadece verilen bilgileri kullanarak soruları cevapla. 
Eğer bilgi yoksa, "Bu konuda detaylı bilgi bulunamadı" de.
Cevaplarını net, kısa ve yardımcı tut."""
    else:
        system_prompt = """You are a helpful assistant for Istanbul Sabahattin Zaim University (IZU).
Answer questions using only the provided information.
If you don't have information, say "I don't have detailed information about this."
Keep answers clear, concise, and helpful."""
    
    # Generate response
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "IZU RAG Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if chunks and faiss_index else "not ready",
        chunks_loaded=len(chunks) if chunks else 0,
        index_size=faiss_index.ntotal if faiss_index else 0,
        timestamp=datetime.now().isoformat()
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - main RAG pipeline
    
    Returns answer with sources and metadata
    """
    import time
    start_time = time.time()
    
    try:
        # Validate
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(request.message) > 500:
            raise HTTPException(status_code=400, detail="Message too long (max 500 characters)")
        
        logger.info(f"Query: {request.message[:100]}...")
        
        # Retrieve relevant chunks
        retrieved = retrieve_chunks(request.message, top_k=5)
        logger.info(f"Retrieved {len(retrieved)} chunks")
        
        # Generate answer
        answer = generate_answer(request.message, retrieved, request.language)
        logger.info(f"Generated answer: {len(answer)} chars")
        
        # Calculate time
        response_time = (time.time() - start_time) * 1000
        
        # Format sources
        sources = [
            {
                "title": chunk['metadata'].get('title', 'Unknown'),
                "url": chunk['metadata'].get('url', ''),
                "score": chunk['score'],
                "snippet": chunk['content'][:200] + "..."
            }
            for chunk in retrieved
        ]
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{int(time.time())}"
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            response_time_ms=response_time,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=dict)
async def get_stats():
    """Get system statistics"""
    return {
        "total_chunks": len(chunks) if chunks else 0,
        "index_type": "FAISS",
        "embedding_model": "text-embedding-3-small",
        "llm_model": "gpt-4o-mini",
        "embedding_dimension": embeddings.shape[1] if embeddings is not None else 0,
        "average_chunk_length": np.mean([len(c['content']) for c in chunks]) if chunks else 0
    }

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*80)
    print("IZU RAG CHATBOT - STARTING SERVER")
    print("="*80)
    print("\nServer will start at: http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop")
    print("="*80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
