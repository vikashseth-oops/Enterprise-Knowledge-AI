from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RetrievalMetrics(BaseModel):
    recall_at_1: float = 0.0
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    recall_at_10: float = 0.0
    mrr: float = 0.0
    ndcg_at_5: float = 0.0
    hit_rate: float = 0.0
    total_queries: int = 0


class GenerationMetrics(BaseModel):
    faithfulness: float = 0.0
    answer_relevance: float = 0.0
    citation_accuracy: float = 0.0
    evaluated_samples: int = 0


class LatencyPercentiles(BaseModel):
    p50_ms: float = 0.0
    p90_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    avg_ms: float = 0.0


class BenchmarkReport(BaseModel):
    retrieval_latency: LatencyPercentiles
    e2e_latency: LatencyPercentiles
    concurrency_rps: float = 0.0
    concurrent_users: int = 1


class EvalReport(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dataset_size: int = 100
    retrieval: RetrievalMetrics
    generation: GenerationMetrics | None = None
    benchmark: BenchmarkReport
    target_met: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class EvalRunRequest(BaseModel):
    evaluate_generation: bool = Field(default=False, description="Run LLM-as-a-judge on generation (slower)")
    sample_size: int | None = Field(default=100, description="Number of queries to evaluate")
    concurrency: int = Field(default=5, description="Concurrent queries for benchmark")
