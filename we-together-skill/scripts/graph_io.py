"""Graph canonical I/O CLI：export / import 子命令。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.services.graph_serializer import (
    dump_graph_to_file,
    load_graph_from_file,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("export")
    p1.add_argument("--root", default=".")
    p1.add_argument("--out", required=True)

    p2 = sub.add_parser("import")
    p2.add_argument("--input", required=True)
    p2.add_argument("--target", required=True)

    args = ap.parse_args()
    if args.cmd == "export":
        db = Path(args.root).resolve() / "db" / "main.sqlite3"
        r = dump_graph_to_file(db, Path(args.out).resolve())
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        r = load_graph_from_file(Path(args.input).resolve(),
                                  Path(args.target).resolve())
        print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
