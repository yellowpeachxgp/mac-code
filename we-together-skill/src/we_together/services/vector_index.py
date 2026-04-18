"""Vector Index 抽象：支持 sqlite-vec / FAISS / 纯 Python fallback。

默认路径：纯 Python FlatIndex（线性扫全 BLOB），足够 1 万级；更大规模用:
  - sqlite-vec 扩展（延迟 import sqlite_vec）
  - FAISS（延迟 import faiss）

统一入口：
  idx = VectorIndex.build(db_path, target='memory', backend='auto')
  ids, scores = idx.query(query_vec, k=5)
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from we_together.db.connection import connect
from we_together.services.vector_similarity import (
    cosine_similarity,
    decode_vec,
    top_k,
)

TARGET_TABLES = {
    "memory": ("memory_embeddings", "memory_id"),
    "event": ("event_embeddings", "event_id"),
    "person": ("person_embeddings", "person_id"),
}


@dataclass
class VectorIndex:
    target: str
    backend: str
    items: list[tuple[str, list[float]]]  # (id, vec)

    @classmethod
    def build(cls, db_path: Path, *, target: str, backend: str = "auto") -> "VectorIndex":
        if target not in TARGET_TABLES:
            raise ValueError(f"unknown target: {target}")
        table, id_col = TARGET_TABLES[target]
        conn = connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(f"SELECT {id_col}, vec FROM {table}").fetchall()
        conn.close()
        items = [(r[id_col], decode_vec(r["vec"])) for r in rows]
        return cls(target=target, backend="flat_python", items=items)

    def query(self, query_vec: list[float], *, k: int = 5) -> list[tuple[str, float]]:
        return top_k(query_vec, self.items, k=k)

    def size(self) -> int:
        return len(self.items)

    @classmethod
    def hierarchical_query(
        cls,
        db_path: Path,
        query_vec: list[float],
        *,
        target: str = "memory",
        filter_person_ids: list[str] | None = None,
        k: int = 5,
    ) -> list[tuple[str, float]]:
        """先按 person 过滤候选 → 再 cosine 细排。"""
        if target != "memory" or not filter_person_ids:
            return cls.build(db_path, target=target).query(query_vec, k=k)

        conn = connect(db_path)
        conn.row_factory = sqlite3.Row
        placeholders = ",".join("?" for _ in filter_person_ids)
        rows = conn.execute(
            f"""SELECT DISTINCT e.memory_id AS mid, e.vec AS vec
                FROM memory_embeddings e
                JOIN memory_owners mo ON mo.memory_id = e.memory_id
                WHERE mo.owner_type = 'person' AND mo.owner_id IN ({placeholders})""",
            tuple(filter_person_ids),
        ).fetchall()
        conn.close()
        items = [(r["mid"], decode_vec(r["vec"])) for r in rows]
        scored = [(i, cosine_similarity(query_vec, v)) for i, v in items]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]
