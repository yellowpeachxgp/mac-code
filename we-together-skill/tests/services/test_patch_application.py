import json
import sqlite3
import pytest

from we_together.db.bootstrap import bootstrap_project
from we_together.services.patch_applier import apply_patch_record
from we_together.services.patch_service import build_patch


def test_apply_patch_record_can_create_memory(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    patch = build_patch(
        source_event_id="evt_1",
        target_type="memory",
        target_id="memory_1",
        operation="create_memory",
        payload={
            "memory_id": "memory_1",
            "memory_type": "shared_memory",
            "summary": "一起熬夜聊天",
            "confidence": 0.8,
            "is_shared": 1,
            "status": "active",
            "metadata_json": {"source_event_id": "evt_1"},
        },
        confidence=0.8,
        reason="test memory patch",
    )

    apply_patch_record(db_path=db_path, patch=patch)

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT summary FROM memories WHERE memory_id = ?",
        ("memory_1",),
    ).fetchone()
    patch_row = conn.execute(
        "SELECT status FROM patches WHERE patch_id = ?",
        (patch["patch_id"],),
    ).fetchone()
    conn.close()

    assert row[0] == "一起熬夜聊天"
    assert patch_row[0] == "applied"


def test_apply_patch_record_can_update_state(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    patch = build_patch(
        source_event_id="evt_2",
        target_type="state",
        target_id="state_1",
        operation="update_state",
        payload={
            "state_id": "state_1",
            "scope_type": "scene",
            "scope_id": "scene_1",
            "state_type": "mood",
            "value_json": {"mood": "tense"},
            "confidence": 0.9,
            "is_inferred": 1,
            "decay_policy": None,
            "source_event_refs_json": ["evt_2"],
        },
        confidence=0.9,
        reason="test state patch",
    )

    apply_patch_record(db_path=db_path, patch=patch)

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT value_json FROM states WHERE state_id = ?",
        ("state_1",),
    ).fetchone()
    conn.close()

    assert json.loads(row[0])["mood"] == "tense"


def test_apply_patch_record_can_link_entities(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    patch = build_patch(
        source_event_id="evt_3",
        target_type="entity_link",
        target_id=None,
        operation="link_entities",
        payload={
            "from_type": "memory",
            "from_id": "memory_a",
            "relation_type": "supports",
            "to_type": "memory",
            "to_id": "memory_b",
            "weight": 0.75,
            "metadata_json": {"context": "nightly session"},
        },
        confidence=0.6,
        reason="test entity link patch",
    )

    apply_patch_record(db_path=db_path, patch=patch)

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT weight, metadata_json FROM entity_links WHERE from_type = ? AND from_id = ? AND to_id = ?",
        ("memory", "memory_a", "memory_b"),
    ).fetchone()
    conn.close()

    assert row is not None
    assert row[0] == 0.75
    assert json.loads(row[1])["context"] == "nightly session"


def test_apply_patch_record_can_create_local_branch(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    patch = build_patch(
        source_event_id="evt_4",
        target_type="local_branch",
        target_id="branch_1",
        operation="create_local_branch",
        payload={
            "branch_id": "branch_1",
            "scope_type": "relation",
            "scope_id": "relation_1",
            "status": "open",
            "reason": "conflicting relation evidence",
            "created_from_event_id": "evt_4",
        },
        confidence=0.7,
        reason="test local branch patch",
    )

    apply_patch_record(db_path=db_path, patch=patch)

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT scope_type, scope_id, status, reason, created_from_event_id FROM local_branches WHERE branch_id = ?",
        ("branch_1",),
    ).fetchone()
    conn.close()

    assert row == ("relation", "relation_1", "open", "conflicting relation evidence", "evt_4")


def test_apply_patch_record_can_resolve_local_branch(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    create_patch = build_patch(
        source_event_id="evt_5",
        target_type="local_branch",
        target_id="branch_2",
        operation="create_local_branch",
        payload={
            "branch_id": "branch_2",
            "scope_type": "person",
            "scope_id": "person_1",
            "status": "open",
            "reason": "identity ambiguity",
            "created_from_event_id": "evt_5",
        },
        confidence=0.6,
        reason="open local branch",
    )
    apply_patch_record(db_path=db_path, patch=create_patch)

    resolve_patch = build_patch(
        source_event_id="evt_6",
        target_type="local_branch",
        target_id="branch_2",
        operation="resolve_local_branch",
        payload={
            "branch_id": "branch_2",
            "status": "resolved",
            "resolved_at": "2026-04-09T12:00:00+08:00",
            "reason": "merged after confirmation",
        },
        confidence=0.8,
        reason="resolve local branch",
    )

    apply_patch_record(db_path=db_path, patch=resolve_patch)

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT status, reason, resolved_at FROM local_branches WHERE branch_id = ?",
        ("branch_2",),
    ).fetchone()
    conn.close()

    assert row == ("resolved", "merged after confirmation", "2026-04-09T12:00:00+08:00")


