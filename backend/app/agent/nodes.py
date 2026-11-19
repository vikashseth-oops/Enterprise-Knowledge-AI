import json
import re
import time
from typing import Any

from app.agent.prompts import (
    GENERATE_PROMPT,
    GRADE_PROMPT,
    REWRITE_PROMPT,
    ROUTER_PROMPT,
    VERIFY_PROMPT,
)
from app.agent.state import AgentState
from app.agent.tools import TOOLS_SCHEMA, ToolExecutor
from app.config import settings
from app.core.logging import logger
from app.ingestion.embedder import get_embedder
from app.llm.groq_client import get_groq_client
from app.retrieval.cache import query_cache
from app.retrieval.qdrant_store import get_qdrant_store
from app.schemas.chat import Citation, TraceSpan


def _record_span(
    state: AgentState,
    node: str,
    duration_ms: float,
    status: str = "success",
    meta: dict[str, Any] | None = None,
):
    if "trace_spans" not in state or state["trace_spans"] is None:
        state["trace_spans"] = []
    state["trace_spans"].append(
        TraceSpan(
            node=node,
            start_time_ms=0.0,
            duration_ms=round(duration_ms, 2),
            status=status,
            metadata=meta or {},
        )
    )


def _accumulate_tokens(state: AgentState, usage):
    if "token_usage" not in state or not state["token_usage"]:
        state["token_usage"] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
    state["token_usage"]["prompt_tokens"] += usage.prompt_tokens
    state["token_usage"]["completion_tokens"] += usage.completion_tokens
    state["token_usage"]["total_tokens"] += usage.total_tokens


async def route_node(state: AgentState) -> AgentState:
    """Classifies the query intent using the fast 8B model."""
    start = time.perf_counter()
    groq = get_groq_client()
    query = state.get("original_query", "")

    # Fast heuristic check for obvious calculator / date queries
    lower_q = query.lower().strip()
    if any(lower_q.startswith(x) for x in ["calculate", "what is ", "eval "]) and any(c in lower_q for c in "+-*/%"):
        state["route"] = "needs_tool"
        state["route_reason"] = "Mathematical calculation requested"
        _record_span(
            state,
            "route",
            (time.perf_counter() - start) * 1000.0,
            meta={"route": "needs_tool"},
        )
        return state

    if any(k in lower_q for k in ["what time", "current time", "what date", "today's date"]):
        state["route"] = "needs_tool"
        state["route_reason"] = "Datetime lookup requested"
        _record_span(
            state,
            "route",
            (time.perf_counter() - start) * 1000.0,
            meta={"route": "needs_tool"},
        )
        return state

    if not groq.is_configured():
        # Fallback when LLM key is not provided (mock/offline mode)
        if any(g in lower_q for g in ["hello", "hi", "hey", "who are you"]):
            state["route"] = "chit_chat"
        else:
            state["route"] = "knowledge_question"
        _record_span(
            state,
            "route",
            (time.perf_counter() - start) * 1000.0,
            meta={"route": state["route"]},
        )
        return state

    messages = [
        {"role": "system", "content": ROUTER_PROMPT},
        {"role": "user", "content": f"User Query: {query}"},
    ]

    try:
        content, usage, _ = await groq.chat_completion(
            messages=messages,
            model=settings.GROQ_FAST_MODEL,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        _accumulate_tokens(state, usage)
        parsed = json.loads(content)
        state["route"] = parsed.get("route", "knowledge_question")
        state["route_reason"] = parsed.get("reason", "")
    except Exception as e:
        logger.warning("router_llm_fallback", error=str(e))
        state["route"] = "knowledge_question"
        state["route_reason"] = "Fallback default"

    _record_span(
        state,
        "route",
        (time.perf_counter() - start) * 1000.0,
        meta={"route": state["route"]},
    )
    return state


async def rewrite_node(state: AgentState) -> AgentState:
    """Reformulates or expands the search query with conversation context awareness."""
    start = time.perf_counter()
    groq = get_groq_client()
    query = state.get("original_query", "")
    retry_count = state.get("retry_count", 0)
    history = state.get("messages", [])

    # If no history and first attempt, query is already clean
    if not history and retry_count == 0:
        state["rewritten_query"] = query
        _record_span(
            state,
            "rewrite",
            (time.perf_counter() - start) * 1000.0,
            meta={"rewritten": query},
        )
        return state

    if not groq.is_configured():
        state["rewritten_query"] = query
        _record_span(
            state,
            "rewrite",
            (time.perf_counter() - start) * 1000.0,
            meta={"rewritten": query},
        )
        return state

    history_str = "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in history[-4:])
    prompt = REWRITE_PROMPT.format(
        query=query,
        history=history_str or "No prior history.",
        retry_count=retry_count,
    )

    try:
        content, usage, _ = await groq.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=settings.GROQ_FAST_MODEL,
            temperature=0.3,
        )
        _accumulate_tokens(state, usage)
        rewritten = content.strip().strip('"')
        state["rewritten_query"] = rewritten or query
    except Exception as e:
        logger.warning("rewrite_llm_fallback", error=str(e))
        state["rewritten_query"] = query

    _record_span(
        state,
        "rewrite",
        (time.perf_counter() - start) * 1000.0,
        meta={"rewritten": state["rewritten_query"]},
    )
    return state


