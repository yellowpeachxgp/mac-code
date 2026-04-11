from pathlib import Path
import sys
import argparse
import json


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from we_together.services.identity_fusion_service import find_and_merge_duplicates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自动发现并合并重复人物")
    parser.add_argument("--root", default=str(ROOT), help="Project root")
    parser.add_argument("--threshold", type=float, default=0.7, help="合并阈值 (default: 0.7)")
    args = parser.parse_args()

    db_path = Path(args.root) / "db" / "main.sqlite3"
    result = find_and_merge_duplicates(db_path, threshold=args.threshold)
    print(json.dumps(result, ensure_ascii=False))
