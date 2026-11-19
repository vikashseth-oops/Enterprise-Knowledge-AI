import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_chat import router as chat_router
from app.api.routes_docs import router as docs_router
from app.api.routes_eval import router as eval_router
from app.api.routes_health import router as health_router
from app.config import settings
from app.core.errors import (
    AppException,
    app_exception_handler,
    global_exception_handler,
)
from app.core.logging import logger, setup_logging
from app.ingestion.embedder import get_embedder
from app.retrieval.qdrant_store import get_qdrant_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifespan handler.
    Initializes models and ensures vector DB collections are pre-warmed.
    """
    setup_logging()
    logger.info(
        "application_startup",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        env=settings.APP_ENV,
    )

    # Pre-warm embedder and initialize Qdrant collection
    try:
        logger.info("warming_embedding_model")
        embedder = get_embedder()
        embedder.embed_query("startup health probe")
        logger.info("embedder_warmed_successfully")
    except Exception as e:
        logger.warning("embedder_warmup_warning", error=str(e))

    try:
        store = get_qdrant_store()
        store.ensure_collection()
        logger.info("qdrant_collection_verified")
    except Exception as e:
        logger.warning("qdrant_startup_warning", error=str(e))

    yield

    logger.info("application_shutdown", app=settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Knowledge AI: Cloud-Native Agentic RAG Platform with LangGraph, Qdrant, and Groq.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """Injects unique request-ID and measures request duration."""
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = req_id

    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000.0

    response.headers["X-Request-ID"] = req_id
    response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"
    return response


# Include API Routers
app.include_router(health_router)
app.include_router(docs_router)
app.include_router(chat_router)
app.include_router(eval_router)


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run("app.main:app", host=settings.HOST, port=port, reload=settings.DEBUG)
