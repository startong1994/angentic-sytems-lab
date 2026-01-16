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
6. Confirm logs still show JSON output + `trace_id` (and for `/run`, node spans):
   - `docker compose logs --no-log-prefix api | tail -n 200`

## Debug quick hits

- If the API is up but `/healthz` fails:
  - check container logs: `docker compose logs --no-log-prefix api | tail -n 200`
  - confirm the service is listening on `127.0.0.1:8000`
- If logs are not JSON / missing `trace_id`:
  - make a single request (curl `/healthz` or `/run`) and re-check the most recent log lines
- If you need the full timeline for one run:
  - `docker compose logs --no-log-prefix api | grep <TRACE_ID>`
