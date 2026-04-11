from pathlib import Path
import sys
import argparse
import json


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from we_together.services.snapshot_service import list_snapshots, rollback_to_snapshot


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List or rollback snapshots")
    parser.add_argument("--root", default=str(ROOT), help="Project root")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all snapshots")

    rb = sub.add_parser("rollback", help="Rollback to a snapshot")
    rb.add_argument("--snapshot-id", required=True)

    args = parser.parse_args()
    db_path = Path(args.root) / "db" / "main.sqlite3"

    if args.command == "list":
        snapshots = list_snapshots(db_path)
        print(json.dumps(snapshots, ensure_ascii=False, indent=2))
    elif args.command == "rollback":
        result = rollback_to_snapshot(db_path, args.snapshot_id)
        print(json.dumps(result, ensure_ascii=False))
    else:
        parser.print_help()
