import json
import time
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.agent.prompts import GENERATE_PROMPT
from app.agent.state import AgentState
from app.api.deps import get_graph
from app.api.routes_health import CHAT_LATENCY_HISTOGRAM, RETRIEVAL_LATENCY_HISTOGRAM
from app.config import settings
from app.core.logging import logger
from app.core.security import sanitize_input, verify_api_key
from app.llm.groq_client import get_groq_client
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    LatencyBreakdown,
    TokenUsage,
)

router = APIRouter(prefix="/api/v1/chat", tags=["Chat & Agent"])


def _extract_latency(spans: list) -> LatencyBreakdown:
    mapping = {
        "route": "route_ms",
        "rewrite": "rewrite_ms",
        "retrieve": "retrieve_ms",
        "grade": "grade_ms",
        "generate": "generate_ms",
        "verify": "verify_ms",
    }
    data = {}
    total = 0.0
    for s in spans:
        dur = s.duration_ms if hasattr(s, "duration_ms") else s.get("duration_ms", 0.0)
        node = s.node if hasattr(s, "node") else s.get("node", "")
        if node in mapping:
            data[mapping[node]] = dur
        total += dur
    data["total_ms"] = round(total, 2)
    return LatencyBreakdown(**data)


@router.post("", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
async def chat(request: ChatRequest, graph=Depends(get_graph)):
    """
    Executes an agentic RAG query through the LangGraph pipeline,
    returning an answer grounded in citations, token usage, and node execution trace.
    """
    start_time = time.perf_counter()
    session_id = request.session_id or str(uuid.uuid4())
    cleaned_query = sanitize_input(request.message)

    if not cleaned_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty.",
        )

    initial_state: AgentState = {
        "session_id": session_id,
        "original_query": cleaned_query,
        "messages": [{"role": m.role, "content": m.content} for m in request.history],
        "filters": request.filters,
        "top_k": request.top_k or settings.RETRIEVAL_TOP_K,
        "retry_count": 0,
        "trace_spans": [],
        "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }

    try:
        final_state = await graph.ainvoke(initial_state)
    except Exception as e:
        logger.error("agent_execution_failure", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent reasoning graph failed: {e!s}",
        )

    total_duration = time.perf_counter() - start_time
    CHAT_LATENCY_HISTOGRAM.observe(total_duration)

    spans = final_state.get("trace_spans", [])
    latency_breakdown = _extract_latency(spans)
    if "retrieve_ms" in latency_breakdown.model_dump():
        RETRIEVAL_LATENCY_HISTOGRAM.observe(latency_breakdown.retrieve_ms / 1000.0)

    token_dict = final_state.get("token_usage", {})
    tokens = TokenUsage(
        prompt_tokens=token_dict.get("prompt_tokens", 0),
        completion_tokens=token_dict.get("completion_tokens", 0),
        total_tokens=token_dict.get("total_tokens", 0),
    )

    return ChatResponse(
        answer=final_state.get("answer", "No answer generated."),
        citations=final_state.get("citations", []),
        session_id=session_id,
        route=final_state.get("route", "knowledge_question"),
        rewritten_query=final_state.get("rewritten_query"),
        retrieved_count=len(final_state.get("retrieved_chunks", [])),
        latency=latency_breakdown,
        tokens=tokens,
        trace=spans,
    )


@router.post("/stream", dependencies=[Depends(verify_api_key)])
async def chat_stream(request: ChatRequest, graph=Depends(get_graph)):
    """
    Streams response tokens using Server-Sent Events (SSE), followed by
    citations, latency metrics, and execution trace events.
    """
    session_id = request.session_id or str(uuid.uuid4())
    cleaned_query = sanitize_input(request.message)

    if not cleaned_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty.",
        )

    async def event_generator() -> AsyncIterator[str]:
        start_time = time.perf_counter()
        initial_state: AgentState = {
            "session_id": session_id,
            "original_query": cleaned_query,
            "messages": [{"role": m.role, "content": m.content} for m in request.history],
            "filters": request.filters,
            "top_k": request.top_k or settings.RETRIEVAL_TOP_K,
            "retry_count": 0,
            "trace_spans": [],
            "token_usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        }

        try:
            # First execute the graph up to retrieval/grading
            # (or full graph if offline / tool call)
            state = await graph.ainvoke(initial_state)

            answer = state.get("answer", "")
            route = state.get("route", "knowledge_question")
            is_relevant = state.get("is_relevant", True)
            chunks = state.get("retrieved_chunks", [])
            citations = state.get("citations", [])
            spans = state.get("trace_spans", [])

            groq = get_groq_client()

            # If it's a knowledge question and Groq is configured, stream tokens live
            if route == "knowledge_question" and is_relevant and groq.is_configured() and chunks:
                context_lines = []
                for idx, c in enumerate(chunks, start=1):
                    snippet = c.get("text", "").strip()
                    context_lines.append(f"[{idx}] (Doc: {c.get('doc_name', 'Unknown')})\n{snippet}")
                formatted_context = "\n\n".join(context_lines)
                prompt = GENERATE_PROMPT.format(context=formatted_context, query=cleaned_query)

                stream = groq.chat_stream(
                    messages=[{"role": "user", "content": prompt}],
                    model=settings.GROQ_GEN_MODEL,
                    temperature=0.2,
                )
                accumulated = []
                async for token in stream:
                    accumulated.append(token)
                    yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"
            else:
                # Stream the pre-computed answer in chunks
                words = answer.split(" ")
                for i, w in enumerate(words):
                    token = w + (" " if i < len(words) - 1 else "")
                    yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"

            # Emit citations event
            citations_data = [c.model_dump() if hasattr(c, "model_dump") else c for c in citations]
            yield f"event: citation\ndata: {json.dumps({'citations': citations_data})}\n\n"

            # Emit trace event
            latency_breakdown = _extract_latency(spans)
            spans_data = [s.model_dump() if hasattr(s, "model_dump") else s for s in spans]
            yield f"event: trace\ndata: {json.dumps({'latency': latency_breakdown.model_dump(), 'trace': spans_data})}\n\n"

            # Emit done event
            yield f"event: done\ndata: {json.dumps({'session_id': session_id, 'status': 'completed'})}\n\n"

        except Exception as e:
            logger.error("stream_error", error=str(e))
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
