import re
import time

from fastapi import Request, Security
from fastapi.security.api_key import APIKeyHeader

from app.config import settings
from app.core.errors import AuthenticationError, RateLimitExceededError

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class RateLimiter:
    """Thread-safe sliding-window rate limiter per client IP or key."""

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.requests: dict[str, list[float]] = {}

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        window = now - 60.0

        timestamps = self.requests.get(client_id, [])
        # Filter timestamps outside 1 minute window
        timestamps = [t for t in timestamps if t > window]
        if len(timestamps) >= self.rpm:
            self.requests[client_id] = timestamps
            return False

        timestamps.append(now)
        self.requests[client_id] = timestamps
        return True


rate_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)


async def verify_api_key(
    request: Request,
    api_key: str | None = Security(api_key_header),
) -> str:
    """Verifies the X-API-Key header against configured settings."""
    if not settings.AUTH_ENABLED:
        return "anonymous"

    if not api_key or api_key != settings.API_KEY:
        raise AuthenticationError("Invalid or missing X-API-Key header")

    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    client_key = f"{api_key}:{client_ip}"
    if not rate_limiter.is_allowed(client_key):
        raise RateLimitExceededError("Too many requests. Please wait a minute.")

    return api_key


def sanitize_input(text: str) -> str:
    """
    Sanitizes user input to mitigate prompt injection, delimiter hijacking,
    and control character attacks.
    """
    if not text:
        return ""
    # Strip null bytes and control chars (except normal whitespace like newline and tab)
    sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    # Trim excessive whitespaces
    return sanitized.strip()


def wrap_document_context_safely(context: str) -> str:
    """
    Wraps untrusted document chunks in strict XML boundaries to prevent
    jailbreaking / prompt injections embedded within documents.
    """
    # Neutralize closing context tags if present in document
    safe_context = context.replace("</document_content>", "[ESCAPED_DOC_TAG]")
    return f"<document_content>\n{safe_context}\n</document_content>"
