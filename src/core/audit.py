from __future__ import annotations

import json
import time
from typing import Any

from src.middleware.logging import logger  


def audit_tool_attempt(
    *,
    trace_id: str,
    tool_name: str,
    decision: str,  # "allow" | "deny"
    reason: str,
    params_redacted: dict[str, Any],
    result_summary: str,
) -> None:
    event = {
        "timestamp_ms": int(time.time() * 1000),
        "event": "tool_attempt",
        "trace_id": trace_id,
        "tool_name": tool_name,
        "decision": decision,
        "reason": reason,
        "params_redacted": params_redacted,
        "result_summary": result_summary,
    }
    # keep it structured and grep-friendly
    logger.info(json.dumps(event, ensure_ascii=False), extra={"trace_id": trace_id})
