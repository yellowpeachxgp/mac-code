"""日常维护编排：一次跑完图谱自演化与清理。

步骤:
  1. relation drift
  2. state decay
  3. branch auto resolve
  4. merge_duplicates (identity 合并)
  5. graph_summary 打印
"""
import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from we_together.services.branch_resolver_service import auto_resolve_branches
from we_together.services.identity_fusion_service import find_and_merge_duplicates
from we_together.services.relation_drift_service import drift_relations
from we_together.services.state_decay_service import decay_states


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="每日维护编排")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--drift-window-days", type=int, default=30)
    parser.add_argument("--decay-threshold", type=float, default=0.1)
    parser.add_argument("--branch-threshold", type=float, default=0.8)
    parser.add_argument("--branch-margin", type=float, default=0.2)
    parser.add_argument("--merge-threshold", type=float, default=0.7)
    args = parser.parse_args()

    db_path = Path(args.root) / "db" / "main.sqlite3"
    report = {
        "drift": drift_relations(db_path, window_days=args.drift_window_days),
        "decay": decay_states(db_path, threshold=args.decay_threshold),
        "auto_resolve": auto_resolve_branches(
            db_path, threshold=args.branch_threshold, margin=args.branch_margin,
        ),
        "merge_duplicates": find_and_merge_duplicates(db_path, threshold=args.merge_threshold),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
