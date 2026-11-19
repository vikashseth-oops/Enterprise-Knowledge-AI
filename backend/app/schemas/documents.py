from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    doc_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    chunk_count: int = 0
    status: Literal["queued", "processing", "indexed", "failed"] = "queued"
    error_message: str | None = None
    collection: str = "enterprise_knowledge"
    tags: list[str] = Field(default_factory=list)


class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    doc_name: str
    chunk_index: int
    text: str
    page_number: int | None = None
    section: str | None = None
    token_count: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentUploadResponse(BaseModel):
    message: str
    uploaded_files: list[DocumentMetadata]
    batch_id: str


class DocumentListResponse(BaseModel):
    total: int
    documents: list[DocumentMetadata]


class DocumentDetailResponse(BaseModel):
    document: DocumentMetadata
    chunks_sample: list[DocumentChunk] = Field(default_factory=list)
