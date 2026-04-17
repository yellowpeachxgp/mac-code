import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from we_together.runtime.sqlite_retrieval import build_runtime_retrieval_package_from_db

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a runtime retrieval package from SQLite")
    parser.add_argument("--root", default=str(ROOT), help="Project root containing db/main.sqlite3")
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--input-hash", default=None)
    parser.add_argument("--cache-ttl", type=int, default=None, help="Cache TTL in seconds (default: use built-in default)")
    parser.add_argument("--max-memories", type=int, default=20, help="最大 memory 条数")
    parser.add_argument("--max-relations", type=int, default=10, help="最大 relation 条数")
    parser.add_argument("--max-states", type=int, default=30, help="最大 state 条数")
    args = parser.parse_args()

    db_path = Path(args.root) / "db" / "main.sqlite3"
    try:
        package = build_runtime_retrieval_package_from_db(
            db_path=db_path,
            scene_id=args.scene_id,
            input_hash=args.input_hash,
            cache_ttl_seconds=args.cache_ttl,
            max_memories=args.max_memories,
            max_relations=args.max_relations,
            max_states=args.max_states,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

    print(json.dumps(package, ensure_ascii=False))
