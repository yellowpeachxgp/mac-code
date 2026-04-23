import json
import sys
import zipfile
from importlib import util
from pathlib import Path

from we_together.packaging.skill_packager import pack_skill


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_verify_skill_package():
    script_path = REPO_ROOT / "scripts" / "verify_skill_package.py"
    module_name = "verify_skill_package_test_module"
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = util.spec_from_file_location(module_name, script_path)
    module = util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_verify_skill_package_rejects_manifest_only_fake_package(
    tmp_path, monkeypatch, capsys
):
    verify_skill_package = _load_verify_skill_package()
    pkg = tmp_path / "fake.weskill.zip"
    with zipfile.ZipFile(pkg, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "manifest.json",
            json.dumps(
                {
                    "name": "fake",
                    "skill_version": "0.0.0",
                    "schema_version": "0000",
                    "files": [],
                }
            ),
        )

    monkeypatch.setattr(
        sys,
        "argv",
        ["verify_skill_package.py", "--package", str(pkg)],
    )

    assert verify_skill_package.main() != 0
    report = json.loads(capsys.readouterr().out)
    assert report["ok"] is False


def test_verify_skill_package_accepts_real_packed_repo_package(
    tmp_path, monkeypatch, capsys
):
    verify_skill_package = _load_verify_skill_package()
    pkg = tmp_path / "we-together.weskill.zip"
    pack_skill(REPO_ROOT, pkg)

    monkeypatch.setattr(
        sys,
        "argv",
        ["verify_skill_package.py", "--package", str(pkg)],
    )

    assert verify_skill_package.main() == 0
    report = json.loads(capsys.readouterr().out)
    assert report["ok"] is True
    assert report["has_skill_md"] is True
    assert report["has_migrations"] is True
    assert report["file_count"] > 0
