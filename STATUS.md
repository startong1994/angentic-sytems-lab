# STATUS

## What this repo guarantees (Plan C invariants)

- Python 3.11 + uv
- Docker / docker compose (via `make up`)
- FastAPI
- Pydantic v2 (strict=True)
- LangGraph
- Qdrant (pgvector only as fallback)

## Last shipped (evidence pointers)

- Day 1 — Repo boots via `make up`; `/healthz` verified; offline drill passed  
  Evidence: `docs/day1-proof.md`

- Day 2 — Request-scoped `trace_id` + JSON-only structured logging (with manual spans)  
  Evidence: `docs/day2-proof.md`

- Day 3 — LangGraph skeleton (bounded loop, no tools) + determinism test (uv / Py3.11)  
  Evidence: `docs/day3-proof.md`

- Day 4 — FastAPI `/run` wired to LangGraph + end-to-end trace propagation + node span logs + failure path + offline drill  
  Evidence: `docs/day4-proof.md`

- Day 5 — MCP spike: read-only tool endpoint + deny-by-default allowlist + audited tool attempts (allow + deny) with `trace_id`  
  Evidence: `docs/day5-proof.md`

## How to run (fresh machine)

1. Install Docker Desktop (macOS)
2. Ensure Docker daemon is running
3. Clone repo
4. Install uv
5. Pre-pull images (optional but recommended)
6. Run: `make up`
7. Verify: `curl http://127.0.0.1:8000/healthz`
8. Run tests: `uv run pytest -q`

## Run graph via API

POST `/run`

- Header: `X-Trace-Id` (optional; if omitted, middleware generates one)
- Body: `{"input":"hello"}`
- Response: `{"trace_id":"...","status":"done|error","result":"..."|null}`

Trace propagation path:
HTTP -> middleware -> `request.state.trace_id` -> `GraphState.trace_id` -> node logs

Debug by trace_id:
- `docker compose logs --no-log-prefix api | grep <TRACE_ID>`

## MCP (Day 5)

POST `/mcp/tools/read_file`

- Purpose: minimal MCP-style read-only tool (offline-safe; reads under `./data/`)
- Allowlist env: `MCP_ALLOWED_TOOLS=read_file` (deny-by-default when unset/empty)
- Body: `{"path":"data/sample.txt"}`
- Example (allowed):
  - `curl -sS -X POST http://127.0.0.1:8000/mcp/tools/read_file -H 'Content-Type: application/json' -H 'X-Trace-Id: DEMO' -d '{"path":"data/sample.txt"}'`

Audit behavior:
- Every tool attempt emits a JSON audit event `event="tool_attempt"` including:
  - `trace_id`, `tool_name`, `decision="allow|deny"`, `reason`, `params_redacted`, `result_summary`
- Denied attempts return HTTP 403 with `{"detail":"tool_not_allowed"}`

## Verify (expected behavior)

- `GET /healthz` returns success
- `POST /run` returns a `RunResponse` with `{trace_id, status, result}`
- After any request, application logs emit JSON entries that include a request-scoped `trace_id`
- For `/run`, logs include node timeline spans:
  - `event`: `node_start` / `node_end`
  - `trace_id`
  - `node` (e.g., `plan`, `verify`, `finish`)
  - `status`
  - `duration_ms`

MCP verification:
- With `MCP_ALLOWED_TOOLS=read_file`:
  - `POST /mcp/tools/read_file` returns `{"ok":true,...}` for `data/sample.txt`
- With allowlist unset/empty:
  - `POST /mcp/tools/read_file` returns HTTP 403 `{"detail":"tool_not_allowed"}`
- Logs show `tool_attempt` events for both allow and deny:
  - `docker compose logs --no-log-prefix api | grep <TRACE_ID>`

Failure path:
- If input == `"fail"`, API still returns HTTP 200 with:
  - `{"trace_id":"...","status":"error","result":null}`
- Logs include exception + `node` + `trace_id`

## Offline drill (exercise-level)

Goal: after caching deps/images, the system should boot with network disabled.

1. While online: pre-pull/build everything you need (e.g. run `make up` once successfully)
2. Disable network (system-wide)
3. Run: `make up`
4. Verify: `curl http://127.0.0.1:8000/healthz`
5. Verify `/run` still works:
   - `curl -sS -X POST http://127.0.0.1:8000/run -H 'Content-Type: application/json' -d '{"input":"hello"}'`
6. (Optional) Verify MCP still works offline (local file under `./data/`):
   - `curl -sS -X POST http://127.0.0.1:8000/mcp/tools/read_file -H 'Content-Type: application/json' -d '{"path":"data/sample.txt"}'`
7. Confirm logs still show JSON output + `trace_id` (and for `/run`, node spans):
   - `docker compose logs --no-log-prefix api | tail -n 200`

## Debug quick hits

- If the API is up but `/healthz` fails:
  - check container logs: `docker compose logs --no-log-prefix api | tail -n 200`
  - confirm the service is listening on `127.0.0.1:8000`
- If logs are not JSON / missing `trace_id`:
  - make a single request (curl `/healthz` or `/run`) and re-check the most recent log lines
- If you need the full timeline for one run:
  - `docker compose logs --no-log-prefix api | grep <TRACE_ID>`
