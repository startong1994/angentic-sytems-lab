from __future__ import annotations

import os

from fastapi.testclient import TestClient

from src.app.main import app


def test_mcp_read_file_denied_by_default() -> None:
    client = TestClient(app)
    os.environ.pop("MCP_ALLOWED_TOOLS", None)

    r = client.post(
        "/mcp/tools/read_file",
        headers={"X-Trace-Id": "DAY5-DENY"},
        json={"path": "data/sample.txt"},
    )
    assert r.status_code == 403


def test_mcp_read_file_allowed() -> None:
    client = TestClient(app)
    os.environ["MCP_ALLOWED_TOOLS"] = "read_file"

    r = client.post(
        "/mcp/tools/read_file",
        headers={"X-Trace-Id": "DAY5-ALLOW"},
        json={"path": "data/sample.txt"},
    )
    # tool runs; may still fail if sample file missing
    assert r.status_code == 200
    body = r.json()
    assert "ok" in body
