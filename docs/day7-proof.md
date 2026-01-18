# Day 7 Proof — Audit Outcome + No-Bypass Tool Execution

## Goal

- Separate **policy** vs **execution** in tool audit logs:
  - `decision`: `allow|deny` (policy)
  - `outcome`: `ok|blocked|error` (execution)
- Add a minimal HITL **approval stub** gate.
- Prove **no bypass**: when blocked by policy/approval, the tool handler is not executed.

## Environment

- Python: 3.11.14 (uv)
- Tests: pytest

## Changes Shipped

1) Audit model updated: `ToolAttemptEvent` includes `outcome`.
2) Audit logger requires and emits `outcome`.
3) MCP router:
   - Allowlist check blocks early (`decision=deny`, `outcome=blocked`)
   - Approval stub blocks `.secret` access without `X-Approval: approved` (`decision=deny`, `outcome=blocked`)
   - Guardrail errors (e.g. `path_outside_data_dir`) classify as `outcome=blocked` (not `error`)
4) Tests:
   - Approval block proves handler not called (no bypass)
   - Guardrail path proves handler runs exactly once and returns a blocked outcome

## Evidence

### 1) Tests: no bypass + guardrail handler execution

Command:
```bash
uv run pytest tests/test_day7_no_bypass.py -v
