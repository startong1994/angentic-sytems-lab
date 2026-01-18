from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Header, HTTPException

from src.core.audit import audit_tool_attempt
from src.core.permissions import decide_tool_allowed
from src.mcp.models import ReadFileRequest, ReadFileResponse
from src.tools.registry import get_tool
import src.tools.read_file  # noqa: F401

router = APIRouter(prefix="/mcp", tags=["mcp"])

REPO_ROOT = Path(__file__).resolve().parents[2]

# Define known safety blocks that should be classified as "blocked", not "error"
GUARDRAIL_BLOCKS = {"path_outside_data_dir", "file_too_large", "file_not_found"}

@router.post("/tools/read_file", response_model=ReadFileResponse)
def mcp_read_file(
    payload: ReadFileRequest,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-Id"),
    x_approval: str | None = Header(default=None, alias="X-Approval"),  # <--- HITL Stub
) -> ReadFileResponse:
    trace_id = x_trace_id or "NO-TRACE-ID"
    tool_name = "read_file"
    tool = get_tool(tool_name)

    # 1. Policy Check (Allowlist)
    decision = decide_tool_allowed(tool.name)
    if not decision.allowed:
        audit_tool_attempt(
            trace_id=trace_id,
            tool_name=tool.name,
            decision="deny",
            reason=decision.reason,
            outcome="blocked",  # Policy blocked it
            params_redacted=tool.redact(payload), # type: ignore
            result_summary="blocked_by_policy",
        )
        raise HTTPException(status_code=403, detail="tool_not_allowed")

    # 2. Approval Check (HITL Stub)
    # Simulate: .secret files require explicit approval
    if payload.path.endswith(".secret") and x_approval != "approved":
        audit_tool_attempt(
            trace_id=trace_id,
            tool_name=tool.name,
            decision="deny",
            reason="approval_required",
            outcome="blocked",  # Policy blocked it
            params_redacted=tool.redact(payload), # type: ignore
            result_summary="missing_approval_header",
        )
        raise HTTPException(status_code=403, detail="approval_required")

    # 3. Execution
    try:
        resp = tool.handler(repo_root=REPO_ROOT, req=payload)
        
        # 4. Outcome Classification
        if getattr(resp, "ok", True):
            outcome = "ok"
            summary = f"bytes={getattr(resp, 'bytes', 0)}"
        else:
            # It failed, but was it a Guardrail (blocked) or a Crash (error)?
            error_msg = getattr(resp, "error", "unknown")
            if error_msg in GUARDRAIL_BLOCKS:
                outcome = "blocked"  # Expected safety mechanism
            else:
                outcome = "error"    # Unexpected failure

            summary = f"error {error_msg}"

        audit_tool_attempt(
            trace_id=trace_id,
            tool_name=tool.name,
            decision="allow",
            reason=decision.reason,
            outcome=outcome,  # <--- Precise Outcome
            params_redacted=tool.redact(payload), # type: ignore
            result_summary=summary,
        )
        return resp

    except Exception as e:
        # 5. Crash Handling
        audit_tool_attempt(
            trace_id=trace_id,
            tool_name=tool.name,
            decision="allow",
            reason=decision.reason,
            outcome="error",
            params_redacted=tool.redact(payload), # type: ignore
            result_summary=f"crash {str(e)}",
        )
        raise e