async def retrieve_node(state: AgentState) -> AgentState:
    """Performs hybrid vector + BM25 retrieval against Qdrant with caching."""
    start = time.perf_counter()
    search_query = state.get("rewritten_query") or state.get("original_query", "")
    top_k = state.get("top_k", settings.RETRIEVAL_TOP_K)
    filters = state.get("filters")

    cache_key = f"{search_query}|{top_k}|{filters}"
    cached = query_cache.get(cache_key)
    if cached is not None:
        state["retrieved_chunks"] = cached
        _record_span(
            state,
            "retrieve",
            (time.perf_counter() - start) * 1000.0,
            meta={"count": len(cached), "cache": "hit"},
        )
        return state

    try:
        embedder = get_embedder()
        dense_vec, sparse_vec = embedder.embed_query(search_query)

        store = get_qdrant_store()
        hits = await store.search_hybrid(
            query_dense=dense_vec,
            query_sparse=sparse_vec,
            top_k=top_k,
            filters=filters,
        )
        state["retrieved_chunks"] = hits
        query_cache.set(cache_key, hits)
        _record_span(
            state,
            "retrieve",
            (time.perf_counter() - start) * 1000.0,
            meta={"count": len(hits), "cache": "miss"},
        )
    except Exception as e:
        logger.error("retrieve_node_error", error=str(e))
        state["retrieved_chunks"] = []
        state["error"] = f"Retrieval failed: {e!s}"
        _record_span(state, "retrieve", (time.perf_counter() - start) * 1000.0, status="error")

    return state


async def grade_node(state: AgentState) -> AgentState:
    """Evaluates retrieved chunks relevance and triggers loop-back rewrite if needed."""
    start = time.perf_counter()
    chunks = state.get("retrieved_chunks", [])
    query = state.get("original_query", "")
    groq = get_groq_client()

    if not chunks:
        state["is_relevant"] = False
        state["grading_reason"] = "No chunks retrieved from vector store."
        _record_span(
            state,
            "grade",
            (time.perf_counter() - start) * 1000.0,
            meta={"is_relevant": False},
        )
        return state

    # Check top similarity score
    top_score = max((c.get("score", 0.0) for c in chunks), default=0.0)
    if top_score < settings.RELEVANCE_SCORE_THRESHOLD:
        state["is_relevant"] = False
        state["grading_reason"] = (
            f"Top retrieval score ({top_score:.3f}) below threshold {settings.RELEVANCE_SCORE_THRESHOLD}"
        )
        _record_span(
            state,
            "grade",
            (time.perf_counter() - start) * 1000.0,
            meta={"is_relevant": False, "top_score": top_score},
        )
        return state

    if not groq.is_configured():
        state["is_relevant"] = True
        state["grading_reason"] = "Score passed threshold (offline mode)"
        _record_span(
            state,
            "grade",
            (time.perf_counter() - start) * 1000.0,
            meta={"is_relevant": True},
        )
        return state

    # LLM relevance verification using fast 8B model
    context_samples = "\n\n".join(
        f"[Chunk {i + 1} | ID: {c['chunk_id']}]\n{c['text'][:300]}" for i, c in enumerate(chunks[:3])
    )
    prompt = GRADE_PROMPT.format(query=query, chunks=context_samples)

    try:
        content, usage, _ = await groq.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=settings.GROQ_FAST_MODEL,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        _accumulate_tokens(state, usage)
        res = json.loads(content)
        state["is_relevant"] = res.get("is_relevant", True)
        state["grading_reason"] = res.get("reason", "")
    except Exception as e:
        logger.warning("grade_llm_fallback", error=str(e))
        state["is_relevant"] = True

    _record_span(
        state,
        "grade",
        (time.perf_counter() - start) * 1000.0,
        meta={"is_relevant": state["is_relevant"]},
    )
    return state


