"""scripts/release_prep.py — 发布前本地自检。

检查：
- tag 存在
- pyproject/cli VERSION 一致
- wheel 能 build
- 关键 ADR/CHANGELOG/release_notes 存在
- 全量 pytest 可一键重跑（不真跑，只打印命令）

用法:
  python scripts/release_prep.py --version 0.17.0
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def _check(name: str, ok: bool, detail: str = "") -> dict:
    return {"check": name, "ok": ok, "detail": detail}


def run_checks(version: str, repo_root: Path) -> dict:
    checks: list[dict] = []

    # pyproject version
    pyproject = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'version\s*=\s*"([^"]+)"', pyproject)
    checks.append(_check(
        "pyproject.toml version", m is not None and m.group(1) == version,
        f"found {m.group(1) if m else 'none'}, expected {version}",
    ))

    # cli VERSION
    cli = (repo_root / "src" / "we_together" / "cli.py").read_text(encoding="utf-8")
    m2 = re.search(r'VERSION\s*=\s*"([^"]+)"', cli)
    checks.append(_check(
        "cli.py VERSION", m2 is not None and m2.group(1) == version,
        f"found {m2.group(1) if m2 else 'none'}, expected {version}",
    ))

    # CHANGELOG has entry
    chlog = (repo_root / "docs" / "CHANGELOG.md").read_text(encoding="utf-8")
    has_entry = f"v{version}" in chlog
    checks.append(_check(
        "CHANGELOG entry", has_entry,
        f"'v{version}' in docs/CHANGELOG.md",
    ))

    # release_notes exists
    rn = repo_root / "docs" / f"release_notes_v{version}.md"
    checks.append(_check(
        "release_notes file", rn.exists(),
        str(rn.relative_to(repo_root)),
    ))

    # git tag
    try:
        out = subprocess.check_output(
            ["git", "tag", "-l", f"v{version}"], cwd=repo_root,
        ).decode("utf-8").strip()
        checks.append(_check(
            "git tag exists", out == f"v{version}", f"git tag v{version}",
        ))
    except Exception as exc:
        checks.append(_check("git tag exists", False, str(exc)))

    # wheel built
    wheel_path = repo_root / "dist" / f"we_together-{version}-py3-none-any.whl"
    checks.append(_check(
        "wheel artifact", wheel_path.exists(),
        str(wheel_path.relative_to(repo_root)),
    ))

    all_ok = all(c["ok"] for c in checks)
    return {
        "version": version,
        "ok": all_ok,
        "checks": checks,
        "next": [
            "python -m pytest -q",
            "python -m twine check dist/*",
            "# 本地 TestPyPI 测试：见 docs/release/pypi_checklist.md",
        ] if all_ok else [
            "修复上面 ok=False 的检查后重跑",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    args = ap.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    report = run_checks(args.version, repo_root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
