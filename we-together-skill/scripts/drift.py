from pathlib import Path
import sys
import argparse
import json


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from we_together.services.relation_drift_service import drift_relations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="关系漂移：按 event 窗口重算 strength")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--window-days", type=int, default=30)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    db_path = Path(args.root) / "db" / "main.sqlite3"
    result = drift_relations(db_path, window_days=args.window_days, limit=args.limit)
    print(json.dumps(result, ensure_ascii=False))
