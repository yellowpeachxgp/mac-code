"""scripts/simulate_week.py — 跑 7 天 tick 并输出报告。

用法:
  python scripts/simulate_week.py --root . --ticks 7 --budget 30

输出: JSON 报告含每 tick 的 decay/drift/proactive 统计 + 合理性评估
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.llm import get_llm_client
from we_together.services.time_simulator import simulate, TickBudget
from we_together.services.tick_sanity import evaluate


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--ticks", type=int, default=7)
    ap.add_argument("--budget", type=int, default=30,
                    help="total LLM calls across all ticks")
    ap.add_argument("--self-activation", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    db = root / "db" / "main.sqlite3"
    if not db.exists():
        print(json.dumps({"error": "db not found", "path": str(db)}))
        return 1

    budget = TickBudget(llm_calls=args.budget)
    report = simulate(
        db, ticks=args.ticks, budget=budget,
        llm_client=get_llm_client(),
        do_self_activation=args.self_activation,
    )
    sanity = evaluate(db, ticks=args.ticks)
    report["sanity"] = sanity

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
