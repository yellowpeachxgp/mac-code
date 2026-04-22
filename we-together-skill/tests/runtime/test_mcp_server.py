import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from mcp_server import handle_request  # noqa: E402

from we_together.runtime.adapters.mcp_adapter import build_mcp_tools  # noqa: E402


def test_initialize():
    r = handle_request(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
        dispatcher={}, tools=[],
    )
    assert r["id"] == 1
    assert r["result"]["serverInfo"]["name"] == "we-together"


def test_tools_list_returns_we_together_tools():
    tools = build_mcp_tools()
    r = handle_request(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        dispatcher={}, tools=tools,
    )
    names = {t["name"] for t in r["result"]["tools"]}
    assert "we_together_run_turn" in names
    assert "we_together_graph_summary" in names


def test_tools_call_dispatches():
    calls = []
    def _handler(args):
        calls.append(args)
        return {"ok": True}
    r = handle_request(
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "we_together_graph_summary",
                     "arguments": {"scene_id": "s1"}}},
        dispatcher={"we_together_graph_summary": _handler},
        tools=build_mcp_tools(),
    )
    assert r["result"]["isError"] is False
    payload = json.loads(r["result"]["content"][0]["text"])
    assert payload == {"ok": True}
    assert calls[0] == {"scene_id": "s1"}


def test_tools_call_unknown_tool():
    r = handle_request(
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
         "params": {"name": "not_there", "arguments": {}}},
        dispatcher={}, tools=[],
    )
    assert "error" in r
    assert r["error"]["code"] == -32601


def test_unknown_method():
    r = handle_request(
        {"jsonrpc": "2.0", "id": 5, "method": "xxx"},
        dispatcher={}, tools=[],
    )
    assert "error" in r


def test_initialized_notification_returns_no_response():
    r = handle_request(
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        dispatcher={}, tools=[],
    )
    assert r is None
