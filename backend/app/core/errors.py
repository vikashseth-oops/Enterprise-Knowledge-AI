from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}


class AuthenticationError(AppException):
    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
        )


class RateLimitExceededError(AppException):
    def __init__(self, message: str = "Rate limit exceeded. Please retry later."):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
        )


class DocumentParsingError(AppException):
    def __init__(self, filename: str, reason: str):
        super().__init__(
            message=f"Failed to parse document '{filename}': {reason}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="DOCUMENT_PARSE_ERROR",
            details={"filename": filename, "reason": reason},
        )


class EmbeddingError(AppException):
    def __init__(self, message: str = "Failed to generate embeddings"):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="EMBEDDING_ERROR",
        )


class VectorStoreError(AppException):
    def __init__(self, message: str = "Vector database operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="VECTOR_STORE_ERROR",
        )


class LLMServiceError(AppException):
    def __init__(self, message: str = "LLM upstream inference failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="LLM_SERVICE_ERROR",
        )


class DocumentNotFoundError(AppException):
    def __init__(self, doc_id: str):
        super().__init__(
            message=f"Document with ID '{doc_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
            code="DOCUMENT_NOT_FOUND",
            details={"doc_id": doc_id},
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            }
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred.",
                "details": {"exception": str(exc)},
                "request_id": request_id,
            }
        },
    )
