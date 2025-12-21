# RAG System Evaluation Report

**Generated**: 2025-12-21 13:57:23

**Total Questions Evaluated**: 50

---

## Executive Summary

**Overall Status**: ✅ **EXCELLENT** - System exceeds quality targets


### Key Metrics

- **Answer Quality** (Semantic Similarity): 0.694 🟢
- **Average Response Time**: 2690ms (2.69s)
- **Cost per Question**: $0.0005
- **Total Evaluation Cost**: $0.02

### Performance vs Targets

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Semantic Similarity | ≥0.60 | 0.694 | ✅ |
| Response Time | <3000ms | 2690ms | ✅ |
| Cost per Question | <$0.01 | $0.0005 | ✅ |

---

## 1. Answer Quality Metrics

### Semantic Similarity Analysis

- **Mean**: 0.694
- **Median**: 0.692
- **Std Dev**: 0.063
- **Min**: 0.459
- **Max**: 0.816

### Quality Distribution

- **Excellent (≥0.70)**: 22 questions (44.0%)
- **Good (0.60-0.69)**: 26 questions (52.0%)
- **Acceptable (0.50-0.59)**: 1 questions (2.0%)
- **Poor (<0.50)**: 1 questions (2.0%)

### Retrieval Quality

- **URL Coverage**: 10.0%
- **Topic Coverage**: 25.7%
- **Avg Relevance Score**: 0.378

### Keyword Overlap

- **Mean**: 0.026
- **Median**: 0.015

---

## 2. Performance Metrics

### Response Time Analysis

- **Mean Total Time**: 2690ms
- **Median**: 1976ms
- **95th Percentile**: 5967ms
- **Fastest**: 1153ms
- **Slowest**: 8684ms

### Time Breakdown

- **Avg Retrieval Time**: 360ms (13.4%)
- **Avg Generation Time**: 2330ms (86.6%)

### Throughput

- **Questions per Minute**: 22.3
- **Questions per Hour**: 1338
- **Estimated Daily Capacity**: 32116 questions

---

## 3. Cost Analysis

### Per Question Costs

- **Mean**: $0.0005
- **Median**: $0.0005
- **Min**: $0.0003
- **Max**: $0.0006

### Token Usage

- **Average Tokens**: 2785
- **Total Tokens**: 139,266
- **Max Tokens**: 3495
- **Min Tokens**: 1883

### Projected Costs

- **100 questions**: $0.05
- **1,000 questions**: $0.46
- **10,000 questions**: $4.56
- **100,000 questions**: $45.65
- **1M questions/month**: $456.47

---

## 4. Performance by Category


| Category | Avg Similarity | Std Dev | Questions | Avg Time (ms) | Avg Cost |
|----------|----------------|---------|-----------|---------------|----------|
| academic_services | 0.735 | 0.049 | 6 | 3021 | $0.0000 |
| admissions | 0.689 | 0.062 | 8 | 2294 | $0.0000 |
| campus_life | 0.696 | 0.081 | 3 | 3936 | $0.0000 |
| fees | 0.741 | 0.038 | 4 | 2265 | $0.0000 |
| financial_aid | 0.711 | 0.028 | 3 | 2149 | $0.0000 |
| general_info | 0.640 | 0.081 | 8 | 2627 | $0.0000 |
| international | 0.686 | 0.055 | 6 | 3410 | $0.0010 |
| programs | 0.695 | 0.060 | 10 | 2562 | $0.0000 |
| student_services | 0.713 | 0.032 | 2 | 1813 | $0.0000 |

### Category Insights

- **Best Performing**: fees (0.741)
- **Needs Improvement**: general_info (0.640)

## 5. Performance by Difficulty


| Difficulty | Avg Similarity | Avg Time (ms) |
|------------|----------------|---------------|
| Easy | 0.699 | 2530 |
| Medium | 0.705 | 2552 |
| Hard | 0.647 | 3593 |

---

## 6. Sample Results

### Best Result

- **Question**: Çift anadal veya yandal yapılabilir mi?
- **Similarity**: 0.816
- **Category**: programs
- **Response Time**: 2580ms
- **Answer**: Evet, İstanbul Sabahattin Zaim Üniversitesi'nde (İZÜ) çift anadal ve yandal programları yapılabilir. Bu programlara başvuru ve kabul şartlarını sağlayan öğrenciler, kontenjan dahilinde burslu olarak b...

### Worst Result

- **Question**: İZÜ hangi akreditasyonlara sahip?
- **Similarity**: 0.459
- **Category**: general_info
- **Response Time**: 4529ms
- **Answer**: İstanbul Sabahattin Zaim Üniversitesi (İZÜ) hakkında akreditasyon bilgisi verilmemiştir. Bu nedenle, İZÜ'nün sahip olduğu akreditasyonlar hakkında bilgi veremem. Daha fazla bilgi için üniversitenin re...
- **Expected**: Bilgi bulunamadı....

---

## 7. Recommendations

### Strengths

- ✅ Excellent response time (<3s)
- ✅ Very cost-efficient
- ✅ High answer quality

### Areas for Improvement

1. **Improve retrieval coverage** - Only 10.0% URL coverage
   - Review chunking strategy
   - Add more comprehensive indexing

### Next Steps

1. ✅ **System is ready for deployment**
2. Set up monitoring and logging
3. Collect real user feedback
4. Plan periodic re-evaluation

---

## 8. System Configuration

- **Embedding Model**: text-embedding-3-small
- **LLM Model**: gpt-4o-mini
- **Retrieval Top-K**: 5
- **Temperature**: 0.3
- **Max Tokens**: 500
- **Total Chunks**: 1,154

---

*Report generated automatically by RAG evaluation system*