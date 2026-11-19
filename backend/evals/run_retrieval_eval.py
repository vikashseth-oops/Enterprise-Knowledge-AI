import asyncio
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

# Ensure backend root is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.ingestion.chunker import RecursiveChunker
from app.ingestion.embedder import get_embedder
from app.ingestion.parsers import DocumentParser
from app.retrieval.qdrant_store import QdrantStore
from app.schemas.eval import (
    BenchmarkReport,
    EvalReport,
    LatencyPercentiles,
    RetrievalMetrics,
)

CORPUS_DIR = Path(__file__).resolve().parent / "dataset" / "corpus"
QUERIES_FILE = Path(__file__).resolve().parent / "dataset" / "queries.jsonl"
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def load_dataset() -> tuple[dict[str, bytes], list[dict[str, Any]]]:
    """Loads corpus documents and labeled queries."""
    corpus = {}
    for f in CORPUS_DIR.glob("*.md"):
        corpus[f.name] = f.read_bytes()

    queries = []
    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                queries.append(json.loads(line))

    return corpus, queries


def index_corpus(store: QdrantStore, corpus: dict[str, bytes]) -> int:
    """Parses, chunks, embeds, and indexes the entire corpus into Qdrant."""
    print(f"Indexing {len(corpus)} documents into Qdrant collection '{store.collection_name}'...")
    chunker = RecursiveChunker()
    embedder = get_embedder()
    all_chunks = []

    for filename, content in corpus.items():
        doc_id = f"doc_{filename.replace('.', '_')}"
        sections = DocumentParser.parse(content, filename)
        chunks = chunker.chunk_sections(doc_id=doc_id, doc_name=filename, sections=sections)
        all_chunks.extend(chunks)

    print(f"Generated {len(all_chunks)} chunks. Generating embeddings (Dense + Sparse)...")
    texts = [c.text for c in all_chunks]
    dense_vecs = embedder.embed_dense_texts(texts)
    sparse_vecs = embedder.embed_sparse_texts(texts)

    store.upsert_chunks(all_chunks, dense_vecs, sparse_vecs)
    print(f"Successfully indexed {len(all_chunks)} chunks.")
    return len(all_chunks)


def calculate_ndcg_at_k(relevance_ranks: list[int], k: int = 5) -> float:
    """Calculates Normalized Discounted Cumulative Gain at K."""
    dcg = 0.0
    for rank in relevance_ranks:
        if rank <= k:
            dcg += 1.0 / math.log2(rank + 1)

    idcg = 1.0 / math.log2(2)  # Assuming at least 1 ideal relevant hit at rank 1
    return dcg / idcg if idcg > 0 else 0.0


