from typing import Literal

from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    generate_node,
    grade_node,
    retrieve_node,
    rewrite_node,
    route_node,
    tools_node,
    verify_node,
)
from app.agent.state import AgentState
from app.config import settings
from app.core.logging import logger


def route_decision(state: AgentState) -> Literal["rewrite", "generate", "tools"]:
    """Decides next node based on classification in route_node."""
    route = state.get("route", "knowledge_question")
    if route == "needs_tool":
        return "tools"
    elif route in ["chit_chat", "out_of_scope"]:
        return "generate"
    return "rewrite"


def grade_decision(state: AgentState) -> Literal["generate", "rewrite"]:
    """
    Decides whether to generate the answer or loop back to rewrite
    if relevance is insufficient and retries are under limit.
    """
    is_relevant = state.get("is_relevant", False)
    retry_count = state.get("retry_count", 0)

    if is_relevant:
        return "generate"

    if retry_count < settings.MAX_REWRITE_RETRIES:
        # Increment retry count and loop back to rewrite
        state["retry_count"] = retry_count + 1
        logger.info("relevance_low_looping_rewrite", retry_count=state["retry_count"])
        return "rewrite"

    return "generate"


def build_agent_graph():
    """Constructs and compiles the stateful LangGraph agent graph."""
    builder = StateGraph(AgentState)

    # Add all nodes
    builder.add_node("route", route_node)
    builder.add_node("rewrite", rewrite_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("grade", grade_node)
    builder.add_node("generate", generate_node)
    builder.add_node("verify", verify_node)
    builder.add_node("tools", tools_node)

    # Set entry point
    builder.set_entry_point("route")

    # Routing conditional edges
    builder.add_conditional_edges(
        "route",
        route_decision,
        {
            "rewrite": "rewrite",
            "generate": "generate",
            "tools": "tools",
        },
    )

    builder.add_edge("rewrite", "retrieve")
    builder.add_edge("retrieve", "grade")

    # Grading conditional edges (rewrite loop or generate)
    builder.add_conditional_edges(
        "grade",
        grade_decision,
        {
            "generate": "generate",
            "rewrite": "rewrite",
        },
    )

    # Verification after generation
    builder.add_edge("generate", "verify")
    builder.add_edge("verify", END)
    builder.add_edge("tools", END)

    # Compile executable graph
    graph = builder.compile()
    return graph


_compiled_graph = None


def get_agent_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_agent_graph()
    return _compiled_graph
