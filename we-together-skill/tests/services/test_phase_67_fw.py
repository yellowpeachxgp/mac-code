from __future__ import annotations

import importlib.util
import sqlite3
import sys
import threading
from http.server import HTTPServer
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))


def _load_server():
    p = REPO_ROOT / "scripts" / "federation_http_server.py"
    spec = importlib.util.spec_from_file_location("fed_67", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _seed_person(db: Path, person_id: str, primary_name: str) -> None:
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO persons(person_id, primary_name, status, confidence, metadata_json, created_at, updated_at) "
        "VALUES(?, ?, 'active', 0.9, '{}', datetime('now'), datetime('now'))",
        (person_id, primary_name),
    )
    conn.commit()
    conn.close()


def test_create_shared_memory_from_federation_service(temp_project_with_migrations):
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.federation_write_service import create_shared_memory_from_federation

    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    _seed_person(db, "p_fw_1", "Alice")
    _seed_person(db, "p_fw_2", "Bob")

    result = create_shared_memory_from_federation(
        db,
        summary="federation shared memory",
        owner_person_ids=["p_fw_1", "p_fw_2"],
        source_skill_name="peer-alpha",
        source_locator="curl-test",
        metadata={"kind": "federation-post"},
    )

    conn = sqlite3.connect(db)
    memory_row = conn.execute(
        "SELECT summary, memory_type, is_shared FROM memories WHERE memory_id = ?",
        (result["memory_id"],),
    ).fetchone()
    event_row = conn.execute(
        "SELECT event_type, source_type FROM events WHERE event_id = ?",
        (result["event_id"],),
    ).fetchone()
    owners = conn.execute(
        "SELECT COUNT(*) FROM memory_owners WHERE memory_id = ?",
        (result["memory_id"],),
    ).fetchone()[0]
    snapshot_row = conn.execute(
        "SELECT trigger_event_id FROM snapshots WHERE snapshot_id = ?",
        (result["snapshot_id"],),
    ).fetchone()
    conn.close()

    assert memory_row == ("federation shared memory", "shared_memory", 1)
    assert event_row == ("federation_memory_ingested", "federation")
    assert owners == 2
    assert snapshot_row[0] == result["event_id"]


def test_federation_post_memory_disabled_by_default(temp_project_with_migrations):
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.federation_client import FederationClient

    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    _seed_person(db, "p_fw_3", "Carol")

    m = _load_server()
    server = HTTPServer(("127.0.0.1", 0), m.make_handler(temp_project_with_migrations))
    port = server.server_address[1]
    thr = threading.Thread(target=server.serve_forever, daemon=True)
    thr.start()

    try:
        client = FederationClient(f"http://127.0.0.1:{port}")
        with pytest.raises(RuntimeError, match="403"):
            client.create_memory(summary="x", owner_person_ids=["p_fw_3"])
    finally:
        server.shutdown()
        server.server_close()


def test_federation_post_memory_requires_token_when_configured(temp_project_with_migrations):
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.federation_client import FederationClient
    from we_together.services.federation_security import hash_token

    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    _seed_person(db, "p_fw_4", "Dan")

    m = _load_server()
    handler = m.make_handler(
        temp_project_with_migrations,
        allowed_token_hashes=[hash_token("phase67-token")],
        rate_limiter=None,
        mask_pii_on_export=False,
        allow_writes=True,
    )
    server = HTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thr = threading.Thread(target=server.serve_forever, daemon=True)
    thr.start()

    try:
        client = FederationClient(f"http://127.0.0.1:{port}")
        with pytest.raises(RuntimeError, match="401"):
            client.create_memory(summary="x", owner_person_ids=["p_fw_4"])

        authed = FederationClient(
            f"http://127.0.0.1:{port}",
            bearer_token="phase67-token",
        )
        result = authed.create_memory(
            summary="authorized federation write",
            owner_person_ids=["p_fw_4"],
            source_skill_name="peer-beta",
        )
        assert result["owner_count"] == 1
        assert result["memory_id"].startswith("memory_")
    finally:
        server.shutdown()
        server.server_close()


def test_capabilities_reflect_write_mode():
    m = _load_server()
    ro = m._capabilities()
    rw = m._capabilities(allow_writes=True)
    assert ro["read_only"] is True
    assert ro["write_enabled"] is False
    assert rw["read_only"] is False
    assert rw["write_enabled"] is True
