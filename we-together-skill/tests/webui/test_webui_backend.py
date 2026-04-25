from __future__ import annotations

import http.client
import json
import sqlite3
import threading
from pathlib import Path

import pytest

from we_together.db.bootstrap import bootstrap_project
from we_together.llm.providers.mock import MockLLMClient
from we_together.services.patch_applier import apply_patch_record
from we_together.services.patch_service import build_patch
from we_together.services.world_service import (
    link_event_to_place,
    register_object,
    register_place,
    register_project,
)


def _seed_webui_graph(root: Path) -> dict:
    bootstrap_project(root)
    db_path = root / "db" / "main.sqlite3"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO persons(
                person_id, primary_name, status, summary, persona_summary,
                confidence, metadata_json, created_at, updated_at
            ) VALUES('person_web_1', 'Alice', 'active', 'operator',
                     'calm builder', 0.9, '{}', datetime('now'), datetime('now'))
            """
        )
        conn.execute(
            """
            INSERT INTO persons(
                person_id, primary_name, status, summary, persona_summary,
                confidence, metadata_json, created_at, updated_at
            ) VALUES('person_web_2', 'Bob', 'active', 'reviewer',
                     'careful reviewer', 0.8, '{}', datetime('now'), datetime('now'))
            """
        )
        conn.execute(
            """
            INSERT INTO groups(
                group_id, group_type, name, summary, status, confidence,
                metadata_json, created_at, updated_at
            ) VALUES('group_web_1', 'team', 'Core', 'core group',
                     'active', 0.8, '{}', datetime('now'), datetime('now'))
            """
        )
        conn.execute(
            """
            INSERT INTO group_members(
                group_id, person_id, role_label, joined_at, status, metadata_json
            ) VALUES('group_web_1', 'person_web_1', 'owner', datetime('now'),
                     'active', '{}')
            """
        )
        conn.execute(
            """
            INSERT INTO relations(
                relation_id, core_type, custom_label, summary, directionality,
                strength, stability, visibility, status, confidence,
                metadata_json, created_at, updated_at
            ) VALUES('relation_web_1', 'work', 'alice_bob', 'works together',
                     'bidirectional', 0.7, 0.6, 'known', 'active', 0.8, '{}',
                     datetime('now'), datetime('now'))
            """
        )
        conn.execute(
            """
            INSERT INTO scenes(
                scene_id, scene_type, group_id, scene_summary,
                location_scope, channel_scope, visibility_scope,
                activation_barrier, environment_json, status, created_at, updated_at
            ) VALUES('scene_web_1', 'work_discussion', 'group_web_1',
                     'weekly sync', 'remote', 'group_channel', 'group_visible',
                     'low', '{}', 'active', datetime('now'), datetime('now'))
            """
        )
        for person_id, speaking in [("person_web_1", 1), ("person_web_2", 0)]:
            conn.execute(
                """
                INSERT INTO scene_participants(
                    scene_id, person_id, activation_score, activation_state,
                    is_speaking, reason_json, created_at, updated_at
                ) VALUES('scene_web_1', ?, 0.9, 'explicit', ?, '{}',
                         datetime('now'), datetime('now'))
                """,
                (person_id, speaking),
            )
        conn.execute(
            """
            INSERT INTO events(
                event_id, event_type, source_type, scene_id, timestamp, summary,
                visibility_level, confidence, is_structured,
                raw_evidence_refs_json, metadata_json, created_at
            ) VALUES('event_web_1', 'narration_seed', 'test', 'scene_web_1',
                     datetime('now'), 'seed event', 'visible', 0.9, 1, '[]',
                     '{}', datetime('now'))
            """
        )
        for person_id in ("person_web_1", "person_web_2"):
            conn.execute(
                "INSERT INTO event_participants(event_id, person_id, participant_role) VALUES('event_web_1', ?, 'mentioned')",
                (person_id,),
            )
        conn.execute(
            "INSERT INTO event_targets(event_id, target_type, target_id, impact_hint) VALUES('event_web_1', 'relation', 'relation_web_1', 'seed')"
        )
        conn.execute(
            """
            INSERT INTO local_branches(
                branch_id, scope_type, scope_id, status, reason,
                created_from_event_id, created_at
            ) VALUES('branch_web_1', 'person', 'person_web_1', 'open',
                     'review needed', 'event_web_1', datetime('now'))
            """
        )
        conn.execute(
            """
            INSERT INTO branch_candidates(
                candidate_id, branch_id, label, payload_json, confidence,
                status, created_at
            ) VALUES('candidate_web_1', 'branch_web_1', 'Keep current',
                     '{"effect_patches":[]}', 0.8, 'open', datetime('now'))
            """
        )
        conn.commit()
    finally:
        conn.close()

    memory_patch = build_patch(
        source_event_id="event_web_1",
        target_type="memory",
        target_id="memory_web_1",
        operation="create_memory",
        payload={
            "memory_id": "memory_web_1",
            "memory_type": "shared_memory",
            "summary": "Alice and Bob shipped a milestone",
            "relevance_score": 0.9,
            "confidence": 0.8,
            "is_shared": 1,
            "status": "active",
            "metadata_json": {"source": "webui_test"},
        },
        confidence=0.8,
        reason="seed memory",
    )
    apply_patch_record(db_path=db_path, patch=memory_patch)

    conn = sqlite3.connect(db_path)
    try:
        for person_id in ("person_web_1", "person_web_2"):
            conn.execute(
                "INSERT INTO memory_owners(memory_id, owner_type, owner_id, role_label) VALUES('memory_web_1', 'person', ?, NULL)",
                (person_id,),
            )
        conn.commit()
    finally:
        conn.close()

    place = register_place(db_path, name="Web Room", scope="virtual")
    link_event_to_place(db_path, "event_web_1", place["place_id"])
    world_object = register_object(
        db_path,
        kind="tool",
        name="Shared Notebook",
        owner_type="person",
        owner_id="person_web_1",
    )
    world_project = register_project(
        db_path,
        name="WebUI Phase",
        goal="ship host local workbench",
        participants=["person_web_1", "person_web_2"],
    )
    return {
        "root": root,
        "db_path": db_path,
        "object_id": world_object["object_id"],
        "project_id": world_project["project_id"],
    }


def _start_server(root: Path, *, token: str = "dev-token", static_dir: Path | None = None):
    from we_together.webui.server import WebUIConfig, create_server

    config = WebUIConfig(
        root=root,
        tenant_id="default",
        host="127.0.0.1",
        port=0,
        token=token,
        static_dir=static_dir,
        llm_client=MockLLMClient(default_content="你好，我收到了。"),
    )
    server = create_server(config)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _request(
    server,
    method: str,
    path: str,
    *,
    token: str | None = "dev-token",
    body: dict | None = None,
) -> tuple[int, str, dict | list | None]:
    host, port = server.server_address
    conn = http.client.HTTPConnection(host, port, timeout=5)
    headers: dict[str, str] = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    raw_body = None
    if body is not None:
        raw_body = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    conn.request(method, path, body=raw_body, headers=headers)
    resp = conn.getresponse()
    text = resp.read().decode("utf-8")
    conn.close()
    parsed = None
    if resp.getheader("Content-Type", "").startswith("application/json"):
        parsed = json.loads(text)
    return resp.status, text, parsed


def test_webui_auth_requires_token_for_api(temp_project_with_migrations):
    _seed_webui_graph(temp_project_with_migrations)
    server = _start_server(temp_project_with_migrations)
    try:
        status, _, payload = _request(server, "GET", "/api/bootstrap", token=None)
        assert status == 401
        assert payload["ok"] is False
        assert payload["error"]["code"] == "unauthorized"

        status, _, payload = _request(server, "GET", "/api/bootstrap", token="wrong")
        assert status == 401
        assert payload["ok"] is False

        status, _, payload = _request(server, "GET", "/api/bootstrap")
        assert status == 200
        assert payload["ok"] is True
        assert payload["data"]["tenant_id"] == "default"
    finally:
        server.shutdown()
        server.server_close()


def test_webui_rejects_lan_without_token(temp_project_dir):
    from we_together.webui.server import WebUIConfig, validate_startup_security

    with pytest.raises(ValueError, match="token"):
        validate_startup_security(
            WebUIConfig(root=temp_project_dir, host="0.0.0.0", port=7788, token=None)
        )

    validate_startup_security(
        WebUIConfig(root=temp_project_dir, host="127.0.0.1", port=7788, token=None)
    )


def test_webui_health_and_bootstrap(temp_project_with_migrations):
    _seed_webui_graph(temp_project_with_migrations)
    server = _start_server(temp_project_with_migrations)
    try:
        status, _, health = _request(server, "GET", "/healthz", token=None)
        assert status == 200
        assert health["ok"] is True
        assert health["data"]["tenant_id"] == "default"
        assert health["data"]["auth_mode"] == "bearer"

        status, _, bootstrap = _request(server, "GET", "/api/bootstrap")
        assert status == 200
        assert bootstrap["data"]["capabilities"]["graph"] is True
        assert bootstrap["data"]["feature_flags"]["patch_first_editor"] is True
    finally:
        server.shutdown()
        server.server_close()


def test_webui_read_apis_cover_graph_world_review(temp_project_with_migrations):
    _seed_webui_graph(temp_project_with_migrations)
    server = _start_server(temp_project_with_migrations)
    try:
        status, _, summary = _request(server, "GET", "/api/summary")
        assert status == 200
        assert summary["data"]["person_count"] == 2
        assert summary["data"]["branch_count"] == 1
        assert summary["data"]["world"]["object_count"] >= 1

        status, _, scenes = _request(server, "GET", "/api/scenes")
        assert status == 200
        assert scenes["data"]["scenes"][0]["participant_count"] == 2

        status, _, graph = _request(server, "GET", "/api/graph?scene_id=scene_web_1")
        assert status == 200
        node_ids = {node["id"] for node in graph["data"]["nodes"]}
        edge_ids = {edge["id"] for edge in graph["data"]["edges"]}
        assert {"person_web_1", "person_web_2", "memory_web_1"}.issubset(node_ids)
        assert "relation_web_1" in edge_ids

        status, _, world = _request(server, "GET", "/api/world?scene_id=scene_web_1")
        assert status == 200
        assert len(world["data"]["objects"]) >= 1
        assert len(world["data"]["projects"]) >= 1

        status, _, branches = _request(server, "GET", "/api/branches?status=open")
        assert status == 200
        assert branches["data"]["branches"][0]["branch_id"] == "branch_web_1"
        assert branches["data"]["branches"][0]["candidates"][0]["candidate_id"] == "candidate_web_1"
    finally:
        server.shutdown()
        server.server_close()


def test_webui_entity_detail_person_relation_memory(temp_project_with_migrations):
    _seed_webui_graph(temp_project_with_migrations)
    server = _start_server(temp_project_with_migrations)
    try:
        for entity_type, entity_id in [
            ("person", "person_web_1"),
            ("relation", "relation_web_1"),
            ("memory", "memory_web_1"),
            ("group", "group_web_1"),
        ]:
            status, _, payload = _request(server, "GET", f"/api/entities/{entity_type}/{entity_id}")
            assert status == 200
            assert payload["data"]["entity"]["id"] == entity_id
            assert payload["data"]["entity"]["type"] == entity_type
    finally:
        server.shutdown()
        server.server_close()


def test_webui_patch_update_person_records_patch(temp_project_with_migrations):
    seeded = _seed_webui_graph(temp_project_with_migrations)
    server = _start_server(temp_project_with_migrations)
    try:
        status, _, payload = _request(
            server,
            "PATCH",
            "/api/entities/person/person_web_1",
            body={"fields": {"primary_name": "Alice Web", "persona": "ships with care"}},
        )
        assert status == 200
        assert payload["data"]["patch_id"].startswith("patch_")
        assert payload["data"]["event_id"].startswith("webui_event_")
        assert payload["data"]["summary"]["person_count"] == 2

        conn = sqlite3.connect(seeded["db_path"])
        row = conn.execute(
            "SELECT primary_name, persona_summary FROM persons WHERE person_id='person_web_1'"
        ).fetchone()
        patch_row = conn.execute(
            "SELECT operation, target_type, target_id, status FROM patches WHERE patch_id=?",
            (payload["data"]["patch_id"],),
        ).fetchone()
        conn.close()
        assert row == ("Alice Web", "ships with care")
        assert patch_row == ("update_entity", "person", "person_web_1", "applied")
    finally:
        server.shutdown()
        server.server_close()


def test_webui_link_unlink_entities_records_patch(temp_project_with_migrations):
    seeded = _seed_webui_graph(temp_project_with_migrations)
    server = _start_server(temp_project_with_migrations)
    try:
        link_body = {
            "from_type": "person",
            "from_id": "person_web_1",
            "relation_type": "remembers",
            "to_type": "memory",
            "to_id": "memory_web_1",
            "weight": 0.9,
        }
        status, _, linked = _request(server, "POST", "/api/entities/link", body=link_body)
        assert status == 200
        assert linked["data"]["patch_id"].startswith("patch_")

        status, _, unlinked = _request(server, "POST", "/api/entities/unlink", body=link_body)
        assert status == 200
        assert unlinked["data"]["patch_id"].startswith("patch_")

        conn = sqlite3.connect(seeded["db_path"])
        operations = [
            row[0]
            for row in conn.execute(
                "SELECT operation FROM patches WHERE target_type='entity_link' ORDER BY created_at"
            ).fetchall()
        ]
        link_count = conn.execute(
            """
            SELECT COUNT(*) FROM entity_links
            WHERE from_type='person' AND from_id='person_web_1'
            AND relation_type='remembers' AND to_type='memory' AND to_id='memory_web_1'
            """
        ).fetchone()[0]
        conn.close()
        assert "link_entities" in operations
        assert "unlink_entities" in operations
        assert link_count == 0
    finally:
        server.shutdown()
        server.server_close()


def test_webui_chat_run_turn_returns_text_and_event(temp_project_with_migrations):
    _seed_webui_graph(temp_project_with_migrations)
    server = _start_server(temp_project_with_migrations)
    try:
        status, _, payload = _request(
            server,
            "POST",
            "/api/chat/run-turn",
            body={"scene_id": "scene_web_1", "input": "早上好"},
        )
        assert status == 200
        assert payload["data"]["text"] == "你好，我收到了。"
        assert payload["data"]["event_id"].startswith("evt_")
        assert payload["data"]["snapshot_id"].startswith("snap_")
    finally:
        server.shutdown()
        server.server_close()


def test_webui_world_active_world_and_create_object(temp_project_with_migrations):
    seeded = _seed_webui_graph(temp_project_with_migrations)
    server = _start_server(temp_project_with_migrations)
    try:
        status, _, payload = _request(
            server,
            "POST",
            "/api/world/objects",
            body={
                "kind": "artifact",
                "name": "Review Token",
                "owner_type": "person",
                "owner_id": "person_web_2",
            },
        )
        assert status == 200
        assert payload["data"]["object_id"].startswith("obj_")
        assert payload["data"]["audit_event_id"].startswith("webui_event_")

        conn = sqlite3.connect(seeded["db_path"])
        event_row = conn.execute(
            "SELECT event_type, source_type FROM events WHERE event_id=?",
            (payload["data"]["audit_event_id"],),
        ).fetchone()
        conn.close()
        assert event_row == ("webui_audit", "webui")
    finally:
        server.shutdown()
        server.server_close()


def test_webui_world_object_and_project_updates_are_audited(temp_project_with_migrations):
    seeded = _seed_webui_graph(temp_project_with_migrations)
    object_id = seeded["object_id"]
    project_id = seeded["project_id"]
    server = _start_server(temp_project_with_migrations)
    try:
        status, _, owner_payload = _request(
            server,
            "PATCH",
            f"/api/world/objects/{object_id}/owner",
            body={"owner_type": "person", "owner_id": "person_web_2"},
        )
        assert status == 200
        assert owner_payload["data"]["object_id"] == object_id
        assert owner_payload["data"]["audit_event_id"].startswith("webui_event_")

        status, _, status_payload = _request(
            server,
            "PATCH",
            f"/api/world/objects/{object_id}/status",
            body={"status": "lost"},
        )
        assert status == 200
        assert status_payload["data"]["object_id"] == object_id
        assert status_payload["data"]["status"] == "lost"
        assert status_payload["data"]["audit_event_id"].startswith("webui_event_")

        status, _, project_payload = _request(
            server,
            "PATCH",
            f"/api/world/projects/{project_id}/status",
            body={"status": "completed"},
        )
        assert status == 200
        assert project_payload["data"]["project_id"] == project_id
        assert project_payload["data"]["status"] == "completed"
        assert project_payload["data"]["audit_event_id"].startswith("webui_event_")

        conn = sqlite3.connect(seeded["db_path"])
        object_row = conn.execute(
            "SELECT owner_type, owner_id, status FROM objects WHERE object_id=?",
            (object_id,),
        ).fetchone()
        history_row = conn.execute(
            """
            SELECT from_owner_id, to_owner_id, event_id
            FROM object_ownership_history
            WHERE object_id=?
            ORDER BY history_id DESC
            LIMIT 1
            """,
            (object_id,),
        ).fetchone()
        old_link_count = conn.execute(
            """
            SELECT COUNT(*) FROM entity_links
            WHERE from_type='person' AND from_id='person_web_1'
            AND relation_type='owns' AND to_type='object' AND to_id=?
            """,
            (object_id,),
        ).fetchone()[0]
        new_link_count = conn.execute(
            """
            SELECT COUNT(*) FROM entity_links
            WHERE from_type='person' AND from_id='person_web_2'
            AND relation_type='owns' AND to_type='object' AND to_id=?
            """,
            (object_id,),
        ).fetchone()[0]
        project_status = conn.execute(
            "SELECT status FROM projects WHERE project_id=?",
            (project_id,),
        ).fetchone()[0]
        audit_count = conn.execute(
            """
            SELECT COUNT(*) FROM events
            WHERE event_type='webui_audit'
            AND event_id IN (?, ?, ?)
            """,
            (
                owner_payload["data"]["audit_event_id"],
                status_payload["data"]["audit_event_id"],
                project_payload["data"]["audit_event_id"],
            ),
        ).fetchone()[0]
        conn.close()

        assert object_row == ("person", "person_web_2", "lost")
        assert history_row[0] == "person_web_1"
        assert history_row[1] == "person_web_2"
        assert history_row[2] == owner_payload["data"]["audit_event_id"]
        assert old_link_count == 0
        assert new_link_count == 1
        assert project_status == "completed"
        assert audit_count == 3
    finally:
        server.shutdown()
        server.server_close()


def test_webui_branch_resolve_uses_patch(temp_project_with_migrations):
    seeded = _seed_webui_graph(temp_project_with_migrations)
    server = _start_server(temp_project_with_migrations)
    try:
        status, _, payload = _request(
            server,
            "POST",
            "/api/branches/branch_web_1/resolve",
            body={"candidate_id": "candidate_web_1", "reason": "operator approved"},
        )
        assert status == 200
        assert payload["data"]["patch_id"].startswith("patch_")

        conn = sqlite3.connect(seeded["db_path"])
        status_row = conn.execute(
            "SELECT status FROM local_branches WHERE branch_id='branch_web_1'"
        ).fetchone()[0]
        patch_row = conn.execute(
            "SELECT operation, target_type, target_id, status FROM patches WHERE patch_id=?",
            (payload["data"]["patch_id"],),
        ).fetchone()
        conn.close()
        assert status_row == "resolved"
        assert patch_row == ("resolve_local_branch", "local_branch", "branch_web_1", "applied")
    finally:
        server.shutdown()
        server.server_close()


def test_webui_static_spa_served(temp_project_with_migrations, tmp_path):
    _seed_webui_graph(temp_project_with_migrations)
    static_dir = tmp_path / "webui-dist"
    static_dir.mkdir()
    (static_dir / "index.html").write_text("<html><body>we-together webui</body></html>", encoding="utf-8")
    server = _start_server(temp_project_with_migrations, static_dir=static_dir)
    try:
        status, text, _ = _request(server, "GET", "/", token=None)
        assert status == 200
        assert "we-together webui" in text
    finally:
        server.shutdown()
        server.server_close()
