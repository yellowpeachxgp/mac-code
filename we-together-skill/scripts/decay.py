import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from we_together.services.state_decay_service import decay_states

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="state confidence 衰减")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--threshold", type=float, default=0.1)
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()

    db_path = Path(args.root) / "db" / "main.sqlite3"
    result = decay_states(db_path, threshold=args.threshold, limit=args.limit)
    print(json.dumps(result, ensure_ascii=False))
