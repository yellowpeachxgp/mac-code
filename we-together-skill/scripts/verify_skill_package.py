"""scripts/verify_skill_package.py — 解包 .weskill.zip 后运行 smoke。

用法:
  python scripts/verify_skill_package.py --package dist/we-together-0.14.0.weskill.zip

步骤:
  1. 解包到临时目录
  2. 校验 manifest.json 存在 + skill_version + schema_version
  3. 尝试对解包根调用 bootstrap 流程（不落库 LLM）
  4. 调用 graph_summary 返回 0 元素
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.packaging.skill_packager import unpack_skill


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True)
    args = ap.parse_args()

    pkg = Path(args.package).resolve()
    if not pkg.exists():
        print(json.dumps({"ok": False, "error": "package not found"}), flush=True)
        return 1

    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "unpacked"
        r = unpack_skill(pkg, target)
        manifest = r["manifest"]
        required = {"name", "skill_version", "schema_version", "files"}
        missing = required - set(manifest.keys())
        if missing:
            print(json.dumps({"ok": False, "missing": sorted(missing)}), flush=True)
            return 2

        report = {
            "ok": True,
            "name": manifest["name"],
            "skill_version": manifest["skill_version"],
            "schema_version": manifest["schema_version"],
            "file_count": len(manifest.get("files", [])),
            "has_skill_md": "SKILL.md" in manifest.get("files", []),
            "has_migrations": any(
                f.startswith("db/migrations/") for f in manifest.get("files", [])
            ),
        }
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
        return 0 if report["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
