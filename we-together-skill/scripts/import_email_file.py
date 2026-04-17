import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from we_together.services.email_ingestion_service import ingest_email_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import an .eml file into the SQLite graph")
    parser.add_argument("--root", default=str(ROOT), help="Project root containing db/main.sqlite3")
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    db_path = Path(args.root) / "db" / "main.sqlite3"
    result = ingest_email_file(db_path=db_path, email_path=Path(args.file))
    print(json.dumps(result, ensure_ascii=False))
