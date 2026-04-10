from pathlib import Path
import sys
import argparse
import json


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
    args = parser.parse_args()

    db_path = Path(args.root) / "db" / "main.sqlite3"
    try:
        package = build_runtime_retrieval_package_from_db(
            db_path=db_path,
            scene_id=args.scene_id,
            input_hash=args.input_hash,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

    print(json.dumps(package, ensure_ascii=False))
