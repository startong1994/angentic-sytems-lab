import os
from unittest.mock import Mock
from fastapi.testclient import TestClient
from src.app.main import app
import src.tools.read_file  # ensure registration

from src.tools.registry import get_tool
import src.tools.registry as registry

client = TestClient(app)

# Helper to spy on the tool handler
def spy_on_handler(tool_name: str) -> dict:
    """
    Replaces the tool handler in the registry with a wrapper that counts calls.
    Returns a dictionary {'n': count} that updates in real-time.
    """
    spec = get_tool(tool_name)
    real_handler = spec.handler
    calls = {"n": 0}

    def wrapped_handler(*args, **kwargs):
        calls["n"] += 1
        return real_handler(*args, **kwargs)

    # Patch the registry entry safely
    registry._REGISTRY[tool_name] = type(spec)(
        name=spec.name,
        request_model=spec.request_model,
        response_model=spec.response_model,
        handler=wrapped_handler,
        redact=spec.redact,
        # Preserve extra fields if they exist
        **({ "requires_approval": getattr(spec, "requires_approval") } if hasattr(spec, "requires_approval") else {}),
    )
    return calls

# TEST 1: The Guardrail Test (Allowed by Router, Blocked by Tool)
def test_guardrail_runs_handler_but_blocks(monkeypatch):
    monkeypatch.setenv("MCP_ALLOWED_TOOLS", "read_file")
    calls = spy_on_handler("read_file")

    resp = client.post(
        "/mcp/tools/read_file",
        json={"path": "../../etc/passwd"},
        headers={"X-Trace-Id": "TEST-GUARDRAIL"},
    )

    assert resp.status_code == 200
    assert resp.json()["ok"] is False
    assert resp.json()["error"] == "path_outside_data_dir"
    assert calls["n"] == 1  # PROOF: Router let it through, Tool stopped it.

# TEST 2: The Policy Spy Test (Blocked by Router, Tool NEVER runs)
def test_approval_gate_blocks_execution(monkeypatch):
    monkeypatch.setenv("MCP_ALLOWED_TOOLS", "read_file")
    calls = spy_on_handler("read_file")

    # Attempt to access a .secret file without the X-Approval header
    resp = client.post(
        "/mcp/tools/read_file",
        json={"path": "data/plans.secret"},
        headers={"X-Trace-Id": "TEST-POLICY"},
    )

    assert resp.status_code == 403
    assert resp.json()["detail"] == "approval_required"
    assert calls["n"] == 0  # PROOF: Code never ran. Layer 1 blocked it.

# TEST 3: The Happy Path (Allowed by Router, Allowed by Tool)
def test_happy_path_works(monkeypatch):
    monkeypatch.setenv("MCP_ALLOWED_TOOLS", "read_file")
    calls = spy_on_handler("read_file")

    resp = client.post(
        "/mcp/tools/read_file",
        json={"path": "data/sample.txt"},
        headers={"X-Trace-Id": "TEST-HAPPY"},
    )

    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert resp.json()["bytes"] > 0
    assert calls["n"] == 1  # PROOF: It ran successfully.