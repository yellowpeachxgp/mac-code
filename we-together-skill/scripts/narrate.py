"""scripts/narrate.py + scripts/analyze.py 的合并入口（用于 CLI 子命令）。

实际接入 cli.py SCRIPT_MAP 时分别映射。
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

    p1 = sub.add_parser("aggregate", help="LLM 聚合 narrative arcs")
    p1.add_argument("--root", default=".")
    p1.add_argument("--scene-id", default=None)
    p1.add_argument("--limit", type=int, default=20)

    p2 = sub.add_parser("list", help="列出已有 arcs")
    p2.add_argument("--root", default=".")
    p2.add_argument("--scene-id", default=None)

    p3 = sub.add_parser("playback", help="把 arcs 串成故事文本")
    p3.add_argument("--root", default=".")
    p3.add_argument("--scene-id", default=None)

    args = ap.parse_args()
    db = Path(args.root).resolve() / "db" / "main.sqlite3"
    if args.cmd == "aggregate":
        from we_together.services.narrative_service import aggregate_narrative_arcs
        r = aggregate_narrative_arcs(db, scene_id=args.scene_id, limit=args.limit)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    elif args.cmd == "list":
        from we_together.services.narrative_service import list_arcs
        arcs = list_arcs(db, scene_id=args.scene_id)
        print(json.dumps(arcs, ensure_ascii=False, indent=2))
    elif args.cmd == "playback":
        from we_together.services.narrative_service import list_arcs
        arcs = list_arcs(db, scene_id=args.scene_id)
        for arc in arcs:
            print(f"\n# {arc['title'] or '(无标题)'} [{arc['theme']}]\n")
            print(arc['summary'] or "(无摘要)")
            print(f"\n（事件 {len(arc['event_ids'])} 个）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
