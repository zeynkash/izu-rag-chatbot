"""
PHASE 2: RUNNING ALL RAG EXPERIMENTS
Tests: 3 dataset sizes × 3 metrics × 3 indexing methods = 27 configurations
With BGE Reranker
"""

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from FlagEmbedding import FlagReranker
import faiss
import time
import pickle
import os
from typing import List, Dict
from tqdm import tqdm

class RAGExperimentRunner:
    def __init__(self):
        """Initialize experiment runner"""
        print("\n" + "="*80)
        print("INITIALIZING EXPERIMENT RUNNER")
        print("="*80)
        
        # Load models
        print("\n1. Loading embedding model...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("   ✓ Embedding model loaded")
        
        print("\n2. Loading BGE reranker...")
        self.reranker = FlagReranker('BAAI/bge-reranker-base', use_fp16=True)
        print("   ✓ BGE reranker loaded")
        
        # Test queries - you can modify these!
        self.test_queries = [
            "What are the tuition fees for international students?",
            "Which faculties and departments does IZU have?",
            "What is the admission and application process?",
            "Tell me about graduate and master programs",
            "What scholarship opportunities are available?",
            "How do I apply for undergraduate programs?",
            "What are the language requirements?",
            "Tell me about campus facilities and student life"
        ]
        
        print(f"\n3. Test queries: {len(self.test_queries)} queries loaded")
        print("   ✓ Ready to run experiments!")
    
    def load_dataset_split(self, split_name):
        """Load a specific dataset split"""
        chunks_file = f'izu_chunks_{split_name}.pkl'
        embeddings_file = f'izu_embeddings_{split_name}.npy'
        
        if not os.path.exists(chunks_file) or not os.path.exists(embeddings_file):
            raise FileNotFoundError(f"Missing files for {split_name} split. Run Phase 1 first!")
        
        with open(chunks_file, 'rb') as f:
            chunks = pickle.load(f)
        
        embeddings = np.load(embeddings_file)
        
        return chunks, embeddings
    
    def build_hnsw_index(self, embeddings, metric):
        """Build FAISS HNSW index"""
        d = embeddings.shape[1]
        embeddings_copy = embeddings.copy().astype('float32')
        
        if metric == 'cosine':
            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings_copy)
            index = faiss.IndexHNSWFlat(d, 32)
        elif metric == 'euclidean':
            index = faiss.IndexHNSWFlat(d, 32, faiss.METRIC_L2)
        elif metric == 'inner':
            index = faiss.IndexHNSWFlat(d, 32, faiss.METRIC_INNER_PRODUCT)
        
        # HNSW parameters
        index.hnsw.efConstruction = 40
        index.hnsw.efSearch = 16
        
        index.add(embeddings_copy)
        return index
    
    def build_ivf_index(self, embeddings, metric):
        """Build FAISS IVF_FLAT index"""
        d = embeddings.shape[1]
        embeddings_copy = embeddings.copy().astype('float32')
        
        # Number of clusters
        nlist = min(100, max(10, len(embeddings) // 100))
        
        if metric == 'cosine':
            faiss.normalize_L2(embeddings_copy)
            quantizer = faiss.IndexFlatL2(d)
            index = faiss.IndexIVFFlat(quantizer, d, nlist)
        elif metric == 'euclidean':
            quantizer = faiss.IndexFlatL2(d)
            index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)
        elif metric == 'inner':
            quantizer = faiss.IndexFlatIP(d)
            index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_INNER_PRODUCT)
        
        # Train and add
        index.train(embeddings_copy)
        index.add(embeddings_copy)
        index.nprobe = 10
        
        return index
    
    def build_flat_index(self, embeddings, metric):
        """Build FAISS Flat index (as ScaNN alternative)"""
        d = embeddings.shape[1]
        embeddings_copy = embeddings.copy().astype('float32')
        
        if metric == 'cosine':
            faiss.normalize_L2(embeddings_copy)
            index = faiss.IndexFlatL2(d)
        elif metric == 'euclidean':
            index = faiss.IndexFlatL2(d)
        elif metric == 'inner':
            index = faiss.IndexFlatIP(d)
        
        index.add(embeddings_copy)
        return index
    
    def search(self, index, query_embedding, k, metric):
        """Search in index"""
        query_emb = query_embedding.copy().astype('float32').reshape(1, -1)
        
        if metric == 'cosine':
            faiss.normalize_L2(query_emb)
        
        distances, indices = index.search(query_emb, k)
        return distances[0], indices[0]
    
    def rerank_results(self, query, chunks, top_k=5):
        """Rerank using BGE reranker"""
        if not chunks:
            return []
        
        # Prepare pairs
        pairs = [[query, chunk['text']] for chunk in chunks]
        
        # Get scores
        scores = self.reranker.compute_score(pairs)
        
        # Handle single score
        if isinstance(scores, (int, float)):
            scores = [scores]
        
        # Sort by score
        scored = list(zip(chunks, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [chunk for chunk, score in scored[:top_k]]
    
    def run_single_configuration(self, split_name, chunks, embeddings, metric, index_method):
        """Run experiments for one configuration"""
        # Build index
        start_build = time.time()
        
        if index_method == 'hnsw':
            index = self.build_hnsw_index(embeddings, metric)
        elif index_method == 'ivf_flat':
            index = self.build_ivf_index(embeddings, metric)
        elif index_method == 'scann':
            index = self.build_flat_index(embeddings, metric)
        
        build_time = time.time() - start_build
        
        # Run queries
        query_times = []
        search_times = []
        rerank_times = []
        
        for query in self.test_queries:
            # Encode query
            query_emb = self.embedding_model.encode([query])[0]
            
            # Search
            start_search = time.time()
            distances, indices = self.search(index, query_emb, k=20, metric=metric)
            search_time = time.time() - start_search
            search_times.append(search_time)
            
            # Get chunks
            retrieved = [chunks[i] for i in indices if i < len(chunks)]
            
            # Rerank
            start_rerank = time.time()
            reranked = self.rerank_results(query, retrieved, top_k=5)
            rerank_time = time.time() - start_rerank
            rerank_times.append(rerank_time)
            
            total_time = search_time + rerank_time
            query_times.append(total_time)
        
        # Calculate metrics
        result = {
            'dataset_size': split_name,
            'num_chunks': len(chunks),
            'metric': metric,
            'index_method': index_method,
            'build_time_sec': build_time,
            'avg_search_time_ms': np.mean(search_times) * 1000,
            'avg_rerank_time_ms': np.mean(rerank_times) * 1000,
            'avg_total_time_ms': np.mean(query_times) * 1000,
            'min_query_time_ms': np.min(query_times) * 1000,
            'max_query_time_ms': np.max(query_times) * 1000,
            'reranker': 'BGE'
        }
        
        return result
    
    def run_all_experiments(self):
        """Run all 27 experiments"""
        print("\n" + "="*80)
        print("PHASE 2: RUNNING ALL EXPERIMENTS")
        print("="*80)
        print(f"\nTotal configurations: 27")
        print("  - 3 dataset sizes (small, medium, large)")
        print("  - 3 metrics (cosine, euclidean, inner)")
        print("  - 3 indexing methods (hnsw, ivf_flat, scann)")
        print("  - 1 reranker (BGE)")
        print("\nThis will take approximately 10-20 minutes...")
        print("="*80 + "\n")
        
        results = []
        
        dataset_sizes = ['small', 'medium', 'large']
        metrics = ['cosine', 'euclidean', 'inner']
        indexing_methods = ['hnsw', 'ivf_flat', 'scann']
        
        total_experiments = 27
        experiment_num = 0
        
        for split_name in dataset_sizes:
            print(f"\n{'='*80}")
            print(f"DATASET: {split_name.upper()}")
            print(f"{'='*80}")
            
            # Load data
            print(f"Loading {split_name} dataset...")
            chunks, embeddings = self.load_dataset_split(split_name)
            print(f"✓ Loaded {len(chunks)} chunks")
            
            for metric in metrics:
                print(f"\n  {'─'*70}")
                print(f"  METRIC: {metric.upper()}")
                print(f"  {'─'*70}")
                
                for index_method in indexing_methods:
                    experiment_num += 1
                    
                    print(f"\n    [{experiment_num}/27] Testing: {index_method.upper()}")
                    
                    # Run experiment
                    start = time.time()
                    result = self.run_single_configuration(
                        split_name, chunks, embeddings, metric, index_method
                    )
                    elapsed = time.time() - start
                    
                    results.append(result)
                    
                    # Display results
                    print(f"    ✓ Complete in {elapsed:.1f}s")
                    print(f"      Build time: {result['build_time_sec']:.2f}s")
                    print(f"      Avg query: {result['avg_total_time_ms']:.2f}ms")
                    print(f"        - Search: {result['avg_search_time_ms']:.2f}ms")
                    print(f"        - Rerank: {result['avg_rerank_time_ms']:.2f}ms")
        
        return results
    
    def save_results(self, results):
        """Save results to CSV and display summary"""
        print("\n" + "="*80)
        print("SAVING RESULTS")
        print("="*80)
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Save to CSV
        output_file = 'izu_rag_results_bge.csv'
        df.to_csv(output_file, index=False)
        print(f"✓ Results saved to: {output_file}")
        
        # Display summary
        print("\n" + "="*80)
        print("RESULTS SUMMARY")
        print("="*80)
        
        print("\n📊 COMPLETE RESULTS TABLE:")
        print(df.to_string(index=False))
        
        # Best configurations
        print("\n" + "="*80)
        print("🏆 BEST CONFIGURATIONS")
        print("="*80)
        
        fastest = df.loc[df['avg_total_time_ms'].idxmin()]
        print(f"\n⚡ FASTEST QUERY TIME:")
        print(f"   {fastest['dataset_size']} + {fastest['metric']} + {fastest['index_method']}")
        print(f"   {fastest['avg_total_time_ms']:.2f}ms")
        
        fastest_build = df.loc[df['build_time_sec'].idxmin()]
        print(f"\n🔨 FASTEST BUILD TIME:")
        print(f"   {fastest_build['dataset_size']} + {fastest_build['metric']} + {fastest_build['index_method']}")
        print(f"   {fastest_build['build_time_sec']:.2f}s")
        
        # Group analysis
        print("\n" + "="*80)
        print("📈 ANALYSIS BY CATEGORY")
        print("="*80)
        
        print("\n1. Average by Dataset Size:")
        by_size = df.groupby('dataset_size')['avg_total_time_ms'].mean()
        for size, time_ms in by_size.items():
            print(f"   {size}: {time_ms:.2f}ms")
        
        print("\n2. Average by Metric:")
        by_metric = df.groupby('metric')['avg_total_time_ms'].mean()
        for metric, time_ms in by_metric.items():
            print(f"   {metric}: {time_ms:.2f}ms")
        
        print("\n3. Average by Index Method:")
        by_index = df.groupby('index_method')['avg_total_time_ms'].mean()
        for method, time_ms in by_index.items():
            print(f"   {method}: {time_ms:.2f}ms")
        
        return df


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("IZU RAG SYSTEM - PHASE 2: EXPERIMENTS")
    print("Testing with BGE Reranker")
    print("="*80)
    
    # Check if Phase 1 is complete
    required_files = [
        'izu_chunks_small.pkl', 'izu_embeddings_small.npy',
        'izu_chunks_medium.pkl', 'izu_embeddings_medium.npy',
        'izu_chunks_large.pkl', 'izu_embeddings_large.npy'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print("\n❌ ERROR: Phase 1 not complete!")
        print("Missing files:")
        for f in missing:
            print(f"  - {f}")
        print("\nPlease run Phase 1 (data_preparation.py) first!")
        return
    
    print("\n✓ Phase 1 files found")
    print("\nStarting experiments...")
    
    try:
        # Initialize runner
        runner = RAGExperimentRunner()
        
        # Run all experiments
        results = runner.run_all_experiments()
        
        # Save and display results
        df = runner.save_results(results)
        
        print("\n" + "="*80)
        print("🎉 ALL EXPERIMENTS COMPLETE!")
        print("="*80)
        print(f"\n✓ Tested {len(results)} configurations")
        print(f"✓ Results saved to: izu_rag_results_bge.csv")
        print("\nYou can now:")
        print("  1. Analyze the CSV file")
        print("  2. Compare with your friend's results")
        print("  3. Create visualizations")
        print("  4. Write your report")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
