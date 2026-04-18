"""Skill 可分发包：把 SKILL.md + migrations/seeds + 选定脚本打包为 .weskill.zip。

最小 manifest 约定:
  {
    "format_version": 1,
    "name": "we-together",
    "skill_version": "0.8.0",
    "schema_version": "0007",
    "created_at": "...",
    "files": ["SKILL.md", "db/migrations/*", ...]
  }

使用 Python 内置 zipfile 实现，无外部依赖。
"""
from __future__ import annotations

import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_INCLUDE_GLOBS = [
    "SKILL.md",
    "db/migrations/*.sql",
    "db/seeds/*.yaml",
    "db/seeds/*.yml",
    "db/seeds/*.json",
    "scripts/*.py",
    "src/we_together/**/*.py",
]


def _collect_files(root: Path, globs: list[str]) -> list[Path]:
    files: list[Path] = []
    for g in globs:
        files.extend(sorted(root.glob(g)))
    # dedupe 保持相对顺序
    seen: set[Path] = set()
    out: list[Path] = []
    for f in files:
        if f.is_file() and f not in seen:
            seen.add(f)
            out.append(f)
    return out


def pack_skill(
    root: Path,
    output_path: Path,
    *,
    skill_version: str = "0.8.0",
    schema_version: str = "0007",
    include_globs: list[str] | None = None,
) -> dict:
    include_globs = include_globs or DEFAULT_INCLUDE_GLOBS
    files = _collect_files(root, include_globs)
    manifest = {
        "format_version": 1,
        "name": "we-together",
        "skill_version": skill_version,
        "schema_version": schema_version,
        "created_at": datetime.now(UTC).isoformat(),
        "files": [str(f.relative_to(root)) for f in files],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        for f in files:
            zf.write(f, arcname=str(f.relative_to(root)))
    return {"output": str(output_path), "file_count": len(files), "manifest": manifest}


def unpack_skill(package_path: Path, target_root: Path) -> dict:
    target_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package_path, "r") as zf:
        manifest_raw = zf.read("manifest.json").decode("utf-8")
        manifest = json.loads(manifest_raw)
        zf.extractall(target_root)
    return {"target": str(target_root), "manifest": manifest}
