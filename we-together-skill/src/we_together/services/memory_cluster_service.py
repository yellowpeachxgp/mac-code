"""记忆聚类：按 memory_type + owners 重叠度把 active memory 分组。

算法：
  1. 拉所有 active memory + memory_owners
  2. 按 memory_type 分桶
  3. 桶内按 owner set 的 Jaccard 相似度 >= threshold 做 union-find
  4. 输出 size >= min_cluster_size 的 cluster

返回：list[{cluster_id, memory_type, memory_ids, owner_ids, size}]
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from we_together.db.connection import connect


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


class _DSU:
    def __init__(self, items: list[str]) -> None:
        self.parent = {x: x for x in items}

    def find(self, x: str) -> str:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def cluster_memories(
    db_path: Path,
    *,
    min_cluster_size: int = 2,
    owner_overlap_threshold: float = 0.5,
) -> list[dict]:
    conn = connect(db_path)
    conn.row_factory = sqlite3.Row
    mem_rows = conn.execute(
        "SELECT memory_id, memory_type FROM memories WHERE status = 'active'"
    ).fetchall()
    owner_rows = conn.execute(
        "SELECT memory_id, owner_id FROM memory_owners WHERE owner_type = 'person'"
    ).fetchall()
    conn.close()

    owners_by_mid: dict[str, set[str]] = {}
    for r in owner_rows:
        owners_by_mid.setdefault(r["memory_id"], set()).add(r["owner_id"])

    by_type: dict[str, list[str]] = {}
    for r in mem_rows:
        by_type.setdefault(r["memory_type"], []).append(r["memory_id"])

    results: list[dict] = []
    cluster_seq = 0
    for mtype, mids in by_type.items():
        dsu = _DSU(mids)
        for i, a in enumerate(mids):
            owners_a = owners_by_mid.get(a, set())
            for b in mids[i + 1:]:
                owners_b = owners_by_mid.get(b, set())
                if _jaccard(owners_a, owners_b) >= owner_overlap_threshold:
                    dsu.union(a, b)
        groups: dict[str, list[str]] = {}
        for mid in mids:
            groups.setdefault(dsu.find(mid), []).append(mid)
        for root, members in groups.items():
            if len(members) < min_cluster_size:
                continue
            owners_union: set[str] = set()
            for mid in members:
                owners_union |= owners_by_mid.get(mid, set())
            cluster_seq += 1
            results.append({
                "cluster_id": f"cluster_{mtype}_{cluster_seq}",
                "memory_type": mtype,
                "memory_ids": members,
                "owner_ids": sorted(owners_union),
                "size": len(members),
            })

    return results
