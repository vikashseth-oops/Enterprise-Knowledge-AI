from typing import Any, TypedDict

from app.schemas.chat import Citation, TraceSpan


class AgentState(TypedDict, total=False):
    session_id: str
    original_query: str
    messages: list[dict[str, str]]
    filters: dict[str, Any] | None
    top_k: int

    # Routing and rewrite
    route: str
    route_reason: str
    rewritten_query: str
    retry_count: int

    # Retrieval and Grading
    retrieved_chunks: list[dict[str, Any]]
    is_relevant: bool
    grading_reason: str

    # Tools
    tool_calls: list[dict[str, Any]] | None
    tool_results: list[dict[str, Any]] | None

    # Generation and Verification
    raw_answer: str
    answer: str
    citations: list[Citation]
    verification_passed: bool

    # Observability
    trace_spans: list[TraceSpan]
    token_usage: dict[str, int]
    error: str | None