async def generate_node(state: AgentState) -> AgentState:
    """Generates a citation-grounded response using the 70B model."""
    start = time.perf_counter()
    route = state.get("route", "knowledge_question")
    query = state.get("original_query", "")
    groq = get_groq_client()

    # Handle chit-chat
    if route == "chit_chat":
        if groq.is_configured():
            try:
                content, usage, _ = await groq.chat_completion(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are Enterprise Knowledge AI, a helpful, polite corporate AI assistant.",
                        },
                        {"role": "user", "content": query},
                    ],
                    model=settings.GROQ_FAST_MODEL,
                    temperature=0.7,
                )
                _accumulate_tokens(state, usage)
                state["answer"] = content
            except Exception:
                state["answer"] = (
                    "Hello! I am Enterprise Knowledge AI. How can I assist you with corporate policies, documentation, or workflows today?"
                )
        else:
            state["answer"] = (
                "Hello! I am your Enterprise Knowledge AI Assistant. Ask me anything about our enterprise knowledge base."
            )
        state["citations"] = []
        _record_span(state, "generate", (time.perf_counter() - start) * 1000.0)
        return state

    # Handle out-of-scope
    if route == "out_of_scope":
        state["answer"] = (
            "I am specifically designed to assist with enterprise documentation, corporate policies, workflows, and company knowledge. This inquiry is outside my operational scope."
        )
        state["citations"] = []
        _record_span(state, "generate", (time.perf_counter() - start) * 1000.0)
        return state

    # Handle when no relevant chunks were retrieved
    if not state.get("is_relevant", False):
        state["answer"] = (
            "I could not find sufficient information in the enterprise knowledge base to answer this question. Please ensure relevant documents have been uploaded, or refine your search terms."
        )
        state["citations"] = []
        _record_span(state, "generate", (time.perf_counter() - start) * 1000.0)
        return state

    # Build context with citation numbering [1], [2], ...
    chunks = state.get("retrieved_chunks", [])
    context_lines = []
    citations: list[Citation] = []

    for idx, c in enumerate(chunks, start=1):
        snippet = c.get("text", "").strip()
        context_lines.append(
            f"[{idx}] (Doc: {c.get('doc_name', 'Unknown')}, Page: {c.get('page_number', 'N/A')})\n{snippet}"
        )
        citations.append(
            Citation(
                citation_id=idx,
                doc_id=c.get("doc_id", ""),
                doc_name=c.get("doc_name", "Unknown"),
                chunk_id=c.get("chunk_id", ""),
                page_number=c.get("page_number"),
                snippet=snippet[:300] + "..." if len(snippet) > 300 else snippet,
                score=round(c.get("score", 0.0), 4),
                source=c.get("source"),
            )
        )

    formatted_context = "\n\n".join(context_lines)
    prompt = GENERATE_PROMPT.format(context=formatted_context, query=query)

    if not groq.is_configured():
        # Offline mock answer grounded in top chunk
        top_snippet = chunks[0]["text"][:200] if chunks else "Enterprise records."
        state["answer"] = f"Based on the enterprise documentation [1], {top_snippet}"
        state["raw_answer"] = state["answer"]
        state["citations"] = citations[:1]
        _record_span(state, "generate", (time.perf_counter() - start) * 1000.0)
        return state

    try:
        content, usage, _ = await groq.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=settings.GROQ_GEN_MODEL,
            temperature=0.2,
        )
        _accumulate_tokens(state, usage)
        state["raw_answer"] = content
        state["answer"] = content

        # Filter citations to only those actually cited in the generated answer (e.g., [1], [2])
        cited_indices = set(int(m) for m in re.findall(r"\[(\d+)\]", content))
        if cited_indices:
            used_citations = [c for c in citations if c.citation_id in cited_indices]
            state["citations"] = used_citations if used_citations else citations
        else:
            state["citations"] = citations

    except Exception as e:
        logger.error("generate_node_error", error=str(e))
        state["answer"] = "An error occurred while generating the response. Please try again."
        state["citations"] = []
        state["error"] = str(e)

    _record_span(state, "generate", (time.perf_counter() - start) * 1000.0)
    return state


