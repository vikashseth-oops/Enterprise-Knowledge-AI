import time
import uuid
from contextlib import asynccontextmanager, contextmanager
from typing import Any

from app.schemas.chat import TraceSpan


class TraceCollector:
    """Collects timed execution spans for LangGraph execution traces."""

    def __init__(self, trace_id: str | None = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.spans: list[TraceSpan] = []
        self._start_wall_time = time.perf_counter()

    def record_span(
        self,
        node: str,
        start_time_ms: float,
        duration_ms: float,
        status: str = "success",
        metadata: dict[str, Any] | None = None,
    ):
        self.spans.append(
            TraceSpan(
                node=node,
                start_time_ms=round(start_time_ms, 2),
                duration_ms=round(duration_ms, 2),
                status=status,
                metadata=metadata or {},
            )
        )

    @contextmanager
    def span(self, node: str, metadata: dict[str, Any] | None = None):
        start = time.perf_counter()
        meta = metadata.copy() if metadata else {}
        status = "success"
        try:
            yield meta
        except Exception as e:
            status = "error"
            meta["error"] = str(e)
            raise
        finally:
            end = time.perf_counter()
            start_ms = (start - self._start_wall_time) * 1000.0
            duration_ms = (end - start) * 1000.0
            self.record_span(node, start_ms, duration_ms, status=status, metadata=meta)

    @asynccontextmanager
    async def async_span(self, node: str, metadata: dict[str, Any] | None = None):
        start = time.perf_counter()
        meta = metadata.copy() if metadata else {}
        status = "success"
        try:
            yield meta
        except Exception as e:
            status = "error"
            meta["error"] = str(e)
            raise
        finally:
            end = time.perf_counter()
            start_ms = (start - self._start_wall_time) * 1000.0
            duration_ms = (end - start) * 1000.0
            self.record_span(node, start_ms, duration_ms, status=status, metadata=meta)

    def get_latency_for_node(self, node: str) -> float:
        total = 0.0
        for s in self.spans:
            if s.node == node:
                total += s.duration_ms
        return round(total, 2)

    def total_latency_ms(self) -> float:
        if not self.spans:
            return 0.0
        return round(sum(s.duration_ms for s in self.spans), 2)
