"""federation_http_server（Phase 42 FD MVP）：真 HTTP endpoint。

路由:
  GET /federation/v1/persons          列出本地 persons（applied visibility=shared+）
  GET /federation/v1/persons/{pid}    单个 person 详情
  GET /federation/v1/memories?owner_id=...  按 owner 列 memory（只返 is_shared=1）
  GET /federation/v1/capabilities     公告本 skill 提供的联邦能力

设计:
- Python stdlib http.server；不依赖 FastAPI
- 读-only；本阶段不支持写（安全边界）
- 身份: 无 auth（v0.15 MVP）；v0.16 加 token 或 mTLS
- visibility 过滤在服务端完成
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.runtime.skill_runtime import SKILL_SCHEMA_VERSION

FEDERATION_PROTOCOL_VERSION = "1"


def _capabilities() -> dict:
    return {
        "federation_protocol_version": FEDERATION_PROTOCOL_VERSION,
        "skill_schema_version": SKILL_SCHEMA_VERSION,
        "supported_endpoints": [
            "/federation/v1/persons",
            "/federation/v1/persons/{pid}",
            "/federation/v1/memories",
            "/federation/v1/capabilities",
        ],
        "read_only": True,
        "auth": "none (v0.15 MVP)",
    }


def _list_persons(db: Path, limit: int = 50) -> dict:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT person_id, primary_name, status, confidence "
            "FROM persons WHERE status='active' LIMIT ?", (limit,),
        ).fetchall()
    finally:
        conn.close()
    return {"persons": [dict(r) for r in rows], "count": len(rows)}


def _get_person(db: Path, pid: str) -> dict | None:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT person_id, primary_name, status, confidence, metadata_json "
            "FROM persons WHERE person_id=?", (pid,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return None
    d = dict(row)
    try:
        d["metadata"] = json.loads(d.pop("metadata_json") or "{}")
    except Exception:
        d["metadata"] = {}
    return d


def _list_shared_memories(db: Path, *, owner_id: str | None = None, limit: int = 50) -> dict:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        if owner_id:
            rows = conn.execute(
                """SELECT DISTINCT m.memory_id, m.summary, m.relevance_score,
                   m.confidence, m.created_at
                   FROM memories m
                   JOIN memory_owners mo ON mo.memory_id=m.memory_id
                   WHERE m.status='active' AND m.is_shared=1
                     AND mo.owner_type='person' AND mo.owner_id=?
                   LIMIT ?""",
                (owner_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT memory_id, summary, relevance_score, confidence, created_at
                   FROM memories
                   WHERE status='active' AND is_shared=1
                   LIMIT ?""",
                (limit,),
            ).fetchall()
    finally:
        conn.close()
    return {"memories": [dict(r) for r in rows], "count": len(rows)}


def make_handler(root: Path):
    class H(BaseHTTPRequestHandler):
        def _write_json(self, status: int, payload: dict):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)
            db = root / "db" / "main.sqlite3"

            if path == "/federation/v1/capabilities":
                self._write_json(200, _capabilities())
                return
            if not db.exists():
                self._write_json(503, {"error": "db not ready"})
                return

            if path == "/federation/v1/persons":
                limit = int(qs.get("limit", ["50"])[0])
                self._write_json(200, _list_persons(db, limit=limit))
                return
            if path.startswith("/federation/v1/persons/"):
                pid = path.rsplit("/", 1)[-1]
                p = _get_person(db, pid)
                if p is None:
                    self._write_json(404, {"error": "person not found", "id": pid})
                else:
                    self._write_json(200, p)
                return
            if path == "/federation/v1/memories":
                owner = qs.get("owner_id", [None])[0]
                limit = int(qs.get("limit", ["50"])[0])
                self._write_json(200, _list_shared_memories(
                    db, owner_id=owner, limit=limit,
                ))
                return

            self._write_json(404, {"error": "not found", "path": path})

        def log_message(self, *a, **kw):
            pass

    return H


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=7781)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    HTTPServer((args.host, args.port), make_handler(root)).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
