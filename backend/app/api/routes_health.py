from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.llm.groq_client import get_groq_client
from app.retrieval.qdrant_store import get_qdrant_store

router = APIRouter(tags=["Health & Monitoring"])

# Prometheus Metrics
REQUEST_COUNTER = Counter(
    "rag_http_requests_total",
    "Total HTTP requests handled by the platform",
    ["method", "endpoint", "status_code"],
)
CHAT_LATENCY_HISTOGRAM = Histogram(
    "rag_chat_latency_seconds",
    "End-to-end chat latency in seconds",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 3.5, 5.0, 10.0],
)
RETRIEVAL_LATENCY_HISTOGRAM = Histogram(
    "rag_retrieval_latency_seconds",
    "Retrieval latency in seconds",
    buckets=[0.02, 0.05, 0.1, 0.19, 0.3, 0.5, 1.0],
)


@router.get("/healthz", status_code=status.HTTP_200_OK)
async def healthz():
    """Liveness probe for Cloud Run and Kubernetes."""
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    """Readiness probe checking Qdrant and Groq connectivity."""
    store = get_qdrant_store()
    groq = get_groq_client()

    qdrant_healthy = store.is_healthy()
    groq_ready = groq.is_configured()

    all_ready = qdrant_healthy

    status_code = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_ready else "not_ready",
            "components": {
                "qdrant": "connected" if qdrant_healthy else "unreachable",
                "groq_api": "configured" if groq_ready else "missing_key_warning",
            },
        },
    )


@router.get("/metrics")
async def metrics():
    """Exposes Prometheus application metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
