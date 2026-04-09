from pathlib import Path
import sys
import argparse
import json


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from we_together.services.file_ingestion_service import ingest_file_auto


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatically detect and import a file into the SQLite graph")
    parser.add_argument("--root", default=str(ROOT), help="Project root containing db/main.sqlite3")
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    db_path = Path(args.root) / "db" / "main.sqlite3"
    file_path = Path(args.file)
    if not file_path.exists() or not file_path.is_file():
        print(f"File not found: {file_path}", file=sys.stderr)
        raise SystemExit(1)

    result = ingest_file_auto(db_path=db_path, file_path=file_path)
    print(json.dumps(result, ensure_ascii=False))
