from we_together.db.bootstrap import bootstrap_project
from we_together.runtime.sqlite_retrieval import build_runtime_retrieval_package_from_db
from we_together.services.group_service import create_group, add_group_member
from we_together.services.patch_applier import apply_patch_record
from we_together.services.patch_service import build_patch
from we_together.services.scene_service import create_scene, add_scene_participant
from we_together.services.ingestion_service import ingest_narration, ingest_text_chat
import sqlite3


def test_build_runtime_retrieval_package_from_db_reads_scene_and_participants(
    temp_project_with_migrations,
):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="late night remote chat",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
            "time_scope": "late_night",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id="person_alice",
        activation_state="explicit",
        activation_score=0.95,
        is_speaking=True,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)

    assert package["scene_summary"]["scene_id"] == scene_id
    assert package["environment_constraints"]["channel_scope"] == "private_dm"
    assert len(package["participants"]) == 1
    assert package["activation_map"][0]["activation_state"] == "explicit"


def test_build_runtime_retrieval_package_uses_person_names_and_active_relations(
    temp_project_with_migrations,
):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    ingest_narration(
        db_path=db_path,
        text="小王和小李以前是同事，现在还是朋友。",
        source_name="manual-note",
    )

    conn = sqlite3.connect(db_path)
    people = {
        row[1]: row[0]
        for row in conn.execute("SELECT person_id, primary_name FROM persons").fetchall()
    }
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="friends chat",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id=people["小王"],
        activation_state="explicit",
        activation_score=0.95,
        is_speaking=True,
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id=people["小李"],
        activation_state="latent",
        activation_score=0.85,
        is_speaking=False,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)

    display_names = {item["display_name"] for item in package["participants"]}
    assert "小王" in display_names
    assert "小李" in display_names
    assert len(package["active_relations"]) >= 1
    assert len(package["relevant_memories"]) >= 1


def test_retrieval_package_includes_group_context_when_scene_has_group(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    group_id = create_group(
        db_path=db_path,
        group_type="team",
        name="核心团队",
        summary="主开发小组",
    )
    add_group_member(db_path=db_path, group_id=group_id, person_id="person_alice", role_label="owner")

    scene_id = create_scene(
        db_path=db_path,
        scene_type="work_discussion",
        scene_summary="team sync",
        environment={
            "location_scope": "remote",
            "channel_scope": "group_channel",
            "visibility_scope": "group_visible",
        },
        group_id=group_id,
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id="person_alice",
        activation_state="explicit",
        activation_score=1.0,
        is_speaking=True,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)

    assert package["scene_summary"]["group_id"] == group_id
    assert package["group_context"]["group_id"] == group_id
    assert package["group_context"]["name"] == "核心团队"


def test_retrieval_package_includes_state_scopes_and_relation_participants(
    temp_project_with_migrations,
):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    ingest_narration(
        db_path=db_path,
        text="小王和小李以前是同事，现在还是朋友。",
        source_name="manual-note",
    )

    conn = sqlite3.connect(db_path)
    people = {
        row[1]: row[0]
        for row in conn.execute("SELECT person_id, primary_name FROM persons").fetchall()
    }
    relation_id = conn.execute("SELECT relation_id FROM relations LIMIT 1").fetchone()[0]
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="friends chat",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id=people["小王"],
        activation_state="explicit",
        activation_score=0.95,
        is_speaking=True,
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id=people["小李"],
        activation_state="latent",
        activation_score=0.85,
        is_speaking=False,
    )

    apply_patch_record(
        db_path=db_path,
        patch=build_patch(
            source_event_id="evt_scene_state",
            target_type="state",
            target_id="state_scene_1",
            operation="update_state",
            payload={
                "state_id": "state_scene_1",
                "scope_type": "scene",
                "scope_id": scene_id,
                "state_type": "mood",
                "value_json": {"mood": "warm"},
            },
            confidence=0.8,
            reason="scene state",
        ),
    )
    apply_patch_record(
        db_path=db_path,
        patch=build_patch(
            source_event_id="evt_person_state",
            target_type="state",
            target_id="state_person_1",
            operation="update_state",
            payload={
                "state_id": "state_person_1",
                "scope_type": "person",
                "scope_id": people["小王"],
                "state_type": "energy",
                "value_json": {"energy": "tired"},
            },
            confidence=0.7,
            reason="person state",
        ),
    )
    apply_patch_record(
        db_path=db_path,
        patch=build_patch(
            source_event_id="evt_relation_state",
            target_type="state",
            target_id="state_relation_1",
            operation="update_state",
            payload={
                "state_id": "state_relation_1",
                "scope_type": "relation",
                "scope_id": relation_id,
                "state_type": "tone",
                "value_json": {"tone": "trusting"},
            },
            confidence=0.75,
            reason="relation state",
        ),
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)

    relation_entry = package["active_relations"][0]
    relation_participants = {item["display_name"] for item in relation_entry["participants"]}
    state_scopes = {(item["scope_type"], item["scope_id"]) for item in package["current_states"]}

    assert relation_participants == {"小王", "小李"}
    assert ("scene", scene_id) in state_scopes
    assert ("person", people["小王"]) in state_scopes
    assert ("relation", relation_id) in state_scopes


