import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app

HEADERS = {"X-API-Key": settings.API_KEY}


@pytest.mark.asyncio
async def test_healthz():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readyz():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/readyz")
        # Should return 200 or 503 depending on Groq config
        assert response.status_code in [200, 503]
        assert "components" in response.json()


@pytest.mark.asyncio
async def test_metrics():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/metrics")
        assert response.status_code == 200
        assert "rag_http_requests_total" in response.text


@pytest.mark.asyncio
async def test_unauthorized_access():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/chat", json={"message": "hello"})
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_endpoint_valid():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"message": "Hello, how can you help me today?"}
        response = await ac.post("/api/v1/chat", json=payload, headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "session_id" in data
        assert "latency" in data
        assert "trace" in data


@pytest.mark.asyncio
async def test_chat_stream_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"message": "What is the enterprise policy?"}
        response = await ac.post("/api/v1/chat/stream", json=payload, headers=HEADERS)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
