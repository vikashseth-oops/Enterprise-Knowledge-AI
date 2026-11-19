# Stage 1: Build & Dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# Pre-cache FastEmbed ONNX models inside the builder stage
ENV FASTEMBED_CACHE_PATH=/root/.cache/fastembed
RUN python -c "from fastembed import TextEmbedding, SparseTextEmbedding; \
    print('Downloading dense model...'); TextEmbedding(model_name='BAAI/bge-small-en-v1.5'); \
    print('Downloading sparse model...'); SparseTextEmbedding(model_name='Qdrant/bm25'); \
    print('Models preloaded successfully.')"


# Stage 2: Final Production Runtime (Cloud Run Ready)
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    FASTEMBED_CACHE_PATH=/app/.cache/fastembed

# Create non-root user
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash -m appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local
# Copy pre-downloaded FastEmbed model weights
COPY --from=builder --chown=appuser:appgroup /root/.cache/fastembed /app/.cache/fastembed

# Copy backend application source
COPY --chown=appuser:appgroup . /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/healthz || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
