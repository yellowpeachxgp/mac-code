import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from we_together.llm import get_llm_client
from we_together.services.self_activation_service import self_activate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自激活：生成内心独白事件")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--daily-budget", type=int, default=3)
    parser.add_argument("--per-run", type=int, default=2)
    parser.add_argument("--provider", default=None)
    args = parser.parse_args()

    db_path = Path(args.root) / "db" / "main.sqlite3"
    client = get_llm_client(args.provider)
    result = self_activate(
        db_path=db_path, scene_id=args.scene_id,
        llm_client=client, daily_budget=args.daily_budget,
        per_run_limit=args.per_run,
    )
    print(json.dumps(result, ensure_ascii=False))