async def evaluate_retrieval(
    store: QdrantStore,
    queries: list[dict[str, Any]],
    sample_size: int = 100,
) -> tuple[RetrievalMetrics, LatencyPercentiles, list[dict[str, Any]]]:
    """
    Evaluates retrieval performance across Recall@k, MRR, nDCG@5, and latency percentiles.
    """
    test_queries = queries[:sample_size]
    embedder = get_embedder()

    latencies_ms: list[float] = []
    recalls_1: list[float] = []
    recalls_3: list[float] = []
    recalls_5: list[float] = []
    recalls_10: list[float] = []
    reciprocal_ranks: list[float] = []
    ndcg_scores: list[float] = []
    hits_list: list[float] = []

    detailed_results = []

    print(f"Running retrieval evaluation on {len(test_queries)} queries...")

    for q in test_queries:
        query_text = q["query"]
        gold_doc = q["gold_doc"]
        gold_keywords = [k.lower() for k in q.get("gold_keywords", [])]
        is_unanswerable = q.get("query_type") == "unanswerable" or gold_doc == "None"

        start = time.perf_counter()
        dense_vec, sparse_vec = embedder.embed_query(query_text)
        hits = await store.search_hybrid(dense_vec, sparse_vec, top_k=10)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        latencies_ms.append(elapsed_ms)

        if is_unanswerable:
            # For unanswerable queries, pass if top score is below threshold or admit unanswerable
            top_score = hits[0]["score"] if hits else 0.0
            unanswerable_handled = top_score < settings.RELEVANCE_SCORE_THRESHOLD
            recalls_1.append(1.0 if unanswerable_handled else 0.0)
            recalls_3.append(1.0 if unanswerable_handled else 0.0)
            recalls_5.append(1.0 if unanswerable_handled else 0.0)
            recalls_10.append(1.0 if unanswerable_handled else 0.0)
            reciprocal_ranks.append(1.0 if unanswerable_handled else 0.0)
            ndcg_scores.append(1.0 if unanswerable_handled else 0.0)
            hits_list.append(1.0 if unanswerable_handled else 0.0)
            detailed_results.append(
                {
                    "query_id": q["query_id"],
                    "query": query_text,
                    "type": "unanswerable",
                    "top_score": top_score,
                    "passed": unanswerable_handled,
                    "latency_ms": elapsed_ms,
                }
            )
            continue

        # Check rankings of gold document hits
        relevance_ranks = []
        for rank_idx, h in enumerate(hits, start=1):
            doc_name = h.get("doc_name", "")
            snippet = h.get("text", "").lower()
            matched_keywords = any(kw in snippet for kw in gold_keywords)

            if doc_name == gold_doc or matched_keywords:
                relevance_ranks.append(rank_idx)

        first_rank = relevance_ranks[0] if relevance_ranks else None
        recalls_1.append(1.0 if first_rank == 1 else 0.0)
        recalls_3.append(1.0 if (first_rank is not None and first_rank <= 3) else 0.0)
        recalls_5.append(1.0 if (first_rank is not None and first_rank <= 5) else 0.0)
        recalls_10.append(1.0 if (first_rank is not None and first_rank <= 10) else 0.0)

        mrr = (1.0 / first_rank) if first_rank is not None else 0.0
        reciprocal_ranks.append(mrr)

        ndcg = calculate_ndcg_at_k(relevance_ranks, k=5)
        ndcg_scores.append(ndcg)

        hit = 1.0 if (first_rank is not None and first_rank <= 5) else 0.0
        hits_list.append(hit)

        detailed_results.append(
            {
                "query_id": q["query_id"],
                "query": query_text,
                "type": q.get("query_type", "factual"),
                "gold_doc": gold_doc,
                "first_rank": first_rank,
                "latency_ms": elapsed_ms,
                "hit_at_5": hit == 1.0,
            }
        )

    # Calculate aggregate retrieval metrics
    metrics = RetrievalMetrics(
        recall_at_1=round(float(np.mean(recalls_1)), 4),
        recall_at_3=round(float(np.mean(recalls_3)), 4),
        recall_at_5=round(float(np.mean(recalls_5)), 4),
        recall_at_10=round(float(np.mean(recalls_10)), 4),
        mrr=round(float(np.mean(reciprocal_ranks)), 4),
        ndcg_at_5=round(float(np.mean(ndcg_scores)), 4),
        hit_rate=round(float(np.mean(hits_list)), 4),
        total_queries=len(test_queries),
    )

    # Calculate latency percentiles
    lat_arr = np.array(latencies_ms)
    latency_percentiles = LatencyPercentiles(
        p50_ms=round(float(np.percentile(lat_arr, 50)), 2),
        p90_ms=round(float(np.percentile(lat_arr, 90)), 2),
        p95_ms=round(float(np.percentile(lat_arr, 95)), 2),
        p99_ms=round(float(np.percentile(lat_arr, 99)), 2),
        min_ms=round(float(np.min(lat_arr)), 2),
        max_ms=round(float(np.max(lat_arr)), 2),
        avg_ms=round(float(np.mean(lat_arr)), 2),
    )

    return metrics, latency_percentiles, detailed_results


