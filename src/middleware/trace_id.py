import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

TRACE_HEADER = "X-Trace-Id"


class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        incoming = request.headers.get(TRACE_HEADER)
        trace_id = incoming if incoming else str(uuid.uuid4())
        request.state.trace_id = trace_id

        response = await call_next(request)
        response.headers[TRACE_HEADER] = trace_id
        return response
