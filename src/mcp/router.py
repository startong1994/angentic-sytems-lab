from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Header, HTTPException

from src.core.audit import audit_tool_attempt
from src.core.permissions import decide_tool_allowed
from src.mcp.models import ReadFileRequest, ReadFileResponse
from src.tools.read_file import ReadFileError, read_file_safe

router = APIRouter(prefix="/mcp", tags=["mcp"])

REPO_ROOT = Path(__file__).resolve().parents[2]  # .../src/mcp/router.py -> repo root


@router.post("/tools/read_file", response_model=ReadFileResponse)
def mcp_read_file(
    payload: ReadFileRequest,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
) -> ReadFileResponse:
    trace_id = x_trace_id or "NO-TRACE-ID"
    tool_name = "read_file"

    decision = decide_tool_allowed(tool_name)
    if not decision.allowed:
        audit_tool_attempt(
            trace_id=trace_id,
            tool_name=tool_name,
            decision="deny",
            reason=decision.reason,
            params_redacted={"path": payload.path},
            result_summary="blocked",
        )
        raise HTTPException(status_code=403, detail="tool_not_allowed")

    try:
        result = read_file_safe(repo_root=REPO_ROOT, relative_path=payload.path)
        audit_tool_attempt(
            trace_id=trace_id,
            tool_name=tool_name,
            decision="allow",
            reason=decision.reason,
            params_redacted={"path": payload.path},
            result_summary=f"ok bytes={result.bytes}",
        )
        return ReadFileResponse(ok=True, bytes=result.bytes, preview=result.preview)
    except ReadFileError as e:
        audit_tool_attempt(
            trace_id=trace_id,
            tool_name=tool_name,
            decision="allow",
            reason=decision.reason,
            params_redacted={"path": payload.path},
            result_summary=f"error {str(e)}",
        )
        return ReadFileResponse(ok=False, error=str(e))
