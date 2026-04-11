import json
import sqlite3

from we_together.db.bootstrap import bootstrap_project
from we_together.services.dialogue_service import record_dialogue_event
from we_together.services.scene_service import create_scene, add_scene_participant


def test_record_dialogue_event_creates_event_and_participants(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO persons(
            person_id, primary_name, status, summary, persona_summary, work_summary,
            life_summary, style_summary, boundary_summary, confidence, metadata_json,
            created_at, updated_at
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        ("person_dlg_a", "小明", "active", None, None, None, None, None, None, 0.8, "{}"),
    )
    conn.commit()
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="dialogue test",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id="person_dlg_a",
        activation_state="explicit",
        activation_score=1.0,
        is_speaking=True,
    )

    result = record_dialogue_event(
        db_path=db_path,
        scene_id=scene_id,
        user_input="今天心情怎么样？",
        response_text="挺好的，谢谢关心。",
        speaking_person_ids=["person_dlg_a"],
    )

    assert "event_id" in result
    assert result["event_type"] == "dialogue_event"

    conn = sqlite3.connect(db_path)
    event_row = conn.execute(
        "SELECT event_type, source_type, scene_id, summary FROM events WHERE event_id = ?",
        (result["event_id"],),
    ).fetchone()
    participant_rows = conn.execute(
        "SELECT person_id, participant_role FROM event_participants WHERE event_id = ?",
        (result["event_id"],),
    ).fetchall()
    conn.close()

    assert event_row[0] == "dialogue_event"
    assert event_row[1] == "dialogue"
    assert event_row[2] == scene_id
    assert len(participant_rows) >= 1
    assert participant_rows[0][1] == "speaker"


def test_record_dialogue_event_creates_snapshot(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="snapshot dialogue test",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
        },
    )

    result = record_dialogue_event(
        db_path=db_path,
        scene_id=scene_id,
        user_input="你好",
        response_text="你好呀",
        speaking_person_ids=[],
    )

    assert result["snapshot_id"] is not None
    conn = sqlite3.connect(db_path)
    snap_row = conn.execute(
        "SELECT snapshot_id FROM snapshots WHERE snapshot_id = ?",
        (result["snapshot_id"],),
    ).fetchone()
    conn.close()
    assert snap_row is not None
