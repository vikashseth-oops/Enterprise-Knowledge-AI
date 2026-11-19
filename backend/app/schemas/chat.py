from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="The user query or prompt")
    history: list[ChatMessage] = Field(default_factory=list, description="Recent conversation history")
    session_id: str | None = Field(default=None, description="Session ID for conversation memory")
    filters: dict[str, Any] | None = Field(
        default=None,
        description="Metadata filters for retrieval (e.g. source, category)",
    )
    top_k: int | None = Field(default=None, ge=1, le=20, description="Override top-k retrieved chunks")
    stream: bool = Field(default=False, description="Whether to stream response tokens")


class Citation(BaseModel):
    citation_id: int = Field(..., description="1-based index matching [1], [2] in text")
    doc_id: str
    doc_name: str
    chunk_id: str
    page_number: int | None = None
    snippet: str
    score: float
    source: str | None = None


class TraceSpan(BaseModel):
    node: str
    start_time_ms: float
    duration_ms: float
    status: str = "success"
    metadata: dict[str, Any] = Field(default_factory=dict)


class LatencyBreakdown(BaseModel):
    route_ms: float = 0.0
    rewrite_ms: float = 0.0
    retrieve_ms: float = 0.0
    grade_ms: float = 0.0
    generate_ms: float = 0.0
    verify_ms: float = 0.0
    total_ms: float = 0.0


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    session_id: str
    route: str
    rewritten_query: str | None = None
    retrieved_count: int = 0
    latency: LatencyBreakdown
    tokens: TokenUsage
    trace: list[TraceSpan] = Field(default_factory=list)


class ChatStreamChunk(BaseModel):
    event: Literal["token", "citation", "trace", "done", "error"]
    data: Any
