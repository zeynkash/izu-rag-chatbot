import streamlit as st
import json
import numpy as np
import faiss
import openai
from dotenv import load_dotenv
import os
from datetime import datetime
import time

# Load environment
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load RAG system
@st.cache_resource
def load_rag_system():
    with open('chunks.json', 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    index = faiss.read_index('faiss_index.bin')
    return chunks, index

chunks, index = load_rag_system()

# Production logging function (PASTE HERE)
def log_production_query(question, answer, retrieval_time, generation_time, cost, user_feedback=None):
    """Log queries for monitoring and improvement"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'question': question,
        'answer': answer,
        'retrieval_time_ms': retrieval_time * 1000,
        'generation_time_ms': generation_time * 1000,
        'total_time_ms': (retrieval_time + generation_time) * 1000,
        'cost_usd': cost,
        'user_feedback': user_feedback  # thumbs up/down
    }
    
    # Append to log file
    with open('production_logs.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

# RAG functions
def get_embedding(text):
    response = openai.embeddings.create(
        input=[text.replace("\n", " ")],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def retrieve_chunks(query, top_k=5):
    start_time = time.time()
    
    query_embedding = np.array([get_embedding(query)], dtype='float32')
    faiss.normalize_L2(query_embedding)
    scores, indices = index.search(query_embedding, top_k)
    
    retrieval_time = time.time() - start_time
    
    results = []
    for idx, score in zip(indices[0], scores[0]):
        results.append({
            'content': chunks[idx]['content'],
            'metadata': chunks[idx]['metadata'],
            'score': float(score)
        })
    
    return results, retrieval_time

def generate_answer(query, retrieved_chunks):
    start_time = time.time()
    
    context = "\n---\n".join([
        f"[{c['metadata']['title']}]\n{c['content']}" 
        for c in retrieved_chunks
    ])
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "İZÜ için bir asistansın. Sadece verilen bilgileri kullan."},
            {"role": "user", "content": f"Context:\n{context}\n\nSoru: {query}"}
        ],
        temperature=0.3
    )
    
    generation_time = time.time() - start_time
    
    # Calculate cost
    tokens = response.usage.total_tokens
    cost = (tokens / 1000) * 0.0004
    
    return {
        'answer': response.choices[0].message.content,
        'generation_time': generation_time,
        'tokens': tokens,
        'cost': cost,
        'sources': [c['metadata'] for c in retrieved_chunks]
    }

# Streamlit UI
st.title("🎓 İZÜ Chatbot")
st.write("İstanbul Sabahattin Zaim Üniversitesi hakkında sorularınızı sorun")

# Chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Sorunuzu yazın..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum..."):
            # Retrieve
            retrieved, retrieval_time = retrieve_chunks(prompt, top_k=3)
            
            # Generate
            result = generate_answer(prompt, retrieved)
            
            # Display answer
            st.markdown(result['answer'])
            
            # Display sources (optional)
            with st.expander("📚 Kaynaklar"):
                for i, source in enumerate(result['sources'], 1):
                    st.write(f"{i}. [{source['title']}]({source['url']})")
            
            # Log to production (THIS IS WHERE IT'S USED!)
            log_production_query(
                question=prompt,
                answer=result['answer'],
                retrieval_time=retrieval_time,
                generation_time=result['generation_time'],
                cost=result['cost']
            )
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": result['answer']})

# Feedback buttons
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("👍"):
        st.success("Teşekkürler!")
        # Log positive feedback
        if st.session_state.messages:
            last_q = st.session_state.messages[-2]['content']
            last_a = st.session_state.messages[-1]['content']
            log_production_query(last_q, last_a, 0, 0, 0, user_feedback='positive')

with col2:
    if st.button("👎"):
        st.info("Geri bildiriminiz kaydedildi")
        # Log negative feedback
        if st.session_state.messages:
            last_q = st.session_state.messages[-2]['content']
            last_a = st.session_state.messages[-1]['content']
            log_production_query(last_q, last_a, 0, 0, 0, user_feedback='negative')