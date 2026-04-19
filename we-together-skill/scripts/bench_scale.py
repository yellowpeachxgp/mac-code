"""scripts/bench_scale.py — 合成 N 条 memory 跑 embedding 检索压测。

用法:
  python scripts/bench_scale.py --root . --n 10000 --dim 32

输出:
  {
    "n": 10000, "dim": 32, "build_s": 0.xx, "query_s": 0.xx, "qps": xxx
  }
"""
from __future__ import annotations

import argparse
import json
import platform
import sqlite3
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.llm.providers.embedding import MockEmbeddingClient
from we_together.services.vector_index import VectorIndex
from we_together.services.vector_similarity import encode_vec


def seed_synthetic(db: Path, *, n: int, dim: int) -> None:
    conn = sqlite3.connect(db)
    client = MockEmbeddingClient(dim=dim)
    try:
        conn.execute("PRAGMA synchronous=OFF")
        conn.execute("BEGIN")
        now = "2026-04-19T00:00:00Z"
        for i in range(n):
            mid = f"m_bench_{i}_{uuid.uuid4().hex[:6]}"
            txt = f"memory {i}"
            vec = client.embed([txt])[0]
            conn.execute(
                """INSERT INTO memories(memory_id, memory_type, summary, relevance_score,
                   confidence, is_shared, status, metadata_json, created_at, updated_at)
                   VALUES(?, 'shared_memory', ?, 0.5, 0.5, 1, 'active', '{}', ?, ?)""",
                (mid, txt, now, now),
            )
            conn.execute(
                """INSERT INTO memory_embeddings(memory_id, model_name, dim, vec, created_at)
                   VALUES(?, ?, ?, ?, ?)""",
                (mid, client.provider, client.dim, encode_vec(vec), now),
            )
        conn.commit()
    finally:
        conn.close()


def _format_n_label(n: int) -> str:
    if n >= 1_000_000 and n % 1_000_000 == 0:
        return f"{n // 1_000_000}m"
    if n >= 1_000 and n % 1_000 == 0:
        return f"{n // 1_000}k"
    return str(n)


def build_report(
    *,
    backend: str,
    n_seeded: int,
    dim: int,
    seed_s: float,
    build_s: float,
    index_size: int,
    queries: int,
    query_total_s: float,
) -> dict:
    per_query_ms = (query_total_s / queries) * 1000 if queries > 0 else 0.0
    qps = queries / query_total_s if query_total_s > 0 else 0.0
    return {
        "backend": backend,
        "n_seeded": n_seeded,
        "dim": dim,
        "seed_s": round(seed_s, 3),
        "build_s": round(build_s, 3),
        "index_size": index_size,
        "queries": queries,
        "query_total_s": round(query_total_s, 3),
        "per_query_ms": round(per_query_ms, 2),
        "qps": round(qps, 1),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "generated_at": datetime.now(UTC).isoformat(),
    }


def archive_report(report: dict, bench_dir: Path) -> Path:
    bench_dir.mkdir(parents=True, exist_ok=True)
    n_label = _format_n_label(int(report["n_seeded"]))
    backend = str(report["backend"])
    ts = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    path = bench_dir / f"bench_{n_label}_{backend}_{ts}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--dim", type=int, default=32)
    ap.add_argument("--queries", type=int, default=50)
    ap.add_argument("--backend", default="flat_python")
    ap.add_argument("--archive", action="store_true")
    ap.add_argument("--archive-dir", default=None)
    args = ap.parse_args()

    db = Path(args.root).resolve() / "db" / "main.sqlite3"
    if not db.exists():
        print(json.dumps({"error": "db not found"}))
        return 1

    t0 = time.perf_counter()
    seed_synthetic(db, n=args.n, dim=args.dim)
    seed_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    idx = VectorIndex.build(db, target="memory", backend=args.backend)
    build_s = time.perf_counter() - t0

    client = MockEmbeddingClient(dim=args.dim)
    qv = client.embed(["query"])[0]

    t0 = time.perf_counter()
    for _ in range(args.queries):
        idx.query(qv, k=10)
    q_total_s = time.perf_counter() - t0
    report = build_report(
        backend=idx.backend,
        n_seeded=args.n,
        dim=args.dim,
        seed_s=seed_s,
        build_s=build_s,
        index_size=idx.size(),
        queries=args.queries,
        query_total_s=q_total_s,
    )
    if args.archive:
        bench_dir = Path(args.archive_dir) if args.archive_dir else (Path(args.root).resolve() / "benchmarks" / "scale")
        path = archive_report(report, bench_dir)
        root = Path(args.root).resolve()
        try:
            report["archived_to"] = str(path.relative_to(root))
        except ValueError:
            report["archived_to"] = str(path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
