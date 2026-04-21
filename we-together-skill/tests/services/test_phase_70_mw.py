from __future__ import annotations

import importlib.util
import sqlite3
import sys
import threading
from http.server import HTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _load_bootstrap_script():
    p = REPO_ROOT / "scripts" / "bootstrap.py"
    spec = importlib.util.spec_from_file_location("bootstrap_phase_70", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_seed_demo_script():
    p = REPO_ROOT / "scripts" / "seed_demo.py"
    spec = importlib.util.spec_from_file_location("seed_demo_phase_70", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_fed_server():
    p = REPO_ROOT / "scripts" / "federation_http_server.py"
    spec = importlib.util.spec_from_file_location("fed_phase_70", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_bootstrap_script_supports_tenant_id(tmp_path, monkeypatch):
    mod = _load_bootstrap_script()
    root = tmp_path / "proj"
    monkeypatch.setattr(
        "sys.argv",
        ["bootstrap.py", "--root", str(root), "--tenant-id", "alpha"],
    )
    mod.main()
    assert (root / "tenants" / "alpha" / "db" / "main.sqlite3").exists()


def test_seed_demo_supports_tenant_id(tmp_path, monkeypatch):
    mod = _load_seed_demo_script()
    root = tmp_path / "proj"
    monkeypatch.setattr(
        "sys.argv",
        ["seed_demo.py", "--root", str(root), "--tenant-id", "alpha"],
    )
    mod.main()
    db = root / "tenants" / "alpha" / "db" / "main.sqlite3"
    conn = sqlite3.connect(db)
    person_count = conn.execute("SELECT COUNT(*) FROM persons").fetchone()[0]
    conn.close()
    assert person_count >= 8


def test_federation_server_reads_tenant_db(tmp_path):
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.federation_client import FederationClient
    from we_together.services.tenant_router import resolve_tenant_root

    root = tmp_path / "proj"
    bootstrap_project(root)
    tenant_root = resolve_tenant_root(root, "alpha")
    bootstrap_project(tenant_root)

    default_db = root / "db" / "main.sqlite3"
    tenant_db = tenant_root / "db" / "main.sqlite3"

    conn = sqlite3.connect(default_db)
    conn.execute(
        "INSERT INTO persons(person_id, primary_name, status, confidence, metadata_json, created_at, updated_at) "
        "VALUES('p_default', 'Default User', 'active', 0.9, '{}', datetime('now'), datetime('now'))"
    )
    conn.commit()
    conn.close()

    conn = sqlite3.connect(tenant_db)
    conn.execute(
        "INSERT INTO persons(person_id, primary_name, status, confidence, metadata_json, created_at, updated_at) "
        "VALUES('p_alpha', 'Alpha User', 'active', 0.9, '{}', datetime('now'), datetime('now'))"
    )
    conn.commit()
    conn.close()

    mod = _load_fed_server()
    server = HTTPServer(
        ("127.0.0.1", 0),
        mod.make_handler(tenant_root, allow_writes=False),
    )
    port = server.server_address[1]
    thr = threading.Thread(target=server.serve_forever, daemon=True)
    thr.start()
    try:
        client = FederationClient(f"http://127.0.0.1:{port}")
        persons = client.list_persons()
        names = {p["primary_name"] for p in persons["persons"]}
        assert "Alpha User" in names
        assert "Default User" not in names
    finally:
        server.shutdown()
        server.server_close()


def test_operational_scripts_support_tenant_id(tmp_path):
    import subprocess

    repo_root = REPO_ROOT
    python = str(repo_root / ".venv" / "bin" / "python")
    root = tmp_path / "ops_tenant"

    subprocess.run(
        [
            python,
            str(repo_root / "scripts" / "seed_demo.py"),
            "--root",
            str(root),
            "--tenant-id",
            "alpha",
        ],
        capture_output=True,
        text=True,
        cwd=repo_root,
        check=True,
    )

    for script_args in [
        [
            str(repo_root / "scripts" / "simulate_week.py"),
            "--root",
            str(root),
            "--tenant-id",
            "alpha",
            "--ticks",
            "1",
            "--budget",
            "0",
        ],
        [
            str(repo_root / "scripts" / "simulate_year.py"),
            "--root",
            str(root),
            "--tenant-id",
            "alpha",
            "--days",
            "1",
            "--budget",
            "0",
        ],
        [
            str(repo_root / "scripts" / "dream_cycle.py"),
            "--root",
            str(root),
            "--tenant-id",
            "alpha",
            "--lookback",
            "7",
        ],
        [
            str(repo_root / "scripts" / "fix_graph.py"),
            "--root",
            str(root),
            "--tenant-id",
            "alpha",
            "--policy",
            "report_only",
        ],
    ]:
        proc = subprocess.run(
            [python, *script_args],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        assert proc.returncode == 0, proc.stderr
