import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from we_together.services.branch_resolver_service import auto_resolve_branches


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自动解决显著占优的 local branch")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--threshold", type=float, default=0.8)
    parser.add_argument("--margin", type=float, default=0.2)
    args = parser.parse_args()

    db_path = Path(args.root) / "db" / "main.sqlite3"
    result = auto_resolve_branches(db_path, threshold=args.threshold, margin=args.margin)
    print(json.dumps(result, ensure_ascii=False))
