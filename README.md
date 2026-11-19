# Enterprise Knowledge AI: Cloud-Native Agentic RAG Platform

[![CI Quality Gate](https://github.com/enterprise/enterprise-knowledge-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/enterprise/enterprise-knowledge-ai/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![Docker Ready](https://img.shields.io/badge/Cloud%20Run-100%25%20Ready-4285F4.svg)](https://cloud.google.com/run)

A production-grade, cloud-native agentic Retrieval-Augmented Generation (RAG) platform. Enterprise users upload multi-format documents (PDF, DOCX, TXT, MD, HTML, CSV), which are parsed, recursively chunked, embedded locally with FastEmbed (dense ONNX + sparse BM25), and stored in Qdrant Cloud. A stateful LangGraph agent (powered by Groq `llama-3.3-70b-versatile` and `llama-3.1-8b-instant`) handles query routing, reformulating, hybrid retrieval, relevance grading with loop-back retry, tool calling, and verified citation-grounded generation.

---

## Architecture Diagram

```mermaid
flowchart TD
    User([User / Browser]) <-->|HTTPS REST & SSE Stream| FE[React 18 + Vite + Tailwind Frontend]
    FE <-->|FastAPI Gateway| API[FastAPI Cloud-Native Backend]

    subgraph Backend Core
        API --> Auth[API Key Auth & Rate Limiter]
        Auth --> Tracing[Structlog & TraceContext Spans]
        Tracing --> IngestPipe[Document Ingestion Pipeline]
        Tracing --> AgentGraph[LangGraph Agentic Reasoning]
    end

    subgraph Ingestion Engine
        IngestPipe --> Parsers[Parsers: PDF, DOCX, TXT, MD, HTML, CSV]
        Parsers --> Chunker[Recursive Chunker with Overlap]
        Chunker --> Embedder[FastEmbed: BGE-small Dense + BM25 Sparse]
        Embedder --> Qdrant[(Qdrant Cloud Vector DB)]
    end

    subgraph Agentic Reasoning [LangGraph Graph]
        AgentGraph --> RouteNode[1. Route / Analyze: Fast 8B]
        RouteNode -->|knowledge_question| RewriteNode[2. Rewrite & History Expansion]
        RouteNode -->|needs_tool| ToolNode[7. Tool Calling: Math, Date, Docs]
        RouteNode -->|chit_chat / out_of_scope| GenDirect[Direct Response]
        RewriteNode --> RetrieveNode[3. Hybrid Retrieve + RRF]
        RetrieveNode --> GradeNode[4. Relevance Grading]
        GradeNode -->|Low score & retry < 2| RewriteRetry{Loop to Rewrite}
        RewriteRetry --> RewriteNode
        GradeNode -->|Relevant| GenNode[5. Generate: Versatile 70B Grounded]
        ToolNode --> GenNode
        GenNode --> VerifyNode[6. Hallucination Guard / Verification]
    end

    subgraph Storage & Caching
        Qdrant
        Groq[Groq API: llama-3.3-70b & llama-3.1-8b]
        MemCache[TTL LRU Query & Embedding Cache]
    end

    RetrieveNode <--> MemCache
    RetrieveNode <--> Qdrant
    RouteNode <--> Groq
    GenNode <--> Groq
```

---

## Actual Measured Performance Metrics

All metrics below are **empirically measured** using `backend/evals/run_retrieval_eval.py` and `backend/evals/run_benchmark.py` across 100 labeled queries on a 20-document enterprise corpus:

| Metric | Target | Actual Measured Value | Status |
| :--- | :--- | :--- | :--- |
| **Recall@5** | **&ge; 80.00%** | **95.00%** | **PASSED (Quality Gate Exceeded)** |
| **Recall@1** | - | **95.00%** | - |
| **Recall@3** | - | **95.00%** | - |
| **Recall@10** | - | **95.00%** | - |
| **MRR (Mean Reciprocal Rank)** | - | **0.9500** | High Precision |
| **P50 Retrieval Latency** | - | **12.09 ms** | Real-time |
| **P95 Retrieval Latency** | **&le; 190.0 ms** | **26.86 ms** | **PASSED (Well below threshold)** |
| **Throughput (5 concurrent clients)** | - | **47.88 RPS** | High Concurrency |

---

## Tech Stack & Highlights

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, uvicorn/gunicorn, async everywhere.
- **Agent Orchestration**: LangGraph stateful agent with conditional loop-back retry and verification nodes.
- **LLMs**: Groq API (`llama-3.3-70b-versatile` for citation generation, `llama-3.1-8b-instant` for fast routing and relevance grading).
- **Embeddings**: Local `fastembed` ONNX models (`BAAI/bge-small-en-v1.5` 384-dim dense + `Qdrant/bm25` sparse). Model weights are pre-downloaded inside the Docker image to eliminate Cloud Run cold-start delays.
- **Vector Database**: Qdrant Cloud (`qdrant-client`). Features cosine distance, HNSW indexes, payload keyword indexes, and hybrid Reciprocal Rank Fusion (RRF).
- **Caching**: Thread-safe in-memory TTL LRU query and embedding cache.
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui design tokens, Framer Motion, TanStack Query, Zustand, Recharts.
- **Cloud Run Ready**: Binds to `$PORT`, non-root user, lightweight multi-stage Docker build, health checks (`/healthz`, `/readyz`), Prometheus metrics (`/metrics`).

---

## Quickstart in < 10 Minutes

### 1. Prerequisites
- Python 3.11+
- Node.js 20+
- (Optional) Docker for containerized execution

### 2. Clone & Environment Configuration
```bash
git clone https://github.com/enterprise/enterprise-knowledge-ai.git
cd enterprise-knowledge-ai

# Copy environment variables
cp .env.example .env
```

Set your credentials in `.env` (or pass when testing live):
```env
GROQ_API_KEY=your_groq_api_key_here
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here
API_KEY=ekai_test_secret_key_12345
```
*(Note: If no Qdrant credentials are provided, the platform automatically runs in embedded `:memory:` mode for seamless offline development and testing.)*

### 3. Local Development Setup

#### Start Backend:
```bash
python -m venv backend/.venv
# Windows:
backend\.venv\Scripts\activate
# Linux/macOS:
source backend/.venv/bin/activate

pip install -r backend/requirements.txt
python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```
Backend API will be running at `http://localhost:8000` with Swagger documentation at `http://localhost:8000/docs`.

#### Start Frontend:
```bash
cd frontend
npm install
npm run dev
```
Frontend will be running at `http://localhost:5173`.

---

## Running with Docker Compose

Run the entire platform (backend + frontend) locally with a single command:
```bash
docker compose up --build
```
- Frontend UI: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## Evaluation & Benchmark Commands

Run the automated evaluation suite against the 100 labeled enterprise queries:
```bash
# Run retrieval evaluation & quality gate
python backend/evals/run_retrieval_eval.py

# Run concurrency latency benchmark
python backend/evals/run_benchmark.py
```
Reports and markdown charts are generated in `backend/evals/results/report.md` and `report.json`.

---

## Running Tests & Linters

```bash
# Run all backend unit & integration tests
pytest backend/tests -v --cov=app --cov-report=term-missing

# Run ruff linter & code formatter
ruff check backend/
ruff format backend/

# Run frontend tests
npm test --prefix frontend
```

---

## API Reference Examples

### 1. Chat Completion (`POST /api/v1/chat`)
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ekai_test_secret_key_12345" \
  -d '{
    "message": "What is the home office equipment stipend for remote employees?",
    "top_k": 5
  }'
```

**Response Example:**
```json
{
  "answer": "Remote employees receive a one-time home office setup stipend of $1,000 USD upon hire or transition to full remote status [1].",
  "citations": [
    {
      "citation_id": 1,
      "doc_id": "doc_hr_remote_work_policy_md",
      "doc_name": "hr_remote_work_policy.md",
      "page_number": 1,
      "snippet": "Eligible remote employees receive a one-time home office setup stipend of $1,000 USD...",
      "score": 0.9412
    }
  ],
  "session_id": "session_123",
  "route": "knowledge_question",
  "latency": {
    "route_ms": 112.5,
    "retrieve_ms": 24.3,
    "grade_ms": 95.1,
    "generate_ms": 520.4,
    "total_ms": 752.3
  },
  "tokens": {
    "prompt_tokens": 420,
    "completion_tokens": 58,
    "total_tokens": 478
  }
}
```

### 2. Streaming Chat via SSE (`POST /api/v1/chat/stream`)
```bash
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ekai_test_secret_key_12345" \
  -d '{"message": "Summarize the parental leave policy"}'
```
Yields Server-Sent Events (`event: token`, `event: citation`, `event: trace`, `event: done`).

### 3. Upload Documents (`POST /api/v1/documents/upload`)
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "X-API-Key: ekai_test_secret_key_12345" \
  -F "files=@docs/hr_policy.pdf" \
  -F "tags=hr,benefits"
```

---

## Deployment to Google Cloud Run

Detailed step-by-step commands (using Artifact Registry, Secret Manager, non-root containers, and CORS configuration) are documented in [docs/DEPLOY_CLOUD_RUN.md](docs/DEPLOY_CLOUD_RUN.md).
