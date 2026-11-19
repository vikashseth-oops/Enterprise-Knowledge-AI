from typing import Any

from fastembed import SparseTextEmbedding, TextEmbedding

from app.config import settings
from app.core.errors import EmbeddingError
from app.core.logging import logger


class Embedder:
    """
    Local ONNX-based dense and sparse embedder using fastembed.
    Provides batch processing and vector normalization.
    """

    def __init__(
        self,
        dense_model_name: str | None = None,
        sparse_model_name: str | None = None,
        cache_dir: str | None = None,
    ):
        self.dense_model_name = dense_model_name or settings.EMBEDDING_MODEL
        self.sparse_model_name = sparse_model_name or settings.SPARSE_MODEL
        self.cache_dir = cache_dir or settings.EMBEDDING_CACHE_DIR

        logger.info(
            "initializing_embedder",
            dense_model=self.dense_model_name,
            sparse_model=self.sparse_model_name,
        )

        try:
            self._dense_model = TextEmbedding(
                model_name=self.dense_model_name,
                cache_dir=self.cache_dir,
            )
        except Exception as e:
            logger.error("dense_embedder_init_error", error=str(e))
            raise EmbeddingError(f"Failed to load dense embedding model {self.dense_model_name}: {e}")

        try:
            self._sparse_model = SparseTextEmbedding(
                model_name=self.sparse_model_name,
                cache_dir=self.cache_dir,
            )
        except Exception as e:
            logger.warning("sparse_embedder_init_fallback", error=str(e))
            # If sparse model fails to initialize, fallback gracefully
            self._sparse_model = None

    def embed_dense_texts(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        """Generates normalized dense embeddings for a list of texts."""
        if not texts:
            return []
        try:
            embeddings_generator = self._dense_model.embed(texts, batch_size=batch_size)
            return [emb.tolist() for emb in embeddings_generator]
        except Exception as e:
            logger.error("embed_dense_error", count=len(texts), error=str(e))
            raise EmbeddingError(f"Dense embedding computation failed: {e!s}")

    def embed_sparse_texts(self, texts: list[str], batch_size: int = 64) -> list[dict[str, Any]]:
        """
        Generates sparse term-weight embeddings (indices and values) for BM25 hybrid search.
        """
        if not texts:
            return []
        if self._sparse_model is None:
            return [{"indices": [], "values": []} for _ in texts]
        try:
            sparse_generator = self._sparse_model.embed(texts, batch_size=batch_size)
            results = []
            for sp in sparse_generator:
                results.append(
                    {
                        "indices": sp.indices.tolist() if hasattr(sp.indices, "tolist") else list(sp.indices),
                        "values": sp.values.tolist() if hasattr(sp.values, "tolist") else list(sp.values),
                    }
                )
            return results
        except Exception as e:
            logger.warning("embed_sparse_error", count=len(texts), error=str(e))
            return [{"indices": [], "values": []} for _ in texts]

    def embed_query(self, query: str) -> tuple[list[float], dict[str, Any]]:
        """Generates dense and sparse representations for a search query."""
        dense_vec = self.embed_dense_texts([query])[0]
        sparse_vec = self.embed_sparse_texts([query])[0]
        return dense_vec, sparse_vec


_global_embedder: Embedder | None = None


def get_embedder() -> Embedder:
    global _global_embedder
    if _global_embedder is None:
        _global_embedder = Embedder()
    return _global_embedder
