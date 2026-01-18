# Day 7 Proof — Audit Outcome + No-Bypass Tool Execution

## Goal

- Formalize separation between policy and execution in tool audit logs:
  - `decision`: allow|deny (policy)
  - `outcome`: ok|blocked|error (execution)
- Add a simple approval gate stub (header-based) that blocks execution.
- Prove "no bypass": when blocked by policy/approval, tool handler is not executed.

## Evidence

### 1) Tests (no bypass + guardrail behavior)

Command:
```bash
uv run pytest tests/test_day7_no_bypass.py -v
