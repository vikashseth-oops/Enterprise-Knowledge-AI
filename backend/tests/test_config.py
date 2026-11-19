from app.config import Settings


def test_settings_defaults():
    s = Settings()
    assert s.APP_NAME == "Enterprise Knowledge AI"
    assert s.EMBEDDING_DIMENSION == 384
    assert s.RETRIEVAL_TOP_K == 5
    assert s.CHUNK_SIZE > 0
    assert s.CHUNK_OVERLAP < s.CHUNK_SIZE


def test_cors_origins_parsing():
    s1 = Settings(CORS_ORIGINS="http://localhost:3000, http://example.com")
    assert "http://localhost:3000" in s1.CORS_ORIGINS
    assert "http://example.com" in s1.CORS_ORIGINS
