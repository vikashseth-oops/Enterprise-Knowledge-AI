# Enterprise Knowledge AI: System Architecture

## 1. High-Level System Architecture

```mermaid
flowchart TD
    User([Enterprise User / Browser]) <-->|HTTPS REST & SSE Stream| FE[React 18 + Vite + Tailwind Frontend]
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

## 2. Ingestion & Vector Indexing Architecture

The document ingestion pipeline processes enterprise documents asynchronously to prevent blocking web worker threads:

1. **Universal Parsing**:
   - **PDF**: Page-by-page extraction preserving page numbering via `pypdf`.
   - **DOCX**: Paragraph and table extraction preserving document hierarchies.
   - **HTML**: Strips scripts, styles, and extracts headers and text using `BeautifulSoup`.
   - **CSV**: Groups rows into structured, readable key-value chunks.
   - **Markdown / Plain Text**: Preserves headers and sectional delineations.

2. **Recursive Hierarchical Chunking**:
   - Recursive character chunker with natural boundaries (`\n\n`, `\n`, `. `, `? `, `! `).
   - Default chunk size: **500 characters** with an overlap of **60 characters**.
   - Preserves metadata: `doc_id`, `filename`, `page_number`, `section_title`, and approximate token counts.

3. **Hybrid Embeddings (Dense + Sparse)**:
   - **Dense Model**: `BAAI/bge-small-en-v1.5` (384-dimensional ONNX model executed locally via `fastembed`). Pre-cached inside the container build to eliminate cold-start delay.
   - **Sparse Model**: `Qdrant/bm25` (term-weight representation for exact token/acronym matching).

4. **Vector Store (Qdrant)**:
   - Cosine distance index for dense vectors with HNSW graph indexing ($M=16, ef\_construct=100$).
   - Named sparse vector index for BM25 term matching.
   - Fast payload indexes on `doc_id`, `source`, `collection`, and `tags` for $O(1)$ filter resolution.

---

## 3. LangGraph Agent Reasoning Workflow

The agent uses a stateful directed graph managed by **LangGraph**:

```mermaid
stateDiagram-v2
    [*] --> Route: User Query
    Route --> Rewrite: knowledge_question
    Route --> Tools: needs_tool
    Route --> Generate: chit_chat / out_of_scope
    Rewrite --> Retrieve: Rewritten Query
    Retrieve --> Grade: Candidate Chunks
    Grade --> Rewrite: Irrelevant (Retry < 2)
    Grade --> Generate: Relevant Context
    Tools --> Generate: Tool Results
    Generate --> Verify: Citation-Grounded Answer
    Verify --> [*]: Verified Response & Citations
```

### Node Specifications:
1. **Route (`route_node`)**:
   - Model: `llama-3.1-8b-instant` (low latency, ~100-200ms).
   - Classifies query into: `knowledge_question`, `chit_chat`, `needs_tool`, `out_of_scope`.
2. **Rewrite (`rewrite_node`)**:
   - Resolves pronouns based on conversation history and expands enterprise domain synonyms.
3. **Retrieve (`retrieve_node`)**:
   - Checks the high-concurrency TTL LRU cache.
   - Performs hybrid search combining dense similarity and sparse BM25 scores via Reciprocal Rank Fusion (RRF with $k=60$).
4. **Grade (`grade_node`)**:
   - Validates that retrieved chunks have sufficient relevance to answer the query.
   - If chunks fail the relevance threshold, loops back to `rewrite` (up to 2 times).
5. **Generate (`generate_node`)**:
   - Model: `llama-3.3-70b-versatile`.
   - Strictly grounded in context. Appends citation brackets `[1]`, `[2]` linking directly to source chunks.
   - Protected by XML delimiter boundaries against prompt injection.
6. **Verify (`verify_node`)**:
   - Hallucination guard: validates every claim against the retrieved context, qualifying or removing unsupported statements.
7. **Tools (`tools_node`)**:
   - Executes function calls: `calculator`, `get_current_datetime`, `list_documents`, `summarize_document`.

---

## 4. Observability & Tracing Architecture

Each node in the LangGraph workflow records an execution span:
- `node`: Node identifier (`route`, `rewrite`, `retrieve`, `grade`, `generate`, `verify`, `tools`).
- `start_time_ms`: Offset from request initiation.
- `duration_ms`: Execution time in milliseconds.
- `status`: `success` or `error`.
- `metadata`: Cache hit/miss, chunk counts, token usage, routing classifications.

All spans are logged as structured JSON via `structlog` and returned in the HTTP response / SSE stream for visual timeline rendering in the frontend.