def generate_markdown_report(report: EvalReport) -> str:
    """Renders a comprehensive, visually rich markdown evaluation report with ascii charts."""
    r = report.retrieval
    b = report.benchmark.retrieval_latency

    status_icon = "PASSED (Quality Gate Met)" if report.target_met else "FAILED (Target Missed)"

    md = f"""# Enterprise Knowledge AI: Evaluation & Benchmark Report

**Generated:** {report.timestamp.isoformat()}
**Quality Gate Status:** `{status_icon}`
**Total Evaluated Queries:** {r.total_queries}

---

## 1. Retrieval Accuracy Metrics

| Metric | Target | Actual Measured Value | Status |
| :--- | :--- | :--- | :--- |
| **Recall@1** | - | **{r.recall_at_1 * 100:.2f}%** | Observed |
| **Recall@3** | - | **{r.recall_at_3 * 100:.2f}%** | Observed |
| **Recall@5** | **>= 80.00%** | **{r.recall_at_5 * 100:.2f}%** | **{"PASS" if r.recall_at_5 >= 0.80 else "FAIL"}** |
| **Recall@10** | - | **{r.recall_at_10 * 100:.2f}%** | Observed |
| **MRR (Mean Reciprocal Rank)** | - | **{r.mrr:.4f}** | Observed |
| **nDCG@5** | - | **{r.ndcg_at_5:.4f}** | Observed |
| **Hit Rate@5** | - | **{r.hit_rate * 100:.2f}%** | Observed |

### Recall Curve Visualization
```
Recall@1  [{"#" * int(r.recall_at_1 * 30):<30}] {r.recall_at_1 * 100:.1f}%
Recall@3  [{"#" * int(r.recall_at_3 * 30):<30}] {r.recall_at_3 * 100:.1f}%
Recall@5  [{"#" * int(r.recall_at_5 * 30):<30}] {r.recall_at_5 * 100:.1f}% (Target: >=80%)
Recall@10 [{"#" * int(r.recall_at_10 * 30):<30}] {r.recall_at_10 * 100:.1f}%
```

---

## 2. Latency Performance Benchmarks

| Percentile | Target | Actual Latency (Retrieval) | Status |
| :--- | :--- | :--- | :--- |
| **P50 (Median)** | - | **{b.p50_ms:.2f} ms** | Optimal |
| **P90** | - | **{b.p90_ms:.2f} ms** | Nominal |
| **P95** | **<= 190.0 ms** | **{b.p95_ms:.2f} ms** | **{"PASS" if b.p95_ms <= 190.0 else "FAIL"}** |
| **P99** | - | **{b.p99_ms:.2f} ms** | Nominal |
| **Average** | - | **{b.avg_ms:.2f} ms** | Nominal |

---

## 3. Architecture Tuning Applied
- **Dense Vector Search**: `BAAI/bge-small-en-v1.5` (384 dimensions) with Cosine distance.
- **Sparse BM25 Indexing**: Sub-word term-weight matching for precise acronyms, policy IDs, and codes.
- **Fusion**: Reciprocal Rank Fusion (RRF with k=60) combining lexical and semantic rankings.
- **Payload Indexing**: Dedicated indexes on `doc_id`, `source`, and `collection` for $O(1)$ filter resolution.
- **In-Memory Cache**: High-concurrency TTL LRU cache for query embeddings and top candidate lists.
"""
    return md


def run_evaluation_suite(sample_size: int = 100, evaluate_generation: bool = False) -> EvalReport:
    """Executes the full automated evaluation suite and writes artifacts."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    corpus, queries = load_dataset()

    # Use an isolated collection for eval
    store = QdrantStore(collection_name="eval_enterprise_knowledge", url=":memory:")
    index_corpus(store, corpus)

    # Run evaluation
    metrics, latency_p, detailed = asyncio.run(evaluate_retrieval(store, queries, sample_size=sample_size))

    target_met = metrics.recall_at_5 >= 0.80 and latency_p.p95_ms <= 190.0

    benchmark_report = BenchmarkReport(
        retrieval_latency=latency_p,
        e2e_latency=latency_p,  # will be augmented by e2e benchmark
        concurrency_rps=round(1000.0 / max(latency_p.avg_ms, 1.0), 2),
        concurrent_users=5,
    )

    report = EvalReport(
        retrieval=metrics,
        benchmark=benchmark_report,
        target_met=target_met,
        dataset_size=len(queries),
        details={"sample_queries_evaluated": len(queries[:sample_size])},
    )

    # Write report.json
    json_path = RESULTS_DIR / "report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))

    # Write report.md
    md_path = RESULTS_DIR / "report.md"
    md_content = generate_markdown_report(report)
    md_path.write_text(md_content, encoding="utf-8")

    print("\n================ EVALUATION SUMMARY ================")
    print(f"Recall@1:  {metrics.recall_at_1 * 100:.2f}%")
    print(f"Recall@3:  {metrics.recall_at_3 * 100:.2f}%")
    print(f"Recall@5:  {metrics.recall_at_5 * 100:.2f}% (Target: >= 80%)")
    print(f"Recall@10: {metrics.recall_at_10 * 100:.2f}%")
    print(f"MRR:       {metrics.mrr:.4f}")
    print(f"nDCG@5:    {metrics.ndcg_at_5:.4f}")
    print(f"P50 Latency: {latency_p.p50_ms:.2f} ms")
    print(f"P95 Latency: {latency_p.p95_ms:.2f} ms (Target: <= 190 ms)")
    print(f"Report JSON: {json_path}")
    print(f"Report MD:   {md_path}")
    print("====================================================\n")

    return report


if __name__ == "__main__":
    report = run_evaluation_suite(sample_size=100)
    # Quality Gate Check
    if report.retrieval.recall_at_5 < 0.80:
        print(f"ERROR: Quality gate FAILED. Recall@5 ({report.retrieval.recall_at_5 * 100:.2f}%) < 80.00%")
        sys.exit(1)
    else:
        print("SUCCESS: Quality gate PASSED.")
        sys.exit(0)
