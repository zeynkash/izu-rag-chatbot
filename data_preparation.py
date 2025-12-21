"""
PHASE 1: DATA PREPARATION FOR IZU RAG SYSTEM
This script prepares your data for experiments
Run once, then use the processed files for all experiments
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pickle
import os

def step1_load_dataset(json_file='/home/zeynkash/projects/izu_scraper/chunking/chunks.json'):
    """Step 1: Load the IZU dataset (NEW: using pre-chunked data)"""
    print("\n" + "="*80)
    print("STEP 1: LOADING DATASET (NEW MERGED DATA)")
    print("="*80)
    
    if not os.path.exists(json_file):
        print(f"❌ ERROR: File '{json_file}' not found!")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Trying chunks.json from chunking directory...")
        return None
    
    print(f"Loading: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks_data = json.load(f)
    
    print(f"✓ Loaded {len(chunks_data)} pre-chunked items")
    
    # Convert chunks format to document format for compatibility
    # New chunks.json has: chunk_id, content, metadata
    # Old format expected: title, url, content
    documents = []
    for chunk in chunks_data:
        documents.append({
            'title': chunk.get('metadata', {}).get('title', 'Untitled'),
            'url': chunk.get('metadata', {}).get('url', ''),
            'content': chunk.get('content', '')
        })
    
    print(f"✓ Converted to {len(documents)} document format")
    
    # Show sample
    if documents:
        print(f"\nSample document:")
        print(f"  Title: {documents[0].get('title', 'N/A')[:60]}...")
        print(f"  URL: {documents[0].get('url', 'N/A')}")
        print(f"  Content length: {len(documents[0].get('content', ''))} characters")
    
    return documents


def step2_create_chunks(documents, chunk_size=500, overlap=100):
    """Step 2: Split documents into smaller chunks"""
    print("\n" + "="*80)
    print("STEP 2: CREATING CHUNKS")
    print("="*80)
    print(f"Chunk size: {chunk_size} characters")
    print(f"Overlap: {overlap} characters")
    
    chunks = []
    
    for doc in tqdm(documents, desc="Processing documents"):
        content = doc.get('content', '')
        title = doc.get('title', 'Untitled')
        url = doc.get('url', '')
        
        if len(content) < 50:  # Skip very short content
            continue
        
        # Split into words
        words = content.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for space
            
            # When chunk reaches target size, save it
            if current_length >= chunk_size:
                chunk_text = ' '.join(current_chunk)
                
                chunks.append({
                    'text': chunk_text,
                    'title': title,
                    'url': url,
                    'source_doc': url
                })
                
                # Keep some overlap for context
                overlap_words = int(len(current_chunk) * 0.2)
                current_chunk = current_chunk[-overlap_words:] if overlap_words > 0 else []
                current_length = sum(len(w)+1 for w in current_chunk)
        
        # Add remaining words as final chunk
        if current_chunk and len(' '.join(current_chunk)) > 50:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'title': title,
                'url': url,
                'source_doc': url
            })
    
    print(f"\n✓ Created {len(chunks)} chunks")
    print(f"  Average chunk length: {np.mean([len(c['text']) for c in chunks]):.0f} characters")
    
    return chunks


def step3_generate_embeddings(chunks):
    """Step 3: Convert text chunks to embeddings (vectors)"""
    print("\n" + "="*80)
    print("STEP 3: GENERATING EMBEDDINGS")
    print("="*80)
    print("Loading embedding model (this may take a minute first time)...")
    
    # Load the embedding model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("✓ Model loaded")
    
    # Extract just the text from chunks
    texts = [chunk['text'] for chunk in chunks]
    
    print(f"\nGenerating embeddings for {len(texts)} chunks...")
    print("(This will take a few minutes depending on dataset size)")
    
    # Generate embeddings
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        convert_to_numpy=True
    )
    
    print(f"\n✓ Generated embeddings")
    print(f"  Shape: {embeddings.shape}")
    print(f"  (Each chunk = {embeddings.shape[1]} dimensional vector)")
    
    return embeddings


def step4_create_splits(chunks, embeddings):
    """Step 4: Create small (40%), medium (60%), large (100%) splits"""
    print("\n" + "="*80)
    print("STEP 4: CREATING DATASET SPLITS")
    print("="*80)
    
    total = len(chunks)
    small_size = int(total * 0.4)
    medium_size = int(total * 0.6)
    
    splits = {
        'small': {
            'chunks': chunks[:small_size],
            'embeddings': embeddings[:small_size],
            'percentage': 40
        },
        'medium': {
            'chunks': chunks[:medium_size],
            'embeddings': embeddings[:medium_size],
            'percentage': 60
        },
        'large': {
            'chunks': chunks,
            'embeddings': embeddings,
            'percentage': 100
        }
    }
    
    print(f"\n✓ Created 3 splits:")
    print(f"  Small:  {len(splits['small']['chunks']):,} chunks (40%)")
    print(f"  Medium: {len(splits['medium']['chunks']):,} chunks (60%)")
    print(f"  Large:  {len(splits['large']['chunks']):,} chunks (100%)")
    
    return splits


def step5_save_everything(chunks, embeddings, splits):
    """Step 5: Save all processed data"""
    print("\n" + "="*80)
    print("STEP 5: SAVING PROCESSED DATA")
    print("="*80)
    
    # Save chunks
    print("\nSaving chunks...")
    with open('izu_chunks.pkl', 'wb') as f:
        pickle.dump(chunks, f)
    size_mb = os.path.getsize('izu_chunks.pkl') / (1024*1024)
    print(f"✓ Saved: izu_chunks.pkl ({size_mb:.2f} MB)")
    
    # Save embeddings
    print("\nSaving embeddings...")
    np.save('izu_embeddings.npy', embeddings)
    size_mb = os.path.getsize('izu_embeddings.npy') / (1024*1024)
    print(f"✓ Saved: izu_embeddings.npy ({size_mb:.2f} MB)")
    
    # Save splits separately for easy access
    print("\nSaving splits...")
    for split_name, split_data in splits.items():
        # Save chunks
        filename = f'izu_chunks_{split_name}.pkl'
        with open(filename, 'wb') as f:
            pickle.dump(split_data['chunks'], f)
        
        # Save embeddings
        filename = f'izu_embeddings_{split_name}.npy'
        np.save(filename, split_data['embeddings'])
        
        print(f"✓ Saved: {split_name} split ({len(split_data['chunks'])} chunks)")
    
    # Save metadata
    print("\nSaving metadata...")
    metadata = {
        'total_chunks': len(chunks),
        'embedding_dimension': embeddings.shape[1],
        'splits': {
            name: {
                'num_chunks': len(data['chunks']),
                'percentage': data['percentage']
            }
            for name, data in splits.items()
        }
    }
    
    with open('izu_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Saved: izu_metadata.json")
    
    print("\n" + "="*80)
    print("ALL FILES SAVED SUCCESSFULLY!")
    print("="*80)
    print("\nGenerated files:")
    print("  1. izu_chunks.pkl - All chunks")
    print("  2. izu_embeddings.npy - All embeddings")
    print("  3. izu_chunks_small.pkl - 40% chunks")
    print("  4. izu_embeddings_small.npy - 40% embeddings")
    print("  5. izu_chunks_medium.pkl - 60% chunks")
    print("  6. izu_embeddings_medium.npy - 60% embeddings")
    print("  7. izu_chunks_large.pkl - 100% chunks")
    print("  8. izu_embeddings_large.npy - 100% embeddings")
    print("  9. izu_metadata.json - Dataset information")
    print("\n✓ You can now proceed to Phase 2 (experiments)")


def main():
    """Run the complete data preparation pipeline"""
    print("\n" + "="*80)
    print("IZU RAG SYSTEM - PHASE 1: DATA PREPARATION")
    print("="*80)
    print("\nThis will prepare your data for all experiments.")
    print("You only need to run this ONCE.")
    print("\nEstimated time: 5-15 minutes (depending on dataset size)")
    print("="*80)
    
    # Check if already processed
    if os.path.exists('izu_chunks.pkl') and os.path.exists('izu_embeddings.npy'):
        response = input("\n⚠️  Processed files already exist. Re-process? (y/n): ")
        if response.lower() != 'y':
            print("Skipping preparation. Using existing files.")
            return
    
    try:
        # Step 1: Load dataset (NEW: using merged chunks)
        documents = step1_load_dataset('/home/zeynkash/projects/izu_scraper/chunking/chunks.json')
        if documents is None:
            return
        
        # Step 2: Create chunks
        chunks = step2_create_chunks(documents)
        
        # Step 3: Generate embeddings
        embeddings = step3_generate_embeddings(chunks)
        
        # Step 4: Create splits
        splits = step4_create_splits(chunks, embeddings)
        
        # Step 5: Save everything
        step5_save_everything(chunks, embeddings, splits)
        
        print("\n" + "="*80)
        print("🎉 PHASE 1 COMPLETE!")
        print("="*80)
        print("\nYour data is ready for experiments!")
        print("Next: Run the experiment script to test all configurations")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nIf you need help, share this error message.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
