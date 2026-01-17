# Day 5 Proof — MCP spike (read-only tool) + permission scaffold + audit logs

## Goal
Ship a minimal MCP-style endpoint with deny-by-default allowlist and audited tool attempts (trace_id).

## Evidence — Allowed call (allowlisted)
Command:
```bash
curl -sS -X POST http://127.0.0.1:8000/mcp/tools/read_file \
  -H 'Content-Type: application/json' \
  -H 'X-Trace-Id: DAY5-ALLOW' \
  -d '{"path":"data/sample.txt"}'
