import pytest

from app.retrieval.cache import TTLLRUCache
from app.retrieval.qdrant_store import QdrantStore
from app.retrieval.reranker import Reranker
from app.schemas.documents import DocumentChunk


def test_ttl_lru_cache():
    cache = TTLLRUCache(max_size=2, ttl_seconds=2)
    cache.set("k1", "v1")
    cache.set("k2", "v2")
    assert cache.get("k1") == "v1"

    # Add 3rd item, evicting oldest
    cache.set("k3", "v3")
    assert cache.get("k2") is None or cache.get("k1") is None
    assert cache.get("k3") == "v3"


def test_reciprocal_rank_fusion():
    dense_hits = [
        {"chunk_id": "c1", "score": 0.95},
        {"chunk_id": "c2", "score": 0.85},
    ]
    sparse_hits = [
        {"chunk_id": "c2", "score": 0.90},
        {"chunk_id": "c3", "score": 0.70},
    ]
    fused = Reranker.reciprocal_rank_fusion(dense_hits, sparse_hits, k=60, top_n=2)
    assert len(fused) == 2
    # c2 was present in both dense and sparse, so its fused RRF score should be highest!
    assert fused[0]["chunk_id"] == "c2"


@pytest.mark.asyncio
async def test_qdrant_store_in_memory():
    store = QdrantStore(collection_name="test_mem_collection", url=":memory:")
    chunk = DocumentChunk(
        chunk_id="test#chunk_0",
        doc_id="test_doc",
        doc_name="test.txt",
        chunk_index=0,
        text="Enterprise knowledge base retrieval testing text.",
    )
    # Upsert with dummy 384-dim vector
    dense_vec = [0.01] * 384
    store.upsert_chunks([chunk], [dense_vec])

    assert store.count_chunks() >= 1

    hits = await store.search_hybrid(dense_vec, top_k=1)
    assert len(hits) == 1
    assert hits[0]["chunk_id"] == "test#chunk_0"
    assert hits[0]["doc_name"] == "test.txt"
