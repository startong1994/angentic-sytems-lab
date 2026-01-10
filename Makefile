up:
	docker compose up --build

dev:
	uv run uvicorn src.app.main:app --reload

test:
	echo "no tests yet"
