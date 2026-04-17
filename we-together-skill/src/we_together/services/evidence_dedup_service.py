"""Evidence hash 去重辅助：同一 evidence（基于内容 hash）二次导入时跳过。

SQLite 约束通过 raw_evidence.content_hash（migration 0001 原生有 metadata_json，我们
改走 evidence_hash 辅助表）。为了避免 schema 漂移，这里引入一个轻量辅助表
evidence_hash_registry（与现有 raw_evidence 并存），由 fusion_service 在落库前检查。
"""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from we_together.db.connection import connect


def _ensure_hash_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS evidence_hash_registry (
            content_hash TEXT PRIMARY KEY,
            evidence_id TEXT NOT NULL,
            registered_at TEXT NOT NULL
        )"""
    )


def compute_evidence_hash(content: str, *, source_name: str = "") -> str:
    h = hashlib.sha256()
    h.update((source_name or "").encode("utf-8"))
    h.update(b"||")
    h.update(content.encode("utf-8"))
    return h.hexdigest()


def is_duplicate(db_path: Path, content_hash: str) -> bool:
    conn = connect(db_path)
    _ensure_hash_table(conn)
    row = conn.execute(
        "SELECT evidence_id FROM evidence_hash_registry WHERE content_hash = ?",
        (content_hash,),
    ).fetchone()
    conn.close()
    return row is not None


def register_evidence_hash(
    db_path: Path, content_hash: str, evidence_id: str, registered_at: str,
) -> None:
    conn = connect(db_path)
    _ensure_hash_table(conn)
    conn.execute(
        "INSERT OR IGNORE INTO evidence_hash_registry(content_hash, evidence_id, registered_at) "
        "VALUES(?, ?, ?)",
        (content_hash, evidence_id, registered_at),
    )
    conn.commit()
    conn.close()