def test_apply_patch_record_marks_failed_for_unsupported_operation(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    patch = build_patch(
        source_event_id="evt_unsupported",
        target_type="unknown",
        target_id="unknown",
        operation="unsupported_operation",
        payload={},
        confidence=0.1,
        reason="unsupported"
    )

    with pytest.raises(ValueError):
        apply_patch_record(db_path=db_path, patch=patch)

    conn = sqlite3.connect(db_path)
    patch_row = conn.execute(
        "SELECT status FROM patches WHERE patch_id = ?",
        (patch["patch_id"],),
    ).fetchone()
    conn.close()

    assert patch_row[0] == "failed"


def test_apply_patch_record_can_unlink_entities(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    link_patch = build_patch(
        source_event_id="evt_link",
        target_type="entity_link",
        target_id=None,
        operation="link_entities",
        payload={
            "from_type": "memory",
            "from_id": "memory_x",
            "relation_type": "supports",
            "to_type": "memory",
            "to_id": "memory_y",
            "weight": 0.6,
        },
        confidence=0.5,
        reason="link to remove",
    )

    apply_patch_record(db_path=db_path, patch=link_patch)

    unlink_patch = build_patch(
        source_event_id="evt_unlink",
        target_type="entity_link",
        target_id=None,
        operation="unlink_entities",
        payload={
            "from_type": "memory",
            "from_id": "memory_x",
            "relation_type": "supports",
            "to_type": "memory",
            "to_id": "memory_y",
        },
        confidence=0.4,
        reason="unlink to clean up",
    )

    apply_patch_record(db_path=db_path, patch=unlink_patch)

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT 1 FROM entity_links WHERE from_type = ? AND from_id = ? AND to_id = ?",
        ("memory", "memory_x", "memory_y"),
    ).fetchone()
    patch_row = conn.execute(
        "SELECT status FROM patches WHERE patch_id = ?",
        (unlink_patch["patch_id"],),
    ).fetchone()
    conn.close()

    assert row is None
    assert patch_row[0] == "applied"


def test_apply_patch_record_can_mark_memory_inactive(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    create_patch = build_patch(
        source_event_id="evt_memory_create",
        target_type="memory",
        target_id="memory_z",
        operation="create_memory",
        payload={
            "memory_id": "memory_z",
            "memory_type": "shared_memory",
            "summary": "旧记忆",
            "confidence": 0.5,
            "is_shared": 1,
            "status": "active",
        },
        confidence=0.5,
        reason="seed memory",
    )
    apply_patch_record(db_path=db_path, patch=create_patch)

    inactive_patch = build_patch(
        source_event_id="evt_memory_inactive",
        target_type="memory",
        target_id="memory_z",
        operation="mark_inactive",
        payload={},
        confidence=0.4,
        reason="retire memory",
    )
    apply_patch_record(db_path=db_path, patch=inactive_patch)

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT status FROM memories WHERE memory_id = ?",
        ("memory_z",),
    ).fetchone()
    patch_row = conn.execute(
        "SELECT status FROM patches WHERE patch_id = ?",
        (inactive_patch["patch_id"],),
    ).fetchone()
    conn.close()

    assert row[0] == "inactive"
    assert patch_row[0] == "applied"


def test_apply_patch_record_can_mark_relation_inactive(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO relations(
            relation_id, core_type, custom_label, summary, directionality,
            strength, stability, visibility, status, time_start, time_end,
            confidence, metadata_json, created_at, updated_at
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        (
            "relation_inactive_test",
            "friendship",
            "朋友",
            "旧关系",
            "bidirectional",
            0.5,
            0.5,
            "known",
            "active",
            None,
            None,
            0.6,
            "{}",
        ),
    )
    conn.commit()
    conn.close()

    inactive_patch = build_patch(
        source_event_id="evt_relation_inactive",
        target_type="relation",
        target_id="relation_inactive_test",
        operation="mark_inactive",
        payload={},
        confidence=0.4,
        reason="retire relation",
    )
    apply_patch_record(db_path=db_path, patch=inactive_patch)

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT status FROM relations WHERE relation_id = ?",
        ("relation_inactive_test",),
    ).fetchone()
    conn.close()

    assert row[0] == "inactive"
