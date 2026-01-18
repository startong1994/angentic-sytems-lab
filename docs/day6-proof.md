# Day 6 Proof — Tool Registry + Audit Schema Hardening

## Goal

- Add tool registry skeleton (single source of truth for tools).
- Harden audit logging schema for tool attempts (JSON-only, strict shape).
- Confirm read_file guardrails block path traversal under `./data/`.

## Environment

- Local dev on macOS
- Python via uv: CPython 3.11.14

Verify:
```bash
uv run python -V
