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
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.packaging.skill_packager import unpack_skill


REQUIRED_PACKAGE_FILES = [
    "SKILL.md",
    "scripts/bootstrap.py",
    "scripts/graph_summary.py",
]


def _validate_unpacked_package(target: Path, manifest: dict) -> dict:
    files = manifest.get("files", [])
    missing_from_manifest = [
        rel for rel in REQUIRED_PACKAGE_FILES if rel not in files
    ]
    missing_on_disk = [
        rel for rel in files if not (target / rel).exists()
    ]
    missing_required_on_disk = [
        rel for rel in REQUIRED_PACKAGE_FILES if not (target / rel).exists()
    ]
    has_migrations = any(
        f.startswith("db/migrations/") for f in files
    ) and any((target / "db" / "migrations").glob("*.sql"))

    return {
        "has_skill_md": "SKILL.md" in files and (target / "SKILL.md").exists(),
        "has_migrations": has_migrations,
        "missing_from_manifest": sorted(missing_from_manifest),
        "missing_on_disk": sorted(missing_on_disk),
        "missing_required_on_disk": sorted(missing_required_on_disk),
    }


def _run_runtime_checks(target: Path) -> dict:
    bootstrap = target / "scripts" / "bootstrap.py"
    graph_summary = target / "scripts" / "graph_summary.py"
    root = target

    bootstrap_proc = subprocess.run(
        [sys.executable, str(bootstrap), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if bootstrap_proc.returncode != 0:
        return {
            "ok": False,
            "step": "bootstrap",
            "stdout": bootstrap_proc.stdout,
            "stderr": bootstrap_proc.stderr,
        }

    db_path = root / "db" / "main.sqlite3"
    if not db_path.exists():
        return {"ok": False, "step": "bootstrap", "error": "db not created"}

    summary_proc = subprocess.run(
        [sys.executable, str(graph_summary), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if summary_proc.returncode != 0:
        return {
            "ok": False,
            "step": "graph_summary",
            "stdout": summary_proc.stdout,
            "stderr": summary_proc.stderr,
        }

    summary = json.loads(summary_proc.stdout)
    sqlite3.connect(db_path).close()
    return {
        "ok": True,
        "step": "graph_summary",
        "summary": summary,
    }


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

        unpacked = _validate_unpacked_package(target, manifest)
        runtime = _run_runtime_checks(target) if not unpacked["missing_required_on_disk"] else {
            "ok": False,
            "step": "precheck",
            "error": "required package files missing on disk",
        }

        report = {
            "ok": (
                unpacked["has_skill_md"]
                and unpacked["has_migrations"]
                and not unpacked["missing_from_manifest"]
                and not unpacked["missing_on_disk"]
                and not unpacked["missing_required_on_disk"]
                and runtime["ok"]
            ),
            "name": manifest["name"],
            "skill_version": manifest["skill_version"],
            "schema_version": manifest["schema_version"],
            "file_count": len(manifest.get("files", [])),
            **unpacked,
            "runtime_check": runtime,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
        return 0 if report["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
