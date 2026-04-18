"""we-together MCP server (stdio, JSON-RPC 2.0)。

协议最小子集:
  - initialize
  - tools/list
  - tools/call

工具由 we_together.runtime.adapters.mcp_adapter.build_mcp_tools 提供。
tool_call 分派到 dispatcher，默认包含:
  - we_together_run_turn
  - we_together_graph_summary

启动:
  python scripts/mcp_server.py --root /path/to/data

Claude Code 接入:
  claude mcp add we-together -- python /abs/path/scripts/mcp_server.py --root /abs/data
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.llm import get_llm_client
from we_together.runtime.adapters.mcp_adapter import build_mcp_tools
from we_together.services.chat_service import run_turn


def _graph_summary(root: Path) -> dict:
    db_path = root / "db" / "main.sqlite3"
    if not db_path.exists():
        return {"error": "db not found"}
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT (SELECT COUNT(*) FROM persons WHERE status='active'), "
        "(SELECT COUNT(*) FROM relations WHERE status='active'), "
        "(SELECT COUNT(*) FROM scenes WHERE status='active'), "
        "(SELECT COUNT(*) FROM events), "
        "(SELECT COUNT(*) FROM memories WHERE status='active')"
    ).fetchone()
    conn.close()
    return {
        "person_count": row[0], "relation_count": row[1], "scene_count": row[2],
        "event_count": row[3], "memory_count": row[4],
    }


def _make_dispatcher(root: Path):
    def we_together_graph_summary(args: dict) -> dict:
        return _graph_summary(root)

    def we_together_run_turn(args: dict) -> dict:
        scene_id = args.get("scene_id", "")
        text = args.get("input", "")
        if not scene_id or not text:
            return {"error": "scene_id and input required"}
        db_path = root / "db" / "main.sqlite3"
        result = run_turn(
            db_path=db_path, scene_id=scene_id, user_input=text,
            llm_client=get_llm_client(),
            adapter_name="openai_compat",
        )
        return {"text": result.get("text") or result.get("response_text", ""),
                "event_id": result.get("event_result", {}).get("event_id")}

    return {
        "we_together_graph_summary": we_together_graph_summary,
        "we_together_run_turn": we_together_run_turn,
    }


def handle_request(req: dict, *, dispatcher: dict, tools: list[dict]) -> dict:
    method = req.get("method")
    req_id = req.get("id")
    params = req.get("params") or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "we-together", "version": "0.9.1"},
                "capabilities": {"tools": {}},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id,
                 "result": {"tools": tools}}
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        if name not in dispatcher:
            return {"jsonrpc": "2.0", "id": req_id,
                     "error": {"code": -32601, "message": f"unknown tool: {name}"}}
        try:
            result = dispatcher[name](args)
        except Exception as exc:
            return {"jsonrpc": "2.0", "id": req_id,
                     "error": {"code": -32000, "message": str(exc)}}
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "content": [{"type": "text",
                              "text": json.dumps(result, ensure_ascii=False)}],
                "isError": False,
            },
        }
    return {"jsonrpc": "2.0", "id": req_id,
             "error": {"code": -32601, "message": f"unknown method: {method}"}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    tools = build_mcp_tools()
    dispatcher = _make_dispatcher(root)

    # 按行读 JSON-RPC 消息（简化版：一行一 msg）
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle_request(req, dispatcher=dispatcher, tools=tools)
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
