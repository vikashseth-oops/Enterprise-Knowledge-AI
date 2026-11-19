import pytest

from app.agent.graph import get_agent_graph
from app.agent.tools import ToolExecutor


@pytest.mark.asyncio
async def test_calculator_tool():
    res = await ToolExecutor.execute("calculator", {"expression": "25 * 4 + 10"})
    assert res["status"] == "success"
    assert res["result"] == 110


@pytest.mark.asyncio
async def test_datetime_tool():
    res = await ToolExecutor.execute("get_current_datetime", {})
    assert res["status"] == "success"
    assert "formatted" in res


@pytest.mark.asyncio
async def test_list_documents_tool():
    res = await ToolExecutor.execute("list_documents", {})
    assert res["status"] == "success"
    assert "documents" in res


@pytest.mark.asyncio
async def test_agent_graph_chitchat_flow():
    graph = get_agent_graph()
    state = {
        "session_id": "test_session",
        "original_query": "hello there!",
        "messages": [],
        "retry_count": 0,
        "trace_spans": [],
        "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
    result = await graph.ainvoke(state)
    assert "answer" in result
    assert len(result["answer"]) > 0
    assert result.get("route") in ["chit_chat", "knowledge_question"]
