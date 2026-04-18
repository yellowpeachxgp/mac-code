"""scripts/simulate_year.py — 365 tick 加速模拟一年。

用法:
  python scripts/simulate_year.py --root . --days 365 --budget 50 --archive-monthly

每 tick 前 advance graph_clock 1 天；结束后跑 integrity_audit + sanity 评估。
--archive-monthly：按 30 天切片聚合月度，整份报告归档到 benchmarks/year_runs/
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.services import graph_clock
from we_together.services.time_simulator import simulate, TickBudget
from we_together.services.tick_sanity import evaluate
from we_together.services.integrity_audit import full_audit


def _month_index(day: int) -> int:
    return day // 30


def run_year(
    db: Path, *,
    days: int, budget: int,
    do_self_activation: bool = False,
    archive_dir: Path | None = None,
) -> dict:
    b = TickBudget(llm_calls=budget)
    monthly: dict[int, dict] = {}

    for day in range(days):
        try:
            graph_clock.advance(db, days=1)
        except Exception:
            pass
        r = simulate(db, ticks=1, budget=b,
                     do_self_activation=do_self_activation)
        month = _month_index(day)
        mon = monthly.setdefault(
            month,
            {"month": month, "days": 0, "snapshots_added": 0},
        )
        mon["days"] += 1
        mon["snapshots_added"] += len([s for s in r["snapshot_ids"] if s])

    sanity = evaluate(db, ticks=days)
    integrity = full_audit(db)

    final_report = {
        "days": days, "budget_input": budget,
        "budget_remaining": b.llm_calls,
        "total_snapshots_added": sum(m["snapshots_added"] for m in monthly.values()),
        "total_months": len(monthly),
        "monthly": sorted(monthly.values(), key=lambda x: x["month"]),
        "sanity": sanity,
        "integrity": {
            "total_issues": integrity["total_issues"],
            "healthy": integrity["healthy"],
        },
        "generated_at": datetime.now(UTC).isoformat(),
    }

    if archive_dir is not None:
        archive_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
        path = archive_dir / f"year_run_{ts}.json"
        path.write_text(
            json.dumps(final_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        final_report["archived_to"] = str(path)

    return final_report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--budget", type=int, default=50)
    ap.add_argument("--self-activation", action="store_true")
    ap.add_argument("--archive-monthly", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    db = root / "db" / "main.sqlite3"
    if not db.exists():
        print(json.dumps({"error": "db not found"}))
        return 1

    archive_dir = None
    if args.archive_monthly:
        archive_dir = root / "benchmarks" / "year_runs"

    report = run_year(
        db, days=args.days, budget=args.budget,
        do_self_activation=args.self_activation,
        archive_dir=archive_dir,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
