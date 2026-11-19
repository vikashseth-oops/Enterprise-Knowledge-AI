import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app

HEADERS = {"X-API-Key": settings.API_KEY}


@pytest.mark.asyncio
async def test_document_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. List initial documents
        list_res = await ac.get("/api/v1/documents", headers=HEADERS)
        assert list_res.status_code == 200
        initial_count = list_res.json()["total"]

        # 2. Upload sample markdown document
        files = {
            "files": (
                "test_policy.md",
                b"# Policy\nFull remote equipment stipend is $1000.",
                "text/markdown",
            ),
        }
        data = {"tags": "hr,benefits"}
        upload_res = await ac.post("/api/v1/documents/upload", files=files, data=data, headers=HEADERS)
        assert upload_res.status_code == 202
        uploaded_doc = upload_res.json()["uploaded_files"][0]
        doc_id = uploaded_doc["doc_id"]
        assert uploaded_doc["filename"] == "test_policy.md"

        # 3. Get document details
        detail_res = await ac.get(f"/api/v1/documents/{doc_id}", headers=HEADERS)
        assert detail_res.status_code == 200
        assert detail_res.json()["document"]["doc_id"] == doc_id

        # 4. Delete document
        delete_res = await ac.delete(f"/api/v1/documents/{doc_id}", headers=HEADERS)
        assert delete_res.status_code == 200
        assert "deleted successfully" in delete_res.json()["message"]

        # 5. Verify deleted
        get_deleted = await ac.get(f"/api/v1/documents/{doc_id}", headers=HEADERS)
        assert get_deleted.status_code == 404


@pytest.mark.asyncio
async def test_upload_invalid_file_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {
            "files": ("malware.exe", b"binary content", "application/octet-stream"),
        }
        res = await ac.post("/api/v1/documents/upload", files=files, headers=HEADERS)
        assert res.status_code == 415
