import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.api.deps import get_pipeline, get_store
from app.config import settings
from app.core.logging import logger
from app.core.security import verify_api_key
from app.ingestion.pipeline import IngestionPipeline
from app.retrieval.qdrant_store import QdrantStore
from app.schemas.documents import (
    DocumentChunk,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentMetadata,
    DocumentUploadResponse,
)

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".html", ".htm", ".csv"}


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_api_key)],
)
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    tags: str | None = Form(None),
    pipeline: IngestionPipeline = Depends(get_pipeline),
):
    """
    Uploads one or multiple documents for parsing, chunking, and vector indexing.
    Processes files in the background and tracks ingestion status.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file must be provided.",
        )

    parsed_tags = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    uploaded_metas: list[DocumentMetadata] = []
    batch_id = str(uuid.uuid4())

    for f in files:
        # File type validation
        filename = f.filename or "unknown"
        ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File '{filename}' has unsupported extension '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        content = await f.read()
        # Size validation
        if len(content) > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File '{filename}' ({len(content)} bytes) exceeds max limit of {settings.MAX_FILE_SIZE_BYTES} bytes.",
            )

        # Register metadata
        meta = pipeline.register_upload(filename, content, tags=parsed_tags)
        uploaded_metas.append(meta)

        # Enqueue background ingestion
        background_tasks.add_task(pipeline.process_document, meta.doc_id, filename, content)

    logger.info("documents_enqueued_for_ingestion", count=len(uploaded_metas), batch_id=batch_id)
    return DocumentUploadResponse(
        message=f"{len(uploaded_metas)} document(s) uploaded successfully and enqueued for indexing.",
        uploaded_files=uploaded_metas,
        batch_id=batch_id,
    )


@router.get("", response_model=DocumentListResponse, dependencies=[Depends(verify_api_key)])
async def list_documents(pipeline: IngestionPipeline = Depends(get_pipeline)):
    """Lists all uploaded documents with current indexing status and chunk count."""
    docs = pipeline.list_documents()
    return DocumentListResponse(total=len(docs), documents=docs)


@router.get(
    "/{doc_id}",
    response_model=DocumentDetailResponse,
    dependencies=[Depends(verify_api_key)],
)
async def get_document(
    doc_id: str,
    pipeline: IngestionPipeline = Depends(get_pipeline),
    store: QdrantStore = Depends(get_store),
):
    """Retrieves document metadata along with a sample of indexed chunks."""
    doc = pipeline.get_document(doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{doc_id}' not found.",
        )

    raw_chunks = store.get_document_chunks(doc_id, limit=10)
    chunks = [
        DocumentChunk(
            chunk_id=c.get("chunk_id", ""),
            doc_id=c.get("doc_id", doc_id),
            doc_name=c.get("doc_name", doc.filename),
            chunk_index=c.get("chunk_index", 0),
            text=c.get("text", ""),
            page_number=c.get("page_number"),
            section=c.get("section"),
            token_count=c.get("token_count"),
            metadata=c.get("metadata", {}),
        )
        for c in raw_chunks
    ]

    return DocumentDetailResponse(document=doc, chunks_sample=chunks)


@router.delete("/{doc_id}", dependencies=[Depends(verify_api_key)])
async def delete_document(
    doc_id: str,
    pipeline: IngestionPipeline = Depends(get_pipeline),
):
    """Deletes a document from the registry and vector database."""
    success = pipeline.delete_document(doc_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{doc_id}' not found.",
        )
    return {"message": f"Document '{doc_id}' and all associated vector chunks deleted successfully."}
