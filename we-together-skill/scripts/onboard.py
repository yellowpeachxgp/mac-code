"""Onboarding CLI：交互式引导新用户完成第一次导入 + 第一次对话。

用法:
  python scripts/onboard.py --root /path/to/project           # 交互
  python scripts/onboard.py --root /path --dry-run            # 只打印将要执行的命令
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.services.onboarding_flow import (
    PROMPTS,
    OnboardingState,
    next_step,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    state = OnboardingState()
    while state.step != "DONE":
        print(f"[{state.step}] {PROMPTS[state.step]}")
        if args.dry_run:
            answer = None
        else:
            try:
                answer = input("> ").strip() or None
            except EOFError:
                answer = None
        state = next_step(state, answer)

    print(f"[DONE] {PROMPTS['DONE']}")
    print()
    print("建议接下来执行的命令：")
    if state.data.get("import_mode") == "narration":
        print(f"  we-together bootstrap --root {args.root}")
        print(f"  we-together ingest narration --root {args.root} --text '...'")
    elif state.data.get("import_mode") != "skip":
        print(f"  we-together bootstrap --root {args.root}")
        print(f"  # 按 {state.data['import_mode']} 格式导入")
    print(f"  we-together create-scene --root {args.root} --type work_discussion --summary '{state.data.get('scene_name')}'")
    print(f"  we-together graph-summary --root {args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
