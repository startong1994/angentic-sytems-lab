# src/middleware/logging.py

import json
import logging
import time
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse

SERVICE_NAME = "agentic-systems-lab"
TRACE_HEADER = "X-Trace-Id"


class JsonFormatter(logging.Formatter):
    """
    JSON-only, defensive formatter.
    - Always emits JSON
    - Never raises during formatting (falls back to minimal JSON)
    - Supports optional fields via LogRecord attributes set in `extra=...`
    """

    def format(self, record: logging.LogRecord) -> str:
        try:
            payload: dict[str, Any] = {
                "timestamp": int(time.time() * 1000),
                "level": record.levelname,
                "service": SERVICE_NAME,
                "event": record.getMessage(),
                "trace_id": getattr(record, "trace_id", None),
            }

            # Optional fields that may appear on certain events.
            for k in ("span", "duration_ms", "status", "status_code", "latency_ms","node"):
                v = getattr(record, k, None)
                if v is not None:
                    payload[k] = v

            # Exception details (stack trace) when logger.exception(...) is used.
            if record.exc_info:
                payload["exc"] = self.formatException(record.exc_info)

            return json.dumps(payload, default=str)
        except Exception as e:
            # Never let formatting failure crash logging.
            fallback = {
                "timestamp": int(time.time() * 1000),
                "level": "ERROR",
                "service": SERVICE_NAME,
                "event": "log_format_error",
                "trace_id": getattr(record, "trace_id", None),
                "error": str(e),
                "orig_event": getattr(record, "msg", None),
            }
            return json.dumps(fallback, default=str)


def configure_logging() -> None:
    """
    Configure root logger to emit JSON logs to stdout.

    Notes:
    - Clears existing handlers to avoid duplicated logs.
    - Disables uvicorn loggers so we don't get non-JSON access/error logs.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = []
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    # Make the app the single source of truth for logs (Day 2 hard gate).
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = []
        lg.propagate = False
        lg.disabled = True


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs request_start / request_end for every request in JSON with trace_id.
    On exceptions:
      - logs request_error with stack trace
      - returns a 500 response that includes X-Trace-Id header
    """

    async def dispatch(self, request: Request, call_next):
        start = time.time()

        def get_trace_id() -> str | None:
            # Source of truth is request.state.trace_id (set by TraceIdMiddleware).
            # Header fallback is read-only to avoid nulls during edge cases.
            return getattr(request.state, "trace_id", None) or request.headers.get(TRACE_HEADER)

        logger.info("request_start", extra={"trace_id": get_trace_id()})

        try:
            response = await call_next(request)
        except Exception:
            trace_id = get_trace_id()
            logger.exception("request_error", extra={"trace_id": trace_id})

            resp = PlainTextResponse("Internal Server Error", status_code=500)
            if trace_id:
                resp.headers[TRACE_HEADER] = trace_id
            return resp

        duration_ms = int((time.time() - start) * 1000)
        logger.info(
            "request_end",
            extra={
                "trace_id": get_trace_id(),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        # Ensure trace header exists even if upstream middleware is misordered.
        trace_id = get_trace_id()
        if trace_id:
            response.headers.setdefault(TRACE_HEADER, trace_id)

        return response
