from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Header, HTTPException

from src.core.audit import audit_tool_attempt
from src.core.permissions import decide_tool_allowed
from src.mcp.models import ReadFileRequest, ReadFileResponse
from src.tools.registry import get_tool
# Import tools to ensure they register themselves
import src.tools.read_file  # noqa: F401

router = APIRouter(prefix="/mcp", tags=["mcp"])

REPO_ROOT = Path(__file__).resolve().parents[2]


@router.post("/tools/read_file", response_model=ReadFileResponse)
def mcp_read_file(
    payload: ReadFileRequest,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> ReadFileResponse:
    trace_id = x_trace_id or "NO-TRACE-ID"
    
    # 1. Look up tool in registry
    # (In a generic router, the tool name would come from the URL or body)
    tool_name = "read_file"
    tool = get_tool(tool_name)

    # 2. Check permissions
    decision = decide_tool_allowed(tool.name)
    if not decision.allowed:
        audit_tool_attempt(
            trace_id=trace_id,
            tool_name=tool.name,
            decision="deny",
            reason=decision.reason,
            params_redacted=tool.redact(payload), # type: ignore
            result_summary="blocked",
        )
        raise HTTPException(status_code=403, detail="tool_not_allowed")

    # 3. Execute tool
    # The handler handles its own exceptions and returns a structured response
    resp = tool.handler(repo_root=REPO_ROOT, req=payload)

    # 4. Audit success/failure (based on the tool's response content)
    # We assume the response model has an 'ok' or 'error' field for summary
    if getattr(resp, "ok", True):
        summary = f"ok bytes={getattr(resp, 'bytes', 0)}"
    else:
        summary = f"error {getattr(resp, 'error', 'unknown')}"

    audit_tool_attempt(
        trace_id=trace_id,
        tool_name=tool.name,
        decision="allow",
        reason=decision.reason,
        params_redacted=tool.redact(payload), # type: ignore
        result_summary=summary,
    )
    
    return resp