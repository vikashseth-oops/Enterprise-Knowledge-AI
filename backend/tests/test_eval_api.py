import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app

HEADERS = {"X-API-Key": settings.API_KEY}


@pytest.mark.asyncio
async def test_get_latest_eval():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/eval/latest", headers=HEADERS)
        # We previously ran run_retrieval_eval.py, so report.json exists!
        assert res.status_code == 200
        data = res.json()
        assert "retrieval" in data
        assert data["retrieval"]["recall_at_5"] >= 0.80
        assert data["target_met"] is True


@pytest.mark.asyncio
async def test_trigger_eval():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"sample_size": 10, "evaluate_generation": False}
        res = await ac.post("/api/v1/eval/run", json=payload, headers=HEADERS)
        assert res.status_code == 200
        assert "Evaluation suite initiated" in res.json()["message"]
