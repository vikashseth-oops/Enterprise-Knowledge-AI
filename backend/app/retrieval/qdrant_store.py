import asyncio
from typing import Any

from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.http import models as rest_models

from app.config import settings
from app.core.errors import VectorStoreError
from app.core.logging import logger
from app.retrieval.reranker import Reranker
from app.schemas.documents import DocumentChunk


class QdrantStore:
    """
    Production-grade Qdrant client supporting Qdrant Cloud, local instances,
    and embedded in-memory mode, dense + sparse vectors, payload indexing,
    and hybrid search with RRF fusion.
    """

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        collection_name: str | None = None,
        prefer_grpc: bool | None = None,
    ):
        self.url = url or settings.QDRANT_URL
        self.api_key = api_key or settings.QDRANT_API_KEY
        self.collection_name = collection_name or settings.QDRANT_COLLECTION
        self.prefer_grpc = prefer_grpc if prefer_grpc is not None else settings.QDRANT_PREFER_GRPC

        self.is_memory = self.url == ":memory:" or self.url.startswith("memory:") or not self.url

        if self.is_memory:
            self.client = QdrantClient(location=":memory:")
            self.async_client = None
        else:
            try:
                self.client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key,
                    prefer_grpc=self.prefer_grpc,
                    timeout=5.0,
                    check_compatibility=False,
                )
                # Test connectivity
                self.client.get_collections()
                self.async_client = AsyncQdrantClient(
                    url=self.url,
                    api_key=self.api_key,
                    prefer_grpc=self.prefer_grpc,
                    timeout=5.0,
                    check_compatibility=False,
                )
            except Exception as e:
                logger.warning(
                    "qdrant_remote_unreachable_fallback_memory",
                    url=self.url,
                    error=str(e),
                )
                self.client = QdrantClient(location=":memory:")
                self.async_client = None
                self.is_memory = True

        self._initialized = False

    def ensure_collection(self):
        """Initializes the collection with dense and sparse vector configurations and payload indexes."""
        if self._initialized:
            return

        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                logger.info("creating_qdrant_collection", collection=self.collection_name)
                vectors_config = {
                    "dense": rest_models.VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=rest_models.Distance.COSINE,
                        hnsw_config=rest_models.HnswConfigDiff(
                            m=16,
                            ef_construct=100,
                        ),
                    )
                }

                sparse_vectors_config = {
                    "sparse": rest_models.SparseVectorParams(
                        index=rest_models.SparseIndexParams(
                            on_disk=False,
                        )
                    )
                }

                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=vectors_config,
                    sparse_vectors_config=sparse_vectors_config,
                )

                indexed_fields = ["doc_id", "source", "collection", "tags"]
                for field in indexed_fields:
                    try:
                        self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name=field,
                            field_schema=rest_models.PayloadSchemaType.KEYWORD,
                        )
                    except Exception as e:
                        logger.warning("payload_index_warn", field=field, error=str(e))

            self._initialized = True
        except Exception as e:
            logger.error("qdrant_ensure_collection_failed", error=str(e))
            raise VectorStoreError(f"Failed to initialize Qdrant collection: {e!s}")

    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        dense_embeddings: list[list[float]],
        sparse_embeddings: list[dict[str, Any]] | None = None,
    ):
        """Upserts a batch of document chunks with their dense and sparse vector representations."""
        self.ensure_collection()
        if not chunks:
            return

        points = []
        for i, chunk in enumerate(chunks):
            dense_vec = dense_embeddings[i]
            sparse_dict = sparse_embeddings[i] if sparse_embeddings else None

            vector_dict: dict[str, Any] = {"dense": dense_vec}
            if sparse_dict and sparse_dict.get("indices"):
                vector_dict["sparse"] = rest_models.SparseVector(
                    indices=sparse_dict["indices"],
                    values=sparse_dict["values"],
                )

            payload = {
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "doc_name": chunk.doc_name,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "page_number": chunk.page_number,
                "section": chunk.section,
                "token_count": chunk.token_count,
                "source": chunk.doc_name,
                "collection": self.collection_name,
                "metadata": chunk.metadata,
            }

            point_id = i + 1 if self.is_memory else (abs(hash(chunk.chunk_id)) % (2**63 - 1))
            points.append(
                rest_models.PointStruct(
                    id=point_id,
                    vector=vector_dict,
                    payload=payload,
                )
            )

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,
            )
            logger.info("chunks_upserted_successfully", count=len(points))
        except Exception as e:
            logger.error("upsert_chunks_failed", error=str(e))
            raise VectorStoreError(f"Failed to upsert chunks into Qdrant: {e!s}")

    def _query_dense(self, query_dense: list[float], fetch_k: int, query_filter: Any) -> list[dict[str, Any]]:
        if hasattr(self.client, "query_points"):
            res = self.client.query_points(
                collection_name=self.collection_name,
                query=query_dense,
                using="dense",
                query_filter=query_filter,
                limit=fetch_k,
                with_payload=True,
            )
            hits = res.points
        else:
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=rest_models.NamedVector(name="dense", vector=query_dense),
                query_filter=query_filter,
                limit=fetch_k,
                with_payload=True,
            )

        return [
            {
                "chunk_id": h.payload.get("chunk_id", str(h.id)),
                "doc_id": h.payload.get("doc_id", ""),
                "doc_name": h.payload.get("doc_name", "Unknown"),
                "text": h.payload.get("text", ""),
                "page_number": h.payload.get("page_number"),
                "section": h.payload.get("section"),
                "score": float(h.score),
                "source": h.payload.get("source", ""),
                "metadata": h.payload.get("metadata", {}),
            }
            for h in hits
        ]

    def _query_sparse(self, query_sparse: dict[str, Any], fetch_k: int, query_filter: Any) -> list[dict[str, Any]]:
        sparse_vec = rest_models.SparseVector(
            indices=query_sparse["indices"],
            values=query_sparse["values"],
        )
        if hasattr(self.client, "query_points"):
            res = self.client.query_points(
                collection_name=self.collection_name,
                query=sparse_vec,
                using="sparse",
                query_filter=query_filter,
                limit=fetch_k,
                with_payload=True,
            )
            hits = res.points
        else:
            sparse_vector = rest_models.NamedSparseVector(name="sparse", vector=sparse_vec)
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=sparse_vector,
                query_filter=query_filter,
                limit=fetch_k,
                with_payload=True,
            )

        return [
            {
                "chunk_id": h.payload.get("chunk_id", str(h.id)),
                "doc_id": h.payload.get("doc_id", ""),
                "doc_name": h.payload.get("doc_name", "Unknown"),
                "text": h.payload.get("text", ""),
                "page_number": h.payload.get("page_number"),
                "section": h.payload.get("section"),
                "score": float(h.score),
                "source": h.payload.get("source", ""),
                "metadata": h.payload.get("metadata", {}),
            }
            for h in hits
        ]

    async def search_hybrid(
        self,
        query_dense: list[float],
        query_sparse: dict[str, Any] | None = None,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Executes hybrid search combining dense cosine similarity and sparse BM25
        with Reciprocal Rank Fusion (RRF).
        """
        self.ensure_collection()
        top_k = top_k or settings.RETRIEVAL_TOP_K

        query_filter = None
        if filters:
            must_conditions = []
            for k, v in filters.items():
                if v is not None:
                    must_conditions.append(
                        rest_models.FieldCondition(
                            key=k,
                            match=rest_models.MatchValue(value=v),
                        )
                    )
            if must_conditions:
                query_filter = rest_models.Filter(must=must_conditions)

        fetch_k = min(top_k * 3, 30)

        # Dense query (direct if in-memory to avoid thread-affinity issues)
        if self.is_memory:
            dense_results = self._query_dense(query_dense, fetch_k, query_filter)
        else:
            dense_results = await asyncio.to_thread(self._query_dense, query_dense, fetch_k, query_filter)

        # Sparse query if available
        sparse_results = []
        if query_sparse and query_sparse.get("indices"):
            try:
                if self.is_memory:
                    sparse_results = self._query_sparse(query_sparse, fetch_k, query_filter)
                else:
                    sparse_results = await asyncio.to_thread(self._query_sparse, query_sparse, fetch_k, query_filter)
            except Exception as e:
                logger.warning("sparse_search_skipped", error=str(e))

        if sparse_results:
            fused = Reranker.reciprocal_rank_fusion(
                dense_results=dense_results,
                sparse_results=sparse_results,
                k=60,
                top_n=top_k,
            )
            return fused
        else:
            return dense_results[:top_k]

    def delete_document(self, doc_id: str) -> bool:
        """Deletes all chunks belonging to a document ID."""
        self.ensure_collection()
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=rest_models.FilterSelector(
                    filter=rest_models.Filter(
                        must=[
                            rest_models.FieldCondition(
                                key="doc_id",
                                match=rest_models.MatchValue(value=doc_id),
                            )
                        ]
                    )
                ),
            )
            return True
        except Exception as e:
            logger.error("delete_document_error", doc_id=doc_id, error=str(e))
            raise VectorStoreError(f"Failed to delete document chunks: {e!s}")

    def get_document_chunks(self, doc_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Retrieves sample chunks for a document."""
        self.ensure_collection()
        try:
            res, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=rest_models.Filter(
                    must=[
                        rest_models.FieldCondition(
                            key="doc_id",
                            match=rest_models.MatchValue(value=doc_id),
                        )
                    ]
                ),
                limit=limit,
                with_payload=True,
            )
            return [p.payload for p in res if p.payload]
        except Exception as e:
            logger.warning("scroll_chunks_failed", doc_id=doc_id, error=str(e))
            return []

    def is_healthy(self) -> bool:
        """Checks whether Qdrant is reachable and responding."""
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False

    def count_chunks(self) -> int:
        """Returns total vector count in the collection."""
        try:
            self.ensure_collection()
            info = self.client.get_collection(self.collection_name)
            return info.points_count or 0
        except Exception:
            return 0


_global_qdrant_store: QdrantStore | None = None


def get_qdrant_store() -> QdrantStore:
    global _global_qdrant_store
    if _global_qdrant_store is None:
        _global_qdrant_store = QdrantStore()
    return _global_qdrant_store
