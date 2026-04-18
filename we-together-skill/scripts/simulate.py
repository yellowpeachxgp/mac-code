"""SM-2..5 合一 CLI：predict_conflicts / scene_script / retire_person / era。

调用:
  we-together predict-conflicts --root . --window-days 30
  we-together scene-script --root . --scene-id <id> --turns 6
  we-together retire-person --root . --person-id <id>
  we-together era --root . --days 3
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("predict-conflicts")
    p1.add_argument("--root", default=".")
    p1.add_argument("--window-days", type=int, default=30)

    p2 = sub.add_parser("scene-script")
    p2.add_argument("--root", default=".")
    p2.add_argument("--scene-id", required=True)
    p2.add_argument("--turns", type=int, default=6)

    p3 = sub.add_parser("retire-person")
    p3.add_argument("--root", default=".")
    p3.add_argument("--person-id", required=True)
    p3.add_argument("--reason", default="retired")

    p4 = sub.add_parser("era")
    p4.add_argument("--root", default=".")
    p4.add_argument("--days", type=int, default=3)
    p4.add_argument("--pair-budget-per-day", type=int, default=1)

    args = ap.parse_args()
    db = Path(args.root).resolve() / "db" / "main.sqlite3"

    if args.cmd == "predict-conflicts":
        from we_together.simulation.conflict_predictor import predict_conflicts
        print(json.dumps(predict_conflicts(db, window_days=args.window_days),
                          ensure_ascii=False, indent=2))
    elif args.cmd == "scene-script":
        from we_together.simulation.scene_scripter import write_scene_script
        print(json.dumps(write_scene_script(db, scene_id=args.scene_id,
                                              turns=args.turns),
                          ensure_ascii=False, indent=2))
    elif args.cmd == "retire-person":
        from we_together.services.retire_person_service import retire_person
        print(json.dumps(retire_person(db, args.person_id, reason=args.reason),
                          ensure_ascii=False, indent=2))
    elif args.cmd == "era":
        from we_together.simulation.era_evolution import simulate_era
        print(json.dumps(simulate_era(db, days=args.days,
                                         pair_budget_per_day=args.pair_budget_per_day),
                          ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
