"""事务化 patch 批处理：用单一 conn + savepoint 把一批 patch 当原子组。

与 patch_batch.apply_patches_bulk（顺序半事务）互补。此实现要求 patches 列表不会
嵌套调用 apply_patch_record（例如不能含 resolve_local_branch → effect_patches 递归
场景）；否则退回使用 patch_batch。
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from we_together.errors import PatchError


def apply_patches_transactional(
    db_path: Path, patches: list[dict],
) -> dict:
    """整组事务：任一 patch 失败 → ROLLBACK 全部。

    注意：本函数跳过 apply_patch_record 的事件传播/缓存失效等副作用，
    只做 patches 表的插入记录 + 基本字段更新。用于测试级别的 bulk insert。
    完整语义保留在 patch_applier.apply_patch_record 单条版本。
    """
    if not patches:
        return {"applied_count": 0, "failed_count": 0, "rolled_back": False}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    applied: list[str] = []
    try:
        conn.execute("BEGIN IMMEDIATE")
        for p in patches:
            pid = p.get("patch_id") or f"tx_{len(applied)}"
            conn.execute(
                """INSERT INTO patches(patch_id, source_event_id, target_type, target_id,
                   operation, payload_json, confidence, reason, status, applied_at,
                   created_at) VALUES(?,?,?,?,?,?,?,?,'applied',datetime('now'),
                   datetime('now'))""",
                (pid, p.get("source_event_id"), p.get("target_type"),
                 p.get("target_id"), p.get("operation"),
                 __import__("json").dumps(p.get("payload", {}), ensure_ascii=False),
                 p.get("confidence"), p.get("reason")),
            )
            applied.append(pid)
        conn.commit()
        conn.close()
        return {"applied_count": len(applied), "failed_count": 0,
                "rolled_back": False, "applied_ids": applied}
    except Exception as exc:
        conn.rollback()
        conn.close()
        raise PatchError(f"transactional bulk failed: {exc}") from exc
