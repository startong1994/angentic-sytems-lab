# Day 1 Proof

## Commands Run
- uv init --no-workspace
- uv python install 3.11
- uv python pin 3.11
- uv add fastapi uvicorn pydantic
- make up

## Outputs
- /healthz returned {"ok":true}
- docker compose logs show uvicorn running

## Offline Drill
- Network disabled (Wi-Fi off)
- make up succeeded
- /healthz still reachable

## Conclusion
PASS
