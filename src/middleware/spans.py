# src/middleware/spans.py

import time
import logging

logger = logging.getLogger(__name__)


class Span:
    def __init__(self, name: str, trace_id: str):
        self.name = name
        self.trace_id = trace_id
        self.start = None

    def __enter__(self):
        self.start = time.time()
        logger.info(
            "span_start",
            extra={
                "trace_id": self.trace_id,
                "span": self.name,
            },
        )
        return self

    def __exit__(self, exc_type, exc, tb):
        duration_ms = int((time.time() - self.start) * 1000)
        status = "error" if exc else "ok"

        logger.info(
            "span_end",
            extra={
                "trace_id": self.trace_id,
                "span": self.name,
                "duration_ms": duration_ms,
                "status": status,
            },
        )
