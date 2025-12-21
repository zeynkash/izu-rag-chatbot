#!/usr/bin/env python3
"""
Generate Comprehensive Evaluation Report
Creates a detailed markdown report from evaluation results
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import os
import glob

def find_latest_results():
    """Find the most recent evaluation results file"""
    csv_files = glob.glob('evaluation_results_*.csv')
    json_files = glob.glob('evaluation_results_*.json')
    
    if csv_files:
        # Get most recent CSV
        latest_csv = max(csv_files, key=os.path.getctime)
        return latest_csv, 'csv'
    elif json_files:
        latest_json = max(json_files, key=os.path.getctime)
        return latest_json, 'json'
    else:
        return None, None

def load_results(filename, file_type):
    """Load evaluation results"""
    if file_type == 'csv':
        return pd.read_csv(filename)
    elif file_type == 'json':
        return pd.read_json(filename)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def generate_report(df, output_file='EVALUATION_REPORT.md'):
    """Generate comprehensive markdown report"""
    
    report = []
    
    # Header
    report.append("# RAG System Evaluation Report")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n**Total Questions Evaluated**: {len(df)}")
    report.append("\n---\n")
    
    # Executive Summary
    report.append("## Executive Summary\n")
    
    avg_similarity = df['semantic_similarity'].mean()
    avg_time = df['total_time_ms'].mean()
    avg_cost = df['cost_usd'].mean()
    total_cost = df['cost_usd'].sum()
    
    # Status determination
    if avg_similarity >= 0.65:
        status = "✅ **EXCELLENT** - System exceeds quality targets"
        status_emoji = "🟢"
    elif avg_similarity >= 0.55:
        status = "✓ **GOOD** - System meets minimum quality standards"
        status_emoji = "🟡"
    else:
        status = "⚠️ **NEEDS IMPROVEMENT** - Below quality targets"
        status_emoji = "🔴"
    
    report.append(f"**Overall Status**: {status}\n")
    report.append(f"\n### Key Metrics\n")
    report.append(f"- **Answer Quality** (Semantic Similarity): {avg_similarity:.3f} {status_emoji}")
    report.append(f"- **Average Response Time**: {avg_time:.0f}ms ({avg_time/1000:.2f}s)")
    report.append(f"- **Cost per Question**: ${avg_cost:.4f}")
    report.append(f"- **Total Evaluation Cost**: ${total_cost:.2f}")
    
    # Performance vs Targets
    report.append(f"\n### Performance vs Targets\n")
    report.append("| Metric | Target | Actual | Status |")
    report.append("|--------|--------|--------|--------|")
    
    # Similarity
    sim_status = "✅" if avg_similarity >= 0.60 else "⚠️"
    report.append(f"| Semantic Similarity | ≥0.60 | {avg_similarity:.3f} | {sim_status} |")
    
    # Response time
    time_status = "✅" if avg_time < 3000 else "⚠️" if avg_time < 5000 else "❌"
    report.append(f"| Response Time | <3000ms | {avg_time:.0f}ms | {time_status} |")
    
    # Cost
    cost_status = "✅" if avg_cost < 0.01 else "⚠️"
    report.append(f"| Cost per Question | <$0.01 | ${avg_cost:.4f} | {cost_status} |")
    
    report.append("\n---\n")
    
    # Detailed Metrics
    report.append("## 1. Answer Quality Metrics\n")
    
    report.append("### Semantic Similarity Analysis\n")
    report.append(f"- **Mean**: {df['semantic_similarity'].mean():.3f}")
    report.append(f"- **Median**: {df['semantic_similarity'].median():.3f}")
    report.append(f"- **Std Dev**: {df['semantic_similarity'].std():.3f}")
    report.append(f"- **Min**: {df['semantic_similarity'].min():.3f}")
    report.append(f"- **Max**: {df['semantic_similarity'].max():.3f}")
    
    # Quality distribution
    excellent = len(df[df['semantic_similarity'] >= 0.70])
    good = len(df[(df['semantic_similarity'] >= 0.60) & (df['semantic_similarity'] < 0.70)])
    acceptable = len(df[(df['semantic_similarity'] >= 0.50) & (df['semantic_similarity'] < 0.60)])
    poor = len(df[df['semantic_similarity'] < 0.50])
    
    report.append(f"\n### Quality Distribution\n")
    report.append(f"- **Excellent (≥0.70)**: {excellent} questions ({excellent/len(df)*100:.1f}%)")
    report.append(f"- **Good (0.60-0.69)**: {good} questions ({good/len(df)*100:.1f}%)")
    report.append(f"- **Acceptable (0.50-0.59)**: {acceptable} questions ({acceptable/len(df)*100:.1f}%)")
    report.append(f"- **Poor (<0.50)**: {poor} questions ({poor/len(df)*100:.1f}%)")
    
    # Retrieval Quality
    report.append(f"\n### Retrieval Quality\n")
    if 'url_coverage' in df.columns:
        report.append(f"- **URL Coverage**: {df['url_coverage'].mean():.1%}")
    if 'topic_coverage' in df.columns:
        report.append(f"- **Topic Coverage**: {df['topic_coverage'].mean():.1%}")
    if 'avg_relevance_score' in df.columns:
        report.append(f"- **Avg Relevance Score**: {df['avg_relevance_score'].mean():.3f}")
    
    if 'keyword_overlap' in df.columns:
        report.append(f"\n### Keyword Overlap\n")
        report.append(f"- **Mean**: {df['keyword_overlap'].mean():.3f}")
        report.append(f"- **Median**: {df['keyword_overlap'].median():.3f}")
    
    report.append("\n---\n")
    
    # Performance Metrics
    report.append("## 2. Performance Metrics\n")
    
    report.append("### Response Time Analysis\n")
    report.append(f"- **Mean Total Time**: {df['total_time_ms'].mean():.0f}ms")
    report.append(f"- **Median**: {df['total_time_ms'].median():.0f}ms")
    report.append(f"- **95th Percentile**: {df['total_time_ms'].quantile(0.95):.0f}ms")
    report.append(f"- **Fastest**: {df['total_time_ms'].min():.0f}ms")
    report.append(f"- **Slowest**: {df['total_time_ms'].max():.0f}ms")
    
    if 'retrieval_time_ms' in df.columns and 'generation_time_ms' in df.columns:
        report.append(f"\n### Time Breakdown\n")
        report.append(f"- **Avg Retrieval Time**: {df['retrieval_time_ms'].mean():.0f}ms ({df['retrieval_time_ms'].mean()/df['total_time_ms'].mean()*100:.1f}%)")
        report.append(f"- **Avg Generation Time**: {df['generation_time_ms'].mean():.0f}ms ({df['generation_time_ms'].mean()/df['total_time_ms'].mean()*100:.1f}%)")
    
    # Throughput
    avg_time_sec = df['total_time_ms'].mean() / 1000
    throughput_per_min = 60 / avg_time_sec if avg_time_sec > 0 else 0
    throughput_per_hour = throughput_per_min * 60
    
    report.append(f"\n### Throughput\n")
    report.append(f"- **Questions per Minute**: {throughput_per_min:.1f}")
    report.append(f"- **Questions per Hour**: {throughput_per_hour:.0f}")
    report.append(f"- **Estimated Daily Capacity**: {throughput_per_hour * 24:.0f} questions")
    
    report.append("\n---\n")
    
    # Cost Analysis
    report.append("## 3. Cost Analysis\n")
    
    report.append("### Per Question Costs\n")
    report.append(f"- **Mean**: ${df['cost_usd'].mean():.4f}")
    report.append(f"- **Median**: ${df['cost_usd'].median():.4f}")
    report.append(f"- **Min**: ${df['cost_usd'].min():.4f}")
    report.append(f"- **Max**: ${df['cost_usd'].max():.4f}")
    
    if 'tokens_used' in df.columns:
        report.append(f"\n### Token Usage\n")
        report.append(f"- **Average Tokens**: {df['tokens_used'].mean():.0f}")
        report.append(f"- **Total Tokens**: {df['tokens_used'].sum():,}")
        report.append(f"- **Max Tokens**: {df['tokens_used'].max():.0f}")
        report.append(f"- **Min Tokens**: {df['tokens_used'].min():.0f}")
    
    report.append(f"\n### Projected Costs\n")
    report.append(f"- **100 questions**: ${avg_cost * 100:.2f}")
    report.append(f"- **1,000 questions**: ${avg_cost * 1000:.2f}")
    report.append(f"- **10,000 questions**: ${avg_cost * 10000:.2f}")
    report.append(f"- **100,000 questions**: ${avg_cost * 100000:.2f}")
    report.append(f"- **1M questions/month**: ${avg_cost * 1000000:.2f}")
    
    report.append("\n---\n")
    
    # Performance by Category
    if 'category' in df.columns:
        report.append("## 4. Performance by Category\n")
        
        category_stats = df.groupby('category').agg({
            'semantic_similarity': ['mean', 'std', 'count'],
            'total_time_ms': 'mean',
            'cost_usd': 'mean'
        }).round(3)
        
        report.append("\n| Category | Avg Similarity | Std Dev | Questions | Avg Time (ms) | Avg Cost |")
        report.append("|----------|----------------|---------|-----------|---------------|----------|")
        
        for cat in category_stats.index:
            sim = category_stats.loc[cat, ('semantic_similarity', 'mean')]
            std = category_stats.loc[cat, ('semantic_similarity', 'std')]
            count = int(category_stats.loc[cat, ('semantic_similarity', 'count')])
            time = category_stats.loc[cat, ('total_time_ms', 'mean')]
            cost = category_stats.loc[cat, ('cost_usd', 'mean')]
            
            report.append(f"| {cat} | {sim:.3f} | {std:.3f} | {count} | {time:.0f} | ${cost:.4f} |")
        
        # Best and worst categories
        best_cat = df.groupby('category')['semantic_similarity'].mean().idxmax()
        worst_cat = df.groupby('category')['semantic_similarity'].mean().idxmin()
        best_score = df.groupby('category')['semantic_similarity'].mean().max()
        worst_score = df.groupby('category')['semantic_similarity'].mean().min()
        
        report.append(f"\n### Category Insights\n")
        report.append(f"- **Best Performing**: {best_cat} ({best_score:.3f})")
        report.append(f"- **Needs Improvement**: {worst_cat} ({worst_score:.3f})")
    
    # Performance by Difficulty
    if 'difficulty' in df.columns:
        report.append("\n## 5. Performance by Difficulty\n")
        
        difficulty_stats = df.groupby('difficulty').agg({
            'semantic_similarity': 'mean',
            'keyword_overlap': 'mean' if 'keyword_overlap' in df.columns else lambda x: 0,
            'total_time_ms': 'mean'
        }).round(3)
        
        report.append("\n| Difficulty | Avg Similarity | Avg Time (ms) |")
        report.append("|------------|----------------|---------------|")
        
        for diff in ['easy', 'medium', 'hard']:
            if diff in difficulty_stats.index:
                sim = difficulty_stats.loc[diff, 'semantic_similarity']
                time = difficulty_stats.loc[diff, 'total_time_ms']
                report.append(f"| {diff.capitalize()} | {sim:.3f} | {time:.0f} |")
    
    report.append("\n---\n")
    
    # Best and Worst Examples
    report.append("## 6. Sample Results\n")
    
    # Best result
    best_idx = df['semantic_similarity'].idxmax()
    report.append("### Best Result\n")
    report.append(f"- **Question**: {df.loc[best_idx, 'question']}")
    report.append(f"- **Similarity**: {df.loc[best_idx, 'semantic_similarity']:.3f}")
    if 'category' in df.columns:
        report.append(f"- **Category**: {df.loc[best_idx, 'category']}")
    report.append(f"- **Response Time**: {df.loc[best_idx, 'total_time_ms']:.0f}ms")
    if 'answer' in df.columns:
        answer = df.loc[best_idx, 'answer']
        report.append(f"- **Answer**: {answer[:200]}...")
    
    # Worst result
    worst_idx = df['semantic_similarity'].idxmin()
    report.append("\n### Worst Result\n")
    report.append(f"- **Question**: {df.loc[worst_idx, 'question']}")
    report.append(f"- **Similarity**: {df.loc[worst_idx, 'semantic_similarity']:.3f}")
    if 'category' in df.columns:
        report.append(f"- **Category**: {df.loc[worst_idx, 'category']}")
    report.append(f"- **Response Time**: {df.loc[worst_idx, 'total_time_ms']:.0f}ms")
    if 'answer' in df.columns:
        answer = df.loc[worst_idx, 'answer']
        report.append(f"- **Answer**: {answer[:200]}...")
    if 'ground_truth' in df.columns:
        gt = df.loc[worst_idx, 'ground_truth']
        report.append(f"- **Expected**: {gt[:200]}...")
    
    report.append("\n---\n")
    
    # Recommendations
    report.append("## 7. Recommendations\n")
    
    report.append("### Strengths\n")
    if avg_time < 3000:
        report.append("- ✅ Excellent response time (<3s)")
    if avg_cost < 0.005:
        report.append("- ✅ Very cost-efficient")
    if avg_similarity >= 0.65:
        report.append("- ✅ High answer quality")
    
    report.append("\n### Areas for Improvement\n")
    improvement_count = 1
    
    if avg_similarity < 0.60:
        report.append(f"{improvement_count}. **Improve answer quality** - Current similarity {avg_similarity:.3f} is below target (0.60)")
        report.append(f"   - Review lowest-scoring categories: {worst_cat}")
        report.append(f"   - Consider re-crawling or adding more context")
        improvement_count += 1
    
    if avg_time >= 3000:
        report.append(f"{improvement_count}. **Optimize response time** - Current {avg_time:.0f}ms exceeds 3000ms target")
        report.append(f"   - Consider reducing max_tokens from 500")
        report.append(f"   - Optimize retrieval process")
        improvement_count += 1
    
    if 'url_coverage' in df.columns and df['url_coverage'].mean() < 0.15:
        report.append(f"{improvement_count}. **Improve retrieval coverage** - Only {df['url_coverage'].mean():.1%} URL coverage")
        report.append(f"   - Review chunking strategy")
        report.append(f"   - Add more comprehensive indexing")
        improvement_count += 1
    
    if poor > len(df) * 0.2:  # More than 20% poor results
        report.append(f"{improvement_count}. **Address poor-performing questions** - {poor} questions ({poor/len(df)*100:.1f}%) scored <0.50")
        report.append(f"   - Manually review these questions")
        report.append(f"   - Identify missing data gaps")
        improvement_count += 1
    
    report.append("\n### Next Steps\n")
    
    if avg_similarity >= 0.65 and avg_time < 5000:
        report.append("1. ✅ **System is ready for deployment**")
        report.append("2. Set up monitoring and logging")
        report.append("3. Collect real user feedback")
        report.append("4. Plan periodic re-evaluation")
    elif avg_similarity >= 0.55:
        report.append("1. Focus on improving lowest-scoring categories")
        report.append("2. Optimize performance if needed")
        report.append("3. Re-run evaluation after improvements")
        report.append("4. Consider A/B testing different configurations")
    else:
        report.append("1. 🔍 **Deep dive analysis required**")
        report.append("2. Review sample answers manually")
        report.append("3. Identify data gaps")
        report.append("4. Consider re-crawling key sections")
        report.append("5. Re-evaluate retrieval strategy")
    
    report.append("\n---\n")
    
    # System Configuration
    report.append("## 8. System Configuration\n")
    report.append(f"- **Embedding Model**: text-embedding-3-small")
    report.append(f"- **LLM Model**: gpt-4o-mini")
    report.append(f"- **Retrieval Top-K**: 5")
    report.append(f"- **Temperature**: 0.3")
    report.append(f"- **Max Tokens**: 500")
    report.append(f"- **Total Chunks**: 1,154")
    
    report.append("\n---\n")
    
    # Footer
    report.append("*Report generated automatically by RAG evaluation system*")
    
    # Write report
    report_text = '\n'.join(report)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    return output_file

def main():
    """Main function"""
    print("=" * 80)
    print("GENERATING EVALUATION REPORT")
    print("=" * 80)
    print()
    
    # Find latest results
    print("Looking for evaluation results...")
    filename, file_type = find_latest_results()
    
    if not filename:
        print("\n⚠️  No evaluation results found!")
        print("\nPlease run the evaluation first:")
        print("  1. Open evaluation.ipynb in Jupyter")
        print("  2. Run all cells")
        print("  3. Then run this script again")
        return
    
    print(f"✓ Found: {filename}")
    print()
    
    # Load results
    print("Loading results...")
    df = load_results(filename, file_type)
    print(f"✓ Loaded {len(df)} evaluation results")
    print()
    
    # Generate report
    print("Generating comprehensive report...")
    output_file = generate_report(df)
    
    print()
    print("=" * 80)
    print("REPORT GENERATION COMPLETE")
    print("=" * 80)
    print()
    print(f"✓ Report saved: {output_file}")
    print()
    print(f"Report includes:")
    print(f"  - Executive summary with status")
    print(f"  - Answer quality metrics")
    print(f"  - Performance analysis")
    print(f"  - Cost projections")
    print(f"  - Performance by category and difficulty")
    print(f"  - Sample best/worst results")
    print(f"  - Actionable recommendations")
    print()
    print(f"View the report:")
    print(f"  cat {output_file}")
    print()

if __name__ == "__main__":
    main()
