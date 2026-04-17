"""记忆凝练 CLI：把同主题多条 memory 压成 1 条 condensed_memory。

用法:
  .venv/bin/python scripts/condense_memories.py --root . [--max-clusters 20]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.services.memory_condenser_service import condense_memory_clusters


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="项目根目录")
    ap.add_argument("--max-clusters", type=int, default=20)
    ap.add_argument("--min-cluster-size", type=int, default=2)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    db_path = root / "db" / "main.sqlite3"
    if not db_path.exists():
        print(f"db not found: {db_path}", file=sys.stderr)
        sys.exit(2)

    result = condense_memory_clusters(
        db_path=db_path,
        max_clusters=args.max_clusters,
        min_cluster_size=args.min_cluster_size,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
