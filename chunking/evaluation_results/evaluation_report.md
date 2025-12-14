
# RAG System Evaluation Report
Generated: 2025-12-14 16:18:50

## Executive Summary

Total Questions Evaluated: 10
Test Categories: 9
Languages: Turkish, English

## 1. Performance Metrics

### Response Time
- Average Total Time: 2318ms
- Average Retrieval Time: 251ms
- Average Generation Time: 2067ms
- 95th Percentile: 3995ms

### Throughput
- Questions per Minute: 25.9
- Estimated Daily Capacity: 37272 questions

## 2. Cost Metrics

### Per Question
- Average Cost: $0.0011
- Median Cost: $0.0011
- Total Evaluation Cost: $0.0108

### Projected Costs
- 1,000 questions: $1.08
- 10,000 questions: $10.82
- 100,000 questions: $108.23

### Token Usage
- Average Tokens: 2705
- Max Tokens: 3218
- Min Tokens: 1928

## 3. Quality Metrics

### Retrieval Quality
- URL Coverage: 10.0%
- Topic Coverage: 16.7%
- Average Relevance Score: 0.558

### Answer Quality
- Keyword Overlap: 20.2%
- Semantic Similarity: 0.616
- Best Performing Category: student_services
- Worst Performing Category: general_info

## 4. Performance by Category

| category          |   semantic_similarity |   total_time_ms |   cost_usd |
|:------------------|----------------------:|----------------:|-----------:|
| academic_services |                 0.754 |         2263.81 |      0.001 |
| admissions        |                 0.646 |         4340.71 |      0.001 |
| campus_life       |                 0.675 |         1010.9  |      0.001 |
| fees              |                 0.546 |         2514.85 |      0.001 |
| financial_aid     |                 0.632 |         1503.19 |      0.001 |
| general_info      |                 0.48  |         1833.59 |      0.001 |
| international     |                 0.581 |         2497.19 |      0.001 |
| programs          |                 0.496 |         3380.74 |      0.001 |
| student_services  |                 0.77  |         1338.86 |      0.001 |

## 5. Performance by Difficulty

| difficulty   |   semantic_similarity |   keyword_overlap |   total_time_ms |
|:-------------|----------------------:|------------------:|----------------:|
| easy         |                 0.639 |             0.21  |         1421.64 |
| hard         |                 0.472 |             0.1   |         3476.26 |
| medium       |                 0.664 |             0.245 |         2635.49 |

## 6. Recommendations

### Strengths
- Response time under 3995ms for 95% of queries
- Cost-efficient at $0.0011 per question
- Good retrieval coverage at 10%

### Areas for Improvement
1. Improve performance on 'general_info' category
2. Optimize token usage to reduce costs
3. Enhance retrieval for complex multi-hop questions

### Next Steps
1. Expand test dataset to 50+ questions
2. Implement human evaluation
3. A/B test different prompt strategies
4. Monitor production metrics

## 7. System Configuration

- Embedding Model: text-embedding-3-small
- LLM Model: gpt-4o-mini
- Retrieval Top-K: 5
- Temperature: 0.3
- Max Tokens: 500

---
Report generated automatically by RAG evaluation system.
