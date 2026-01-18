from __future__ import annotations

import time

from src.core.audit_models import ToolAttemptEvent
from src.middleware.logging import logger


def audit_tool_attempt(
    *,
    trace_id: str,
    tool_name: str,
    decision: str,  # "allow" | "deny"
    reason: str,
    params_redacted: dict[str, str],
    result_summary: str,
) -> None:
    evt = ToolAttemptEvent(
        timestamp_ms=int(time.time() * 1000),
        trace_id=trace_id,
        tool_name=tool_name,
        decision=decision,  # validated by model
        reason=reason,
        params_redacted=params_redacted,
        result_summary=result_summary,
    )
    logger.info(evt.model_dump_json(), extra={"trace_id": trace_id})
