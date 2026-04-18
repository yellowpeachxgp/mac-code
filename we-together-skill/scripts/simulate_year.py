"""scripts/simulate_year.py — 365 tick 加速模拟一年。

用法:
  python scripts/simulate_year.py --root . --days 365 --day-per-tick 1 --budget 50

每 tick 前 advance graph_clock 1 天；结束后 archive tick_run + 跑 integrity_audit。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.services import graph_clock
from we_together.services.time_simulator import simulate, TickBudget
from we_together.services.tick_sanity import evaluate
from we_together.services.integrity_audit import full_audit


def run_year(db: Path, *, days: int, budget: int,
              do_self_activation: bool = False) -> dict:
    results: list[dict] = []
    b = TickBudget(llm_calls=budget)
    # 每 day 推进一次 clock，跑一次 tick
    for day in range(days):
        try:
            graph_clock.advance(db, days=1)
        except Exception:
            pass
        r = simulate(db, ticks=1, budget=b,
                     do_self_activation=do_self_activation)
        results.append({
            "day": day,
            "history": r["history"],
            "budget_remaining": r["llm_calls_remaining"],
        })
    sanity = evaluate(db, ticks=days)
    integrity = full_audit(db)
    return {
        "days": days, "budget_input": budget,
        "budget_remaining": b.llm_calls,
        "results_sample": results[:3] + ([results[-1]] if results else []),
        "total_snapshots": sum(len(r["history"]) for r in results),
        "sanity": sanity,
        "integrity": {
            "total_issues": integrity["total_issues"],
            "healthy": integrity["healthy"],
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--budget", type=int, default=50,
                    help="LLM calls across entire year")
    ap.add_argument("--self-activation", action="store_true")
    args = ap.parse_args()

    db = Path(args.root).resolve() / "db" / "main.sqlite3"
    if not db.exists():
        print(json.dumps({"error": "db not found"}))
        return 1

    report = run_year(db, days=args.days, budget=args.budget,
                      do_self_activation=args.self_activation)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
