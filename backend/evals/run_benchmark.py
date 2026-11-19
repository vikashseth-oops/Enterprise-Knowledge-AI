import asyncio
import json
import sys
import time
from pathlib import Path

import numpy as np

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ingestion.embedder import get_embedder
from app.retrieval.qdrant_store import QdrantStore

QUERIES_FILE = Path(__file__).resolve().parent / "dataset" / "queries.jsonl"
BENCHMARK_RESULTS_FILE = Path(__file__).resolve().parent / "results" / "benchmark.json"


async def worker(store: QdrantStore, queries: list[str], latencies: list[float], num_requests: int):
    embedder = get_embedder()
    for i in range(num_requests):
        q = queries[i % len(queries)]
        start = time.perf_counter()
        dense_vec, sparse_vec = embedder.embed_query(q)
        await store.search_hybrid(dense_vec, sparse_vec, top_k=5)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        latencies.append(elapsed_ms)


async def run_benchmark(concurrency: int = 5, total_requests: int = 100):
    print(f"Starting benchmark: concurrency={concurrency}, total_requests={total_requests}...")
    queries = []
    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                queries.append(json.loads(line)["query"])

    store = QdrantStore(collection_name="eval_enterprise_knowledge")
    store.ensure_collection()

    reqs_per_worker = total_requests // concurrency
    all_latencies: list[float] = []
    tasks = []

    start_wall = time.perf_counter()
    for _ in range(concurrency):
        w_latencies: list[float] = []
        all_latencies.append(w_latencies)
        tasks.append(worker(store, queries, w_latencies, reqs_per_worker))

    await asyncio.gather(*tasks)
    total_time = time.perf_counter() - start_wall

    flat_latencies = [lat for sub in all_latencies for lat in sub]
    lat_arr = np.array(flat_latencies)

    rps = len(flat_latencies) / total_time
    p50 = float(np.percentile(lat_arr, 50))
    p90 = float(np.percentile(lat_arr, 90))
    p95 = float(np.percentile(lat_arr, 95))
    p99 = float(np.percentile(lat_arr, 99))
    avg = float(np.mean(lat_arr))

    results = {
        "concurrency": concurrency,
        "total_requests": len(flat_latencies),
        "total_duration_seconds": round(total_time, 2),
        "throughput_rps": round(rps, 2),
        "latency_ms": {
            "p50": round(p50, 2),
            "p90": round(p90, 2),
            "p95": round(p95, 2),
            "p99": round(p99, 2),
            "avg": round(avg, 2),
        },
    }

    BENCHMARK_RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BENCHMARK_RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n========= BENCHMARK RESULTS =========")
    print(f"Throughput:  {rps:.2f} RPS")
    print(f"P50 Latency: {p50:.2f} ms")
    print(f"P95 Latency: {p95:.2f} ms (Target: <= 190 ms)")
    print(f"P99 Latency: {p99:.2f} ms")
    print(f"Average:     {avg:.2f} ms")
    print(f"Results saved to: {BENCHMARK_RESULTS_FILE}")
    print("=====================================\n")
    return results


if __name__ == "__main__":
    asyncio.run(run_benchmark(concurrency=5, total_requests=100))