async def verify_node(state: AgentState) -> AgentState:
    """Hallucination guard: validates claims against retrieved context."""
    start = time.perf_counter()
    answer = state.get("answer", "")
    chunks = state.get("retrieved_chunks", [])
    groq = get_groq_client()

    # Skip verification for trivial answers, chit chat, or when LLM not configured
    if not chunks or not groq.is_configured() or len(answer) < 50 or "could not find sufficient information" in answer:
        state["verification_passed"] = True
        _record_span(
            state,
            "verify",
            (time.perf_counter() - start) * 1000.0,
            meta={"passed": True},
        )
        return state

    context_str = "\n\n".join(f"[{i + 1}] {c.get('text', '')}" for i, c in enumerate(chunks[:5]))
    prompt = VERIFY_PROMPT.format(context=context_str, answer=answer)

    try:
        content, usage, _ = await groq.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=settings.GROQ_FAST_MODEL,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        _accumulate_tokens(state, usage)
        res = json.loads(content)
        passed = res.get("passed", True)
        state["verification_passed"] = passed
        if not passed and res.get("verified_answer"):
            state["answer"] = res["verified_answer"]
    except Exception as e:
        logger.warning("verify_node_fallback", error=str(e))
        state["verification_passed"] = True

    _record_span(
        state,
        "verify",
        (time.perf_counter() - start) * 1000.0,
        meta={"passed": state.get("verification_passed", True)},
    )
    return state


async def tools_node(state: AgentState) -> AgentState:
    """Executes agent tool calls using the Groq function-calling API."""
    start = time.perf_counter()
    query = state.get("original_query", "")
    groq = get_groq_client()

    # Check for direct calculation or datetime first for maximum speed
    lower_q = query.lower().strip()
    if any(k in lower_q for k in ["what time", "current time", "what date", "today's date"]):
        tool_res = await ToolExecutor.execute("get_current_datetime", {})
        state["answer"] = f"The current date and time is **{tool_res['formatted']}**."
        state["citations"] = []
        _record_span(
            state,
            "tools",
            (time.perf_counter() - start) * 1000.0,
            meta={"tool": "get_current_datetime"},
        )
        return state

    if not groq.is_configured():
        # Fallback offline tool evaluation
        if any(c in query for c in "+-*/"):
            expr = "".join(c for c in query if c in "0123456789+-*/. ()")
            tool_res = await ToolExecutor.execute("calculator", {"expression": expr})
            if tool_res["status"] == "success":
                state["answer"] = f"Calculation result: `{tool_res['result']}`"
            else:
                state["answer"] = "Could not compute the expression."
        else:
            state["answer"] = "Tool execution requires an active GROQ_API_KEY."
        state["citations"] = []
        _record_span(state, "tools", (time.perf_counter() - start) * 1000.0)
        return state

    try:
        # Ask LLM with tools
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant with access to tools. Choose the right tool to satisfy the request.",
            },
            {"role": "user", "content": query},
        ]
        _, usage, tool_calls = await groq.chat_completion(
            messages=messages,
            model=settings.GROQ_FAST_MODEL,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
        )
        _accumulate_tokens(state, usage)

        if tool_calls:
            state["tool_calls"] = tool_calls
            tool_results = []
            for tc in tool_calls:
                fn_name = tc["function"]["name"]
                raw_args = tc["function"]["arguments"]
                args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                exec_result = await ToolExecutor.execute(fn_name, args)
                tool_results.append({"tool": fn_name, "args": args, "result": exec_result})

            state["tool_results"] = tool_results

            # Synthesize final answer from tool output
            synth_messages = [
                {
                    "role": "system",
                    "content": "You are Enterprise Knowledge AI. Formulate a concise, clear response explaining the tool results to the user.",
                },
                {
                    "role": "user",
                    "content": f"Query: {query}\nTool Results: {json.dumps(tool_results)}",
                },
            ]
            synth_content, synth_usage, _ = await groq.chat_completion(
                messages=synth_messages,
                model=settings.GROQ_FAST_MODEL,
                temperature=0.2,
            )
            _accumulate_tokens(state, synth_usage)
            state["answer"] = synth_content
        else:
            state["answer"] = "I evaluated the request but found no tool call necessary."

    except Exception as e:
        logger.error("tools_node_error", error=str(e))
        state["answer"] = f"Failed to execute tools for request: {e!s}"
        state["error"] = str(e)

    state["citations"] = []
    _record_span(state, "tools", (time.perf_counter() - start) * 1000.0)
    return state
