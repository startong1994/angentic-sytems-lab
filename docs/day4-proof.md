# Day 4 Proof — FastAPI ↔ LangGraph wiring + trace propagation

## Middleware (trace_id)
- Reads `X-Trace-Id` or generates one
- Stores on `request.state.trace_id`

<PASTE middleware snippet>

## Endpoint: POST /run
- Injects trace_id into GraphState
- Runs graph synchronously
- Returns only {trace_id, status, result}

<PASTE endpoint snippet>

## Success run
Command:
curl -sS -X POST http://127.0.0.1:8000/run \
  -H 'Content-Type: application/json' \
  -H 'X-Trace-Id: TEST-OK' \
  -d '{"input":"hello"}'

Response:
{"trace_id":"TEST-OK","status":"done","result":"ok:hello"}

Logs (timeline):
docker compose logs --no-log-prefix api | grep TEST-OK

<PASTE the plan/verify/finish node_start/node_end lines with node + duration_ms>

## Failure run
Command:
curl -sS -X POST http://127.0.0.1:8000/run \
  -H 'Content-Type: application/json' \
  -H 'X-Trace-Id: TEST-FAIL' \
  -d '{"input":"fail"}'

Response:
{"trace_id":"TEST-FAIL","status":"error","result":null}

Logs (exception includes node + trace_id):
docker compose logs --no-log-prefix api | grep TEST-FAIL

<PASTE the 3 lines you captured (node_start plan, node_end error plan, run_error)>

## Offline drill
Command:
curl -sS -X POST http://127.0.0.1:8000/run \
  -H 'Content-Type: application/json' \
  -H 'X-Trace-Id: OFFLINE-OK' \
  -d '{"input":"hello"}'

Response:
{"trace_id":"OFFLINE-OK","status":"done","result":"ok:hello"}

Logs:
docker compose logs --no-log-prefix api | grep OFFLINE-OK

<PASTE the OFFLINE-OK node timeline lines>

## Conclusion
PASS
