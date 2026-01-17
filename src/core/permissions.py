from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolDecision:
    allowed: bool
    reason: str


def _parse_allowlist(raw: str) -> set[str]:
    # "read_file,other_tool" -> {"read_file", "other_tool"}
    return {item.strip() for item in raw.split(",") if item.strip()}


def decide_tool_allowed(tool_name: str) -> ToolDecision:
    """
    Deny-by-default allowlist.
    Configure via env var: MCP_ALLOWED_TOOLS=read_file
    """
    allowlist = _parse_allowlist(os.getenv("MCP_ALLOWED_TOOLS", ""))
    if tool_name in allowlist:
        return ToolDecision(allowed=True, reason="allowlisted")
    return ToolDecision(allowed=False, reason="tool_not_allowlisted")
