"""scripts/what_if.py：社会模拟 teaser CLI。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.simulation.what_if_service import simulate_what_if


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--scene-id", required=True)
    ap.add_argument("--hypothesis", required=True)
    args = ap.parse_args()

    db = Path(args.root).resolve() / "db" / "main.sqlite3"
    result = simulate_what_if(db_path=db, scene_id=args.scene_id,
                               hypothesis=args.hypothesis)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
