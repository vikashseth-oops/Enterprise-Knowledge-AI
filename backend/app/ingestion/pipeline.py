import asyncio
import uuid
from datetime import datetime

from app.core.logging import logger
from app.ingestion.chunker import RecursiveChunker
from app.ingestion.embedder import get_embedder
from app.ingestion.parsers import DocumentParser
from app.retrieval.qdrant_store import get_qdrant_store
from app.schemas.documents import DocumentChunk, DocumentMetadata


class IngestionPipeline:
    """
    Manages document ingestion lifecycle: parsing, chunking,
    dense + sparse embedding generation, vector indexing, and status tracking.
    """

    def __init__(self):
        self.doc_registry: dict[str, DocumentMetadata] = {}
        self.chunker = RecursiveChunker()

    def register_upload(self, filename: str, file_bytes: bytes, tags: list[str] | None = None) -> DocumentMetadata:
        doc_id = str(uuid.uuid4())
        ext = filename.split(".")[-1].lower() if "." in filename else "unknown"

        meta = DocumentMetadata(
            doc_id=doc_id,
            filename=filename,
            file_type=ext,
            file_size_bytes=len(file_bytes),
            created_at=datetime.utcnow(),
            chunk_count=0,
            status="queued",
            tags=tags or [],
        )
        self.doc_registry[doc_id] = meta
        return meta

    async def process_document(self, doc_id: str, filename: str, file_bytes: bytes):
        """Asynchronously parses, chunks, embeds, and indexes a single document."""
        meta = self.doc_registry.get(doc_id)
        if not meta:
            logger.error("doc_id_not_found_in_registry", doc_id=doc_id)
            return

        meta.status = "processing"
        logger.info("start_document_ingestion", doc_id=doc_id, filename=filename)

        try:
            # 1. Parse document sections
            sections = await asyncio.to_thread(DocumentParser.parse, file_bytes, filename)
            if not sections:
                raise ValueError("No text content could be extracted from document")

            # 2. Chunk sections
            chunks: list[DocumentChunk] = self.chunker.chunk_sections(
                doc_id=doc_id,
                doc_name=filename,
                sections=sections,
            )
            if not chunks:
                raise ValueError("Document yielded 0 chunks after splitting")

            # 3. Embed chunks (Dense + Sparse)
            texts = [c.text for c in chunks]
            embedder = get_embedder()
            dense_vectors = await asyncio.to_thread(embedder.embed_dense_texts, texts)
            sparse_vectors = await asyncio.to_thread(embedder.embed_sparse_texts, texts)

            # 4. Upsert into Qdrant
            store = get_qdrant_store()
            await asyncio.to_thread(store.upsert_chunks, chunks, dense_vectors, sparse_vectors)

            # 5. Update metadata
            meta.chunk_count = len(chunks)
            meta.status = "indexed"
            logger.info("document_indexed_successfully", doc_id=doc_id, chunks=len(chunks))

        except Exception as e:
            meta.status = "failed"
            meta.error_message = str(e)
            logger.error("document_ingestion_failed", doc_id=doc_id, error=str(e))

    def list_documents(self) -> list[DocumentMetadata]:
        return list(self.doc_registry.values())

    def get_document(self, doc_id: str) -> DocumentMetadata | None:
        return self.doc_registry.get(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        if doc_id in self.doc_registry:
            store = get_qdrant_store()
            store.delete_document(doc_id)
            del self.doc_registry[doc_id]
            logger.info("document_deleted", doc_id=doc_id)
            return True
        return False


_global_pipeline: IngestionPipeline | None = None


def get_ingestion_pipeline() -> IngestionPipeline:
    global _global_pipeline
    if _global_pipeline is None:
        _global_pipeline = IngestionPipeline()
    return _global_pipeline
