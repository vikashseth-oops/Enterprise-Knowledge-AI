import hashlib
import threading
import time
from collections import OrderedDict
from typing import Any

from app.config import settings


class TTLLRUCache:
    """Thread-safe in-memory LRU cache with time-to-live expiration."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = threading.Lock()

    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Any | None:
        if not settings.CACHE_ENABLED:
            return None
        hashed = self._hash_key(key)
        now = time.time()
        with self._lock:
            if hashed not in self._cache:
                return None
            timestamp, value = self._cache[hashed]
            if now - timestamp > self.ttl_seconds:
                del self._cache[hashed]
                return None
            # Move to end (most recently used)
            self._cache.move_to_end(hashed)
            return value

    def set(self, key: str, value: Any):
        if not settings.CACHE_ENABLED:
            return
        hashed = self._hash_key(key)
        now = time.time()
        with self._lock:
            if hashed in self._cache:
                self._cache.move_to_end(hashed)
            self._cache[hashed] = (now, value)
            if len(self._cache) > self.max_size:
                # Evict oldest item
                self._cache.popitem(last=False)

    def clear(self):
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._cache)


query_cache = TTLLRUCache(
    max_size=settings.CACHE_MAX_ENTRIES,
    ttl_seconds=settings.CACHE_TTL_SECONDS,
)
