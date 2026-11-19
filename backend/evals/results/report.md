# Enterprise Knowledge AI: Evaluation & Benchmark Report

**Generated:** 2026-11-19T01:38:34.008862
**Quality Gate Status:** `PASSED (Quality Gate Met)`
**Total Evaluated Queries:** 10

---

## 1. Retrieval Accuracy Metrics

| Metric | Target | Actual Measured Value | Status |
| :--- | :--- | :--- | :--- |
| **Recall@1** | - | **100.00%** | Observed |
| **Recall@3** | - | **100.00%** | Observed |
| **Recall@5** | **>= 80.00%** | **100.00%** | **PASS** |
| **Recall@10** | - | **100.00%** | Observed |
| **MRR (Mean Reciprocal Rank)** | - | **1.0000** | Observed |
| **nDCG@5** | - | **2.2460** | Observed |
| **Hit Rate@5** | - | **100.00%** | Observed |

### Recall Curve Visualization
```
Recall@1  [##############################] 100.0%
Recall@3  [##############################] 100.0%
Recall@5  [##############################] 100.0% (Target: >=80%)
Recall@10 [##############################] 100.0%
```

---

## 2. Latency Performance Benchmarks

| Percentile | Target | Actual Latency (Retrieval) | Status |
| :--- | :--- | :--- | :--- |
| **P50 (Median)** | - | **102.76 ms** | Optimal |
| **P90** | - | **114.74 ms** | Nominal |
| **P95** | **<= 190.0 ms** | **115.69 ms** | **PASS** |
| **P99** | - | **116.46 ms** | Nominal |
| **Average** | - | **99.23 ms** | Nominal |

---

## 3. Architecture Tuning Applied
- **Dense Vector Search**: `BAAI/bge-small-en-v1.5` (384 dimensions) with Cosine distance.
- **Sparse BM25 Indexing**: Sub-word term-weight matching for precise acronyms, policy IDs, and codes.
- **Fusion**: Reciprocal Rank Fusion (RRF with k=60) combining lexical and semantic rankings.
- **Payload Indexing**: Dedicated indexes on `doc_id`, `source`, and `collection` for $O(1)$ filter resolution.
- **In-Memory Cache**: High-concurrency TTL LRU cache for query embeddings and top candidate lists.