def test_inferred_text_chat_state_flows_into_current_states(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    from we_together.services.ingestion_service import ingest_text_chat

    ingest_text_chat(
        db_path=db_path,
        transcript="2026-04-06 23:10 小王: 今天好累\n2026-04-06 23:11 小李: 早点休息\n",
        source_name="chat.txt",
    )

    conn = sqlite3.connect(db_path)
    people = {
        row[1]: row[0]
        for row in conn.execute("SELECT person_id, primary_name FROM persons").fetchall()
    }
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="state retrieval",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id=people["小王"],
        activation_state="explicit",
        activation_score=0.95,
        is_speaking=True,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)
    person_states = [
        item for item in package["current_states"]
        if item["scope_type"] == "person" and item["scope_id"] == people["小王"]
    ]

    assert any(item["state_type"] == "energy" for item in person_states)


def test_group_scene_adds_group_members_as_latent_activation(
    temp_project_with_migrations,
):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    group_id = create_group(
        db_path=db_path,
        group_type="team",
        name="核心团队",
        summary="主开发小组",
    )
    add_group_member(db_path=db_path, group_id=group_id, person_id="person_alice", role_label="owner")
    add_group_member(db_path=db_path, group_id=group_id, person_id="person_bob", role_label="member")

    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO persons(
            person_id, primary_name, status, summary, persona_summary, work_summary,
            life_summary, style_summary, boundary_summary, confidence, metadata_json,
            created_at, updated_at
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        ("person_alice", "Alice", "active", None, None, None, None, None, None, 0.8, "{}"),
    )
    conn.execute(
        """
        INSERT INTO persons(
            person_id, primary_name, status, summary, persona_summary, work_summary,
            life_summary, style_summary, boundary_summary, confidence, metadata_json,
            created_at, updated_at
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        ("person_bob", "Bob", "active", None, None, None, None, None, None, 0.8, "{}"),
    )
    conn.commit()
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="work_discussion",
        scene_summary="team sync",
        environment={
            "location_scope": "remote",
            "channel_scope": "group_channel",
            "visibility_scope": "group_visible",
        },
        group_id=group_id,
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id="person_alice",
        activation_state="explicit",
        activation_score=1.0,
        is_speaking=True,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)

    activation_map = {item["person_id"]: item for item in package["activation_map"]}

    assert activation_map["person_bob"]["activation_state"] == "latent"
    assert activation_map["person_bob"]["activation_score"] > 0
    assert package["response_policy"]["mode"] == "primary_plus_support"


def test_shared_memory_can_activate_latent_participant_without_group_context(
    temp_project_with_migrations,
):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    ingest_narration(
        db_path=db_path,
        text="小王和小李以前是同事，现在还是朋友。",
        source_name="manual-note",
    )

    conn = sqlite3.connect(db_path)
    people = {
        row[1]: row[0]
        for row in conn.execute("SELECT person_id, primary_name FROM persons").fetchall()
    }
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="memory recall",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id=people["小王"],
        activation_state="explicit",
        activation_score=1.0,
        is_speaking=True,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)
    activation_map = {item["person_id"]: item for item in package["activation_map"]}

    assert activation_map[people["小李"]]["activation_state"] == "latent"
    assert activation_map[people["小李"]]["activation_score"] > 0
    assert package["response_policy"]["mode"] == "single_primary"
    assert package["response_policy"]["primary_speaker"] == people["小王"]


def test_active_relation_can_activate_latent_participant_without_group_context(
    temp_project_with_migrations,
):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO persons(
            person_id, primary_name, status, summary, persona_summary, work_summary,
            life_summary, style_summary, boundary_summary, confidence, metadata_json,
            created_at, updated_at
        ) VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now')),
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        (
            "person_alice", "Alice", "active", None, None, None, None, None, None, 0.8, "{}",
            "person_carla", "Carla", "active", None, None, None, None, None, None, 0.8, "{}",
        ),
    )
    conn.execute(
        """
        INSERT INTO relations(
            relation_id, core_type, custom_label, summary, directionality,
            strength, stability, visibility, status, time_start, time_end,
            confidence, metadata_json, created_at, updated_at
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        (
            "relation_ac",
            "friendship",
            "朋友",
            "Alice 与 Carla 关系亲近",
            "bidirectional",
            0.7,
            0.6,
            "known",
            "active",
            None,
            None,
            0.7,
            "{}",
        ),
    )
    conn.execute(
        """
        INSERT INTO events(
            event_id, event_type, source_type, scene_id, group_id,
            timestamp, summary, visibility_level, confidence, is_structured,
            raw_evidence_refs_json, metadata_json, created_at
        ) VALUES(?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            "evt_relation_seed",
            "narration_imported",
            "manual",
            None,
            None,
            "Alice remembers Carla",
            "visible",
            0.8,
            0,
            "[]",
            "{}",
        ),
    )
    conn.executemany(
        """
        INSERT INTO event_participants(event_id, person_id, participant_role)
        VALUES(?, ?, ?)
        """,
        [
            ("evt_relation_seed", "person_alice", "mentioned"),
            ("evt_relation_seed", "person_carla", "mentioned"),
        ],
    )
    conn.execute(
        """
        INSERT INTO event_targets(event_id, target_type, target_id, impact_hint)
        VALUES(?, ?, ?, ?)
        """,
        ("evt_relation_seed", "relation", "relation_ac", "朋友"),
    )
    conn.commit()
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="alice solo chat",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id="person_alice",
        activation_state="explicit",
        activation_score=1.0,
        is_speaking=True,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)
    activation_map = {item["person_id"]: item for item in package["activation_map"]}

    assert activation_map["person_carla"]["activation_state"] == "latent"
    assert activation_map["person_carla"]["activation_score"] > 0
    assert package["response_policy"]["mode"] == "single_primary"


def test_strict_activation_barrier_blocks_derived_latent_activation(
    temp_project_with_migrations,
):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    group_id = create_group(
        db_path=db_path,
        group_type="team",
        name="核心团队",
        summary="主开发小组",
    )
    add_group_member(db_path=db_path, group_id=group_id, person_id="person_alice", role_label="owner")
    add_group_member(db_path=db_path, group_id=group_id, person_id="person_bob", role_label="member")

    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO persons(
            person_id, primary_name, status, summary, persona_summary, work_summary,
            life_summary, style_summary, boundary_summary, confidence, metadata_json,
            created_at, updated_at
        ) VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now')),
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        (
            "person_alice", "Alice", "active", None, None, None, None, None, None, 0.8, "{}",
            "person_bob", "Bob", "active", None, None, None, None, None, None, 0.8, "{}",
        ),
    )
    conn.commit()
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="work_discussion",
        scene_summary="strict team sync",
        environment={
            "location_scope": "remote",
            "channel_scope": "group_channel",
            "visibility_scope": "group_visible",
            "activation_barrier": "strict",
        },
        group_id=group_id,
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id="person_alice",
        activation_state="explicit",
        activation_score=1.0,
        is_speaking=True,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)
    activation_map = {item["person_id"]: item for item in package["activation_map"]}

    assert "person_bob" not in activation_map
    assert package["response_policy"]["mode"] == "single_primary"


def test_high_activation_barrier_limits_derived_latent_budget(
    temp_project_with_migrations,
):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    group_id = create_group(
        db_path=db_path,
        group_type="team",
        name="核心团队",
        summary="主开发小组",
    )
    add_group_member(db_path=db_path, group_id=group_id, person_id="person_alice", role_label="owner")
    add_group_member(db_path=db_path, group_id=group_id, person_id="person_bob", role_label="member")
    add_group_member(db_path=db_path, group_id=group_id, person_id="person_carla", role_label="member")

    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO persons(
            person_id, primary_name, status, summary, persona_summary, work_summary,
            life_summary, style_summary, boundary_summary, confidence, metadata_json,
            created_at, updated_at
        ) VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now')),
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now')),
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        (
            "person_alice", "Alice", "active", None, None, None, None, None, None, 0.8, "{}",
            "person_bob", "Bob", "active", None, None, None, None, None, None, 0.8, "{}",
            "person_carla", "Carla", "active", None, None, None, None, None, None, 0.8, "{}",
        ),
    )
    conn.commit()
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="work_discussion",
        scene_summary="high barrier team sync",
        environment={
            "location_scope": "remote",
            "channel_scope": "group_channel",
            "visibility_scope": "group_visible",
            "activation_barrier": "high",
        },
        group_id=group_id,
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id="person_alice",
        activation_state="explicit",
        activation_score=1.0,
        is_speaking=True,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)

    latent_ids = [
        item["person_id"]
        for item in package["activation_map"]
        if item["activation_state"] == "latent"
    ]
    budget = package["safety_and_budget"]["activation_budget"]

    assert len(latent_ids) == 1
    assert budget["max_derived_latent"] == 1
    assert budget["used_derived_latent"] == 1
    assert budget["blocked_derived_latent"] == 1


def test_relation_participants_activation_latent_by_default(
    temp_project_with_migrations,
):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    ingest_narration(
        db_path=db_path,
        text="小王和小李以前是同事，现在还是朋友。",
        source_name="manual-note",
    )

    conn = sqlite3.connect(db_path)
    people = {
        row[1]: row[0]
        for row in conn.execute("SELECT person_id, primary_name FROM persons").fetchall()
    }
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="relation latent test",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
            "activation_barrier": "low",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id=people["小王"],
        activation_state="explicit",
        activation_score=0.9,
        is_speaking=True,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)
    activation_map = {item["person_id"]: item for item in package["activation_map"]}

    relation_partner = people["小李"]
    assert relation_partner in activation_map
    assert activation_map[relation_partner]["activation_state"] == "latent"
    assert package["response_policy"]["mode"] == "single_primary"


def test_relation_participants_blocked_when_activation_barrier_strict(
    temp_project_with_migrations,
):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    ingest_narration(
        db_path=db_path,
        text="小王和小李以前是同事，现在还是朋友。",
        source_name="manual-note",
    )

    conn = sqlite3.connect(db_path)
    people = {
        row[1]: row[0]
        for row in conn.execute("SELECT person_id, primary_name FROM persons").fetchall()
    }
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="relation strict barrier",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
            "activation_barrier": "strict",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id=people["小王"],
        activation_state="explicit",
        activation_score=0.9,
        is_speaking=True,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)
    activation_map = {item["person_id"]: item for item in package["activation_map"]}

    relation_partner = people["小李"]
    assert relation_partner not in activation_map
    assert package["response_policy"]["mode"] == "single_primary"


def test_event_participants_trigger_additional_latent_activation(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="event activation",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id="person_alice",
        activation_state="explicit",
        activation_score=0.9,
        is_speaking=True,
    )

    conn = sqlite3.connect(db_path)
    conn.executemany(
        """
        INSERT INTO events(event_id, event_type, source_type, timestamp, summary, visibility_level, confidence, is_structured, raw_evidence_refs_json, metadata_json, created_at)
        VALUES(?, ?, ?, datetime('now'), ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        [
            (
                "evt_extra",
                "dialogue_event",
                "system",
                "event triggered activation",
                1.0,
                0,
                1,
                "[]",
                "{}",
            ),
        ],
    )
    conn.executemany(
        """
        INSERT INTO event_participants(event_id, person_id, participant_role)
        VALUES(?, ?, ?)
        """,
        [
            ("evt_extra", "person_alice", "speaker"),
            ("evt_extra", "person_bob", "mentioned"),
        ],
    )
    conn.commit()
    conn.close()

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)
    activation_map = {item["person_id"]: item for item in package["activation_map"]}

    assert "person_bob" in activation_map
    assert activation_map["person_bob"]["activation_state"] == "latent"
    assert package["response_policy"]["mode"] == "single_primary"
    budget = package["safety_and_budget"]["activation_budget"]
    assert budget["used_event_latent"] == 1
    assert package["safety_and_budget"]["propagation_depth"] == 2


def test_event_budget_report_includes_weights(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    scene_id = create_scene(
        db_path=db_path,
        scene_type="work_discussion",
        scene_summary="event budget",
        environment={
            "location_scope": "remote",
            "channel_scope": "group_channel",
            "visibility_scope": "group_visible",
            "activation_barrier": "medium",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id="person_alice",
        activation_state="explicit",
        activation_score=1.0,
        is_speaking=True,
    )

    conn = sqlite3.connect(db_path)
    conn.executemany(
        """
        INSERT INTO events(event_id, event_type, source_type, timestamp, summary, visibility_level, confidence, is_structured, raw_evidence_refs_json, metadata_json, created_at)
        VALUES(?, ?, ?, datetime('now'), ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        [
            (
                "evt_event_budget",
                "dialogue_event",
                "system",
                "event drives budget",
                1.0,
                0,
                1,
                "[]",
                "{}",
            ),
        ],
    )
    conn.executemany(
        """
        INSERT INTO event_participants(event_id, person_id, participant_role)
        VALUES(?, ?, ?)
        """,
        [
            ("evt_event_budget", "person_alice", "speaker"),
            ("evt_event_budget", "person_bob", "mentioned"),
        ],
    )
    conn.commit()
    conn.close()

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)
    budget = package["safety_and_budget"]["activation_budget"]

    assert budget["max_derived_latent"] >= 1
    assert budget["event_weight"] == 0.8
    assert package["safety_and_budget"]["source_weights"]["event"] == 0.8
    assert package["safety_and_budget"]["event_decay_days"] == 30


def test_old_event_participants_receive_decay_limited_activation(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="old event activation",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
            "activation_barrier": "low",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id="person_alice",
        activation_state="explicit",
        activation_score=0.9,
        is_speaking=True,
    )

    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO events(event_id, event_type, source_type, timestamp, summary, visibility_level, confidence, is_structured, raw_evidence_refs_json, metadata_json, created_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            "evt_old",
            "dialogue_event",
            "system",
            "2024-01-01T00:00:00+00:00",
            "old event activation",
            "visible",
            1.0,
            0,
            "[]",
            "{}",
        ),
    )
    conn.executemany(
        """
        INSERT INTO event_participants(event_id, person_id, participant_role)
        VALUES(?, ?, ?)
        """,
        [
            ("evt_old", "person_alice", "speaker"),
            ("evt_old", "person_bob", "mentioned"),
        ],
    )
    conn.commit()
    conn.close()

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)
    activation_map = {item["person_id"]: item for item in package["activation_map"]}

    assert activation_map["person_bob"]["activation_state"] == "latent"
    assert activation_map["person_bob"]["activation_score"] < 0.5


def test_text_chat_imported_relations_are_visible_in_runtime_retrieval(
    temp_project_with_migrations,
):
    bootstrap_project(temp_project_with_migrations)
    db_path = temp_project_with_migrations / "db" / "main.sqlite3"

    transcript = """2026-04-06 23:10 小王: 今天好累
2026-04-06 23:11 小李: 早点休息
"""
    ingest_text_chat(
        db_path=db_path,
        transcript=transcript,
        source_name="chat.txt",
    )

    conn = sqlite3.connect(db_path)
    people = {
        row[1]: row[0]
        for row in conn.execute("SELECT person_id, primary_name FROM persons").fetchall()
    }
    conn.close()

    scene_id = create_scene(
        db_path=db_path,
        scene_type="private_chat",
        scene_summary="text chat retrieval",
        environment={
            "location_scope": "remote",
            "channel_scope": "private_dm",
            "visibility_scope": "mutual_visible",
        },
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id=people["小王"],
        activation_state="explicit",
        activation_score=0.95,
        is_speaking=True,
    )
    add_scene_participant(
        db_path=db_path,
        scene_id=scene_id,
        person_id=people["小李"],
        activation_state="latent",
        activation_score=0.75,
        is_speaking=False,
    )

    package = build_runtime_retrieval_package_from_db(db_path=db_path, scene_id=scene_id)

    relation_ids = {item["relation_id"] for item in package["active_relations"]}
    assert relation_ids
