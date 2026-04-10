from datetime import UTC, datetime, timedelta
from pathlib import Path
import json
import sqlite3
import uuid


STATE_PRIORITY = {
    "inactive": 0,
    "latent": 1,
    "explicit": 2,
}

DERIVED_LATENT_BUDGET_BY_BARRIER = {
    None: 2,
    "low": 3,
    "medium": 2,
    "high": 1,
    "strict": 0,
}

EVENT_LATENT_WEIGHT = 0.8
RELATION_LATENT_WEIGHT = 0.3
GROUP_LATENT_WEIGHT = 0.35
MEMORY_LATENT_WEIGHT = 0.25
EVENT_DECAY_DAYS = 30


def invalidate_runtime_retrieval_cache(
    db_path: Path,
    scene_id: str | None = None,
) -> None:
    conn = sqlite3.connect(db_path)
    if scene_id is None:
        conn.execute(
            "DELETE FROM retrieval_cache WHERE cache_type = ?",
            ("runtime_retrieval",),
        )
    else:
        conn.execute(
            "DELETE FROM retrieval_cache WHERE cache_type = ? AND scene_id = ?",
            ("runtime_retrieval", scene_id),
        )
    conn.commit()
    conn.close()


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _apply_event_decay(timestamp_value: str | None) -> float:
    timestamp = _parse_timestamp(timestamp_value)
    if timestamp is None:
        return EVENT_LATENT_WEIGHT

    age_days = max(0.0, (datetime.now(UTC) - timestamp).total_seconds() / 86400)
    if age_days > EVENT_DECAY_DAYS:
        return EVENT_LATENT_WEIGHT * 0.25
    return EVENT_LATENT_WEIGHT


def _fetch_person_names(conn: sqlite3.Connection, person_ids: list[str]) -> dict[str, str]:
    if not person_ids:
        return {}

    rows = conn.execute(
        "SELECT person_id, primary_name FROM persons WHERE person_id IN (%s)"
        % ",".join("?" for _ in person_ids),
        tuple(person_ids),
    ).fetchall()
    return {row["person_id"]: row["primary_name"] for row in rows}


def _merge_activation_candidate(
    activation_map: dict[str, dict],
    *,
    person_id: str,
    activation_score: float,
    activation_state: str,
    reason: str,
) -> None:
    existing = activation_map.get(person_id)
    candidate = {
        "person_id": person_id,
        "activation_score": activation_score,
        "activation_state": activation_state,
        "activation_reason_summary": reason,
    }
    if not existing:
        activation_map[person_id] = candidate
        return

    if STATE_PRIORITY[activation_state] > STATE_PRIORITY[existing["activation_state"]]:
        activation_map[person_id] = candidate
        return

    if STATE_PRIORITY[activation_state] == STATE_PRIORITY[existing["activation_state"]]:
        if activation_score > existing["activation_score"]:
            activation_map[person_id] = candidate


def _merge_derived_candidate(
    derived_candidates: dict[str, dict],
    *,
    person_id: str,
    activation_score: float,
    reason: str,
    source: str | None = None,
) -> None:
    existing = derived_candidates.get(person_id)
    candidate = {
        "person_id": person_id,
        "activation_score": activation_score,
        "activation_state": "latent",
        "activation_reason_summary": reason,
        "source": source,
    }
    if not existing or activation_score > existing["activation_score"]:
        derived_candidates[person_id] = candidate


def _build_activation_map(
    conn: sqlite3.Connection,
    scene: sqlite3.Row,
    participants_rows: list[sqlite3.Row],
) -> tuple[list[dict], dict]:
    activation_map: dict[str, dict] = {}
    derived_candidates: dict[str, dict] = {}
    participant_ids = [row["person_id"] for row in participants_rows]

    for row in participants_rows:
        _merge_activation_candidate(
            activation_map,
            person_id=row["person_id"],
            activation_score=row["activation_score"] or 0.0,
            activation_state=row["activation_state"],
            reason="scene participant",
        )

    if participant_ids:
        relation_participant_rows = conn.execute(
            """
            SELECT DISTINCT ep_other.person_id
            FROM event_targets et
            JOIN event_participants ep_seed
                ON ep_seed.event_id = et.event_id
            JOIN event_participants ep_other
                ON ep_other.event_id = et.event_id
            WHERE et.target_type = 'relation'
            AND ep_seed.person_id IN (%s)
            """
            % ",".join("?" for _ in participant_ids),
            tuple(participant_ids),
        ).fetchall()
        for row in relation_participant_rows:
            if row["person_id"] in participant_ids:
                continue
            _merge_derived_candidate(
                derived_candidates,
                person_id=row["person_id"],
                activation_score=RELATION_LATENT_WEIGHT,
                reason="active relation linked to current participant",
                source="relation",
            )

    if participant_ids:
        event_participant_rows = conn.execute(
            """
            SELECT
                ep_other.person_id,
                MAX(e.timestamp) AS latest_timestamp
            FROM event_participants ep_seed
            JOIN event_participants ep_other
                ON ep_other.event_id = ep_seed.event_id
            JOIN events e
                ON e.event_id = ep_seed.event_id
            WHERE ep_seed.person_id IN (%s)
            GROUP BY ep_other.person_id
            """
            % ",".join("?" for _ in participant_ids),
            tuple(participant_ids),
        ).fetchall()
        for row in event_participant_rows:
            if row["person_id"] in participant_ids:
                continue
            _merge_derived_candidate(
                derived_candidates,
                person_id=row["person_id"],
                activation_score=_apply_event_decay(row["latest_timestamp"]),
                reason="event participant linked to current participant",
                source="event",
            )

    if scene["group_id"]:
        group_member_rows = conn.execute(
            """
            SELECT person_id
            FROM group_members
            WHERE group_id = ? AND status = ?
            """,
            (scene["group_id"], "active"),
        ).fetchall()
        for row in group_member_rows:
            if row["person_id"] in participant_ids:
                continue
            _merge_derived_candidate(
                derived_candidates,
                person_id=row["person_id"],
                activation_score=GROUP_LATENT_WEIGHT,
                reason="active group member in current scene",
                source="group",
            )

    if participant_ids:
        memory_owner_rows = conn.execute(
            """
            SELECT DISTINCT mo_other.owner_id
            FROM memories m
            JOIN memory_owners mo_seed
                ON mo_seed.memory_id = m.memory_id
            JOIN memory_owners mo_other
                ON mo_other.memory_id = m.memory_id
            WHERE m.is_shared = 1
            AND mo_seed.owner_type = 'person'
            AND mo_other.owner_type = 'person'
            AND mo_seed.owner_id IN (%s)
            """
            % ",".join("?" for _ in participant_ids),
            tuple(participant_ids),
        ).fetchall()
        for row in memory_owner_rows:
            if row["owner_id"] in participant_ids:
                continue
            _merge_derived_candidate(
                derived_candidates,
                person_id=row["owner_id"],
                activation_score=MEMORY_LATENT_WEIGHT,
                reason="shared memory owner linked to active participant",
                source="memory",
            )

    max_derived_latent = DERIVED_LATENT_BUDGET_BY_BARRIER.get(
        scene["activation_barrier"],
        DERIVED_LATENT_BUDGET_BY_BARRIER[None],
    )
    selected_derived = sorted(
        derived_candidates.values(),
        key=lambda item: (item["activation_score"], item["person_id"]),
        reverse=True,
    )[:max_derived_latent]
    for item in selected_derived:
        _merge_activation_candidate(
            activation_map,
            person_id=item["person_id"],
            activation_score=item["activation_score"],
            activation_state="latent",
            reason=item["activation_reason_summary"],
        )

    activation_list = sorted(
        activation_map.values(),
        key=lambda item: (
            STATE_PRIORITY[item["activation_state"]],
            item["activation_score"],
            item["person_id"],
        ),
        reverse=True,
    )
    selected_event_candidates = [item for item in selected_derived if item.get("source") == "event"]
    blocked_event_candidates = [
        item for item in derived_candidates.values() if item.get("source") == "event"
    ]
    source_counts = {}
    for source_name in ("relation", "event", "group", "memory"):
        selected_for_source = [item for item in selected_derived if item.get("source") == source_name]
        derived_for_source = [
            item for item in derived_candidates.values() if item.get("source") == source_name
        ]
        source_counts[source_name] = {
            "used": len(selected_for_source),
            "blocked": max(0, len(derived_for_source) - len(selected_for_source)),
        }
    budget = {
        "activation_budget": {
            "max_derived_latent": max_derived_latent,
            "used_derived_latent": len(selected_derived),
            "blocked_derived_latent": max(0, len(derived_candidates) - len(selected_derived)),
            "event_weight": EVENT_LATENT_WEIGHT,
            "used_event_latent": len(selected_event_candidates),
            "blocked_event_latent": max(0, len(blocked_event_candidates) - len(selected_event_candidates)),
        },
        "propagation_depth": 2 if selected_derived else 1,
        "activation_barrier": scene["activation_barrier"],
        "source_weights": {
            "relation": RELATION_LATENT_WEIGHT,
            "event": EVENT_LATENT_WEIGHT,
            "group": GROUP_LATENT_WEIGHT,
            "memory": MEMORY_LATENT_WEIGHT,
        },
        "source_counts": source_counts,
        "event_decay_days": EVENT_DECAY_DAYS,
    }
    return activation_list, budget


def _fetch_open_local_branches(
    conn: sqlite3.Connection,
    *,
    scene_id: str,
    group_id: str | None,
    activated_person_ids: list[str],
    relation_ids: list[str],
) -> list[dict]:
    scope_values = {
        "scene": [scene_id],
        "group": [group_id] if group_id else [],
        "person": activated_person_ids,
        "relation": relation_ids,
    }
    clauses = []
    params: list[str] = []
    for scope_type, scope_ids in scope_values.items():
        if not scope_ids:
            continue
        placeholders = ",".join("?" for _ in scope_ids)
        clauses.append(f"(scope_type = ? AND scope_id IN ({placeholders}))")
        params.append(scope_type)
        params.extend(scope_ids)
    if not clauses:
        return []

    rows = conn.execute(
        f"""
        SELECT branch_id, scope_type, scope_id, reason
        FROM local_branches
        WHERE status = 'open'
        AND ({' OR '.join(clauses)})
        ORDER BY branch_id
        """,
        tuple(params),
    ).fetchall()
    return [
        {
            "branch_id": row["branch_id"],
            "scope_type": row["scope_type"],
            "scope_id": row["scope_id"],
            "reason": row["reason"],
        }
        for row in rows
    ]


def _count_open_local_branch_candidates(
    conn: sqlite3.Connection,
    branch_ids: list[str],
) -> int:
    if not branch_ids:
        return 0
    placeholders = ",".join("?" for _ in branch_ids)
    row = conn.execute(
        f"""
        SELECT COUNT(*) AS candidate_count
        FROM branch_candidates
        WHERE branch_id IN ({placeholders})
        AND status = 'open'
        """,
        tuple(branch_ids),
    ).fetchone()
    return row["candidate_count"] or 0


def _build_active_relations(
    conn: sqlite3.Connection,
    seed_person_ids: list[str],
    person_names: dict[str, str],
) -> list[dict]:
    if not seed_person_ids:
        return []

    relation_rows = conn.execute(
        """
        SELECT DISTINCT
            r.relation_id,
            r.core_type,
            r.custom_label,
            r.summary,
            r.status,
            r.strength
        FROM relations r
        JOIN event_targets et
            ON et.target_type = 'relation'
            AND et.target_id = r.relation_id
        JOIN event_participants ep
            ON ep.event_id = et.event_id
        WHERE ep.person_id IN (%s)
        AND r.status = 'active'
        """
        % ",".join("?" for _ in seed_person_ids),
        tuple(seed_person_ids),
    ).fetchall()
    relation_ids = [row["relation_id"] for row in relation_rows]
    if not relation_ids:
        return []

    relation_participant_rows = conn.execute(
        """
        SELECT DISTINCT
            et.target_id AS relation_id,
            ep.person_id
        FROM event_targets et
        JOIN event_participants ep
            ON ep.event_id = et.event_id
        WHERE et.target_type = 'relation'
        AND et.target_id IN (%s)
        """
        % ",".join("?" for _ in relation_ids),
        tuple(relation_ids),
    ).fetchall()

    missing_person_ids = [
        row["person_id"]
        for row in relation_participant_rows
        if row["person_id"] not in person_names
    ]
    if missing_person_ids:
        person_names.update(_fetch_person_names(conn, missing_person_ids))

    relation_participants: dict[str, list[dict]] = {}
    for row in relation_participant_rows:
        relation_participants.setdefault(row["relation_id"], []).append(
            {
                "person_id": row["person_id"],
                "display_name": person_names.get(row["person_id"], row["person_id"]),
            }
        )

    return [
        {
            "relation_id": row["relation_id"],
            "participants": relation_participants.get(row["relation_id"], []),
            "core_type": row["core_type"],
            "custom_label": row["custom_label"],
            "status": row["status"],
            "strength": row["strength"],
            "short_summary": row["summary"],
        }
        for row in relation_rows
    ]


def _refresh_scene_active_relations(
    conn: sqlite3.Connection,
    *,
    scene_id: str,
    active_relations: list[dict],
) -> None:
    conn.execute(
        "DELETE FROM scene_active_relations WHERE scene_id = ?",
        (scene_id,),
    )
    for relation in active_relations:
        conn.execute(
            """
            INSERT INTO scene_active_relations(scene_id, relation_id, activation_score, reason_json, created_at)
            VALUES(?, ?, ?, ?, ?)
            """,
            (
                scene_id,
                relation["relation_id"],
                relation.get("strength"),
                json.dumps({"source": "runtime_retrieval"}, ensure_ascii=False),
                datetime.now(UTC).isoformat(),
            ),
        )


def _build_relevant_memories(conn: sqlite3.Connection, activated_person_ids: list[str]) -> list[dict]:
    if not activated_person_ids:
        return []

    memory_rows = conn.execute(
        """
        SELECT DISTINCT m.memory_id, m.summary, m.memory_type, m.relevance_score, m.confidence
        FROM memories m
        JOIN memory_owners mo ON mo.memory_id = m.memory_id
        WHERE mo.owner_id IN (%s)
        AND m.is_shared = 1
        AND m.status = 'active'
        ORDER BY m.relevance_score DESC, m.created_at DESC
        """
        % ",".join("?" for _ in activated_person_ids),
        tuple(activated_person_ids),
    ).fetchall()
    return [
        {
            "memory_id": row["memory_id"],
            "memory_type": row["memory_type"],
            "summary": row["summary"],
            "relevance_score": row["relevance_score"],
            "confidence": row["confidence"],
        }
        for row in memory_rows
    ]


def _build_current_states(
    conn: sqlite3.Connection,
    *,
    scene_id: str,
    group_id: str | None,
    activated_person_ids: list[str],
    relation_ids: list[str],
) -> list[dict]:
    scope_values: dict[str, list[str]] = {
        "scene": [scene_id],
        "person": activated_person_ids,
        "relation": relation_ids,
    }
    if group_id:
        scope_values["group"] = [group_id]

    clauses = []
    params: list[str] = []
    for scope_type, scope_ids in scope_values.items():
        if not scope_ids:
            continue
        clauses.append(
            "(scope_type = ? AND scope_id IN (%s))" % ",".join("?" for _ in scope_ids)
        )
        params.append(scope_type)
        params.extend(scope_ids)

    if not clauses:
        return []

    state_rows = conn.execute(
        """
        SELECT
            state_id,
            scope_type,
            scope_id,
            state_type,
            value_json,
            confidence,
            is_inferred,
            updated_at
        FROM states
        WHERE %s
        ORDER BY confidence DESC, updated_at DESC
        """
        % " OR ".join(clauses),
        tuple(params),
    ).fetchall()
    return [
        {
            "state_id": row["state_id"],
            "scope_type": row["scope_type"],
            "scope_id": row["scope_id"],
            "state_type": row["state_type"],
            "value": json.loads(row["value_json"]),
            "confidence": row["confidence"],
            "is_inferred": bool(row["is_inferred"]),
        }
        for row in state_rows
    ]


def _build_open_branch_summary(
    conn: sqlite3.Connection,
    *,
    scene_id: str,
    activated_person_ids: list[str],
    relation_ids: list[str],
) -> dict:
    scope_values: dict[str, list[str]] = {
        "scene": [scene_id],
        "person": activated_person_ids,
        "relation": relation_ids,
    }
    clauses = []
    params: list[str] = []
    for scope_type, scope_ids in scope_values.items():
        if not scope_ids:
            continue
        clauses.append(
            "(scope_type = ? AND scope_id IN (%s))" % ",".join("?" for _ in scope_ids)
        )
        params.append(scope_type)
        params.extend(scope_ids)

    if not clauses:
        return {
            "open_local_branch_count": 0,
            "open_local_branch_ids": [],
            "open_local_branch_candidate_count": 0,
        }

    rows = conn.execute(
        """
        SELECT branch_id
        FROM local_branches
        WHERE status = 'open'
        AND (%s)
        ORDER BY created_at DESC, branch_id
        """
        % " OR ".join(clauses),
        tuple(params),
    ).fetchall()
    branch_ids = [row["branch_id"] for row in rows]
    candidate_count = 0
    if branch_ids:
        candidate_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM branch_candidates
            WHERE branch_id IN (%s)
            """
            % ",".join("?" for _ in branch_ids),
            tuple(branch_ids),
        ).fetchone()[0]
    return {
        "open_local_branch_count": len(branch_ids),
        "open_local_branch_ids": branch_ids,
        "open_local_branch_candidate_count": candidate_count,
    }


def _build_response_policy(
    scene: sqlite3.Row,
    participants_rows: list[sqlite3.Row],
    activation_map: list[dict],
) -> dict:
    explicit_ids = [
        item["person_id"]
        for item in activation_map
        if item["activation_state"] == "explicit"
    ]
    latent_ids = [
        item["person_id"]
        for item in activation_map
        if item["activation_state"] == "latent"
    ]
    primary = next((row["person_id"] for row in participants_rows if row["is_speaking"]), None)
    if not primary and explicit_ids:
        primary = explicit_ids[0]

    group_like_scene = scene["scene_type"] in {
        "group_chat",
        "meeting",
        "work_discussion",
        "casual_social",
    } or scene["channel_scope"] in {
        "group_channel",
        "work_channel",
        "family_channel",
    }

    if len(explicit_ids) > 1:
        mode = "multi_parallel"
        reason = "multiple explicit speakers reached the response threshold"
    elif latent_ids and group_like_scene:
        mode = "primary_plus_support"
        reason = "group context activated latent supporting participants"
    else:
        mode = "single_primary"
        reason = "single explicit speaker remained after bounded activation"

    silenced_participants = [
        item["person_id"]
        for item in activation_map
        if item["person_id"] != primary and item["activation_state"] != "explicit"
    ]

    return {
        "mode": mode,
        "primary_speaker": primary,
        "supporting_speakers": [item for item in explicit_ids if item != primary],
        "silenced_participants": silenced_participants,
        "reason": reason,
    }


def build_runtime_retrieval_package_from_db(
    db_path: Path,
    scene_id: str,
    input_hash: str | None = None,
    cache_ttl_seconds: int | None = None,
) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    if input_hash:
        now_iso = datetime.now(UTC).isoformat()
        cached_row = conn.execute(
            """
            SELECT payload_json
            FROM retrieval_cache
            WHERE scene_id = ? AND cache_type = ? AND input_hash = ?
              AND (expires_at IS NULL OR expires_at >= ?)
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (scene_id, "runtime_retrieval", input_hash, now_iso),
        ).fetchone()
        if cached_row is not None:
            conn.close()
            return json.loads(cached_row["payload_json"])

    scene = conn.execute("SELECT * FROM scenes WHERE scene_id = ?", (scene_id,)).fetchone()
    if scene is None:
        conn.close()
        raise ValueError(f"Scene not found: {scene_id}")

    group = None
    if scene["group_id"]:
        group = conn.execute(
            "SELECT group_id, group_type, name, summary FROM groups WHERE group_id = ?",
            (scene["group_id"],),
        ).fetchone()
    participants_rows = conn.execute(
        "SELECT * FROM scene_participants WHERE scene_id = ?",
        (scene_id,),
    ).fetchall()
    scene_person_ids = [row["person_id"] for row in participants_rows]
    group_member_ids = []
    if scene["group_id"]:
        group_member_ids = [
            row["person_id"]
            for row in conn.execute(
                "SELECT person_id FROM group_members WHERE group_id = ? AND status = ?",
                (scene["group_id"], "active"),
            ).fetchall()
        ]
    person_names = _fetch_person_names(
        conn,
        list(dict.fromkeys(scene_person_ids + group_member_ids)),
    )

    active_relations = _build_active_relations(conn, scene_person_ids, person_names)
    _refresh_scene_active_relations(conn, scene_id=scene_id, active_relations=active_relations)
    conn.commit()
    activation_map, safety_and_budget = _build_activation_map(conn, scene, participants_rows)
    activated_person_ids = [item["person_id"] for item in activation_map]
    relevant_memories = _build_relevant_memories(conn, activated_person_ids)
    relation_ids = [item["relation_id"] for item in active_relations]
    open_branches = _fetch_open_local_branches(
        conn,
        scene_id=scene_id,
        group_id=scene["group_id"],
        activated_person_ids=activated_person_ids,
        relation_ids=relation_ids,
    )
    open_branch_ids = [item["branch_id"] for item in open_branches]
    safety_and_budget["open_local_branch_count"] = len(open_branches)
    safety_and_budget["open_local_branch_ids"] = open_branch_ids
    safety_and_budget["open_local_branch_candidate_count"] = _count_open_local_branch_candidates(
        conn,
        open_branch_ids,
    )
    current_states = _build_current_states(
        conn,
        scene_id=scene_id,
        group_id=scene["group_id"],
        activated_person_ids=activated_person_ids,
        relation_ids=relation_ids,
    )
    branch_summary = _build_open_branch_summary(
        conn,
        scene_id=scene_id,
        activated_person_ids=activated_person_ids,
        relation_ids=[item["relation_id"] for item in active_relations],
    )

    scene_summary = {
        "scene_id": scene["scene_id"],
        "scene_type": scene["scene_type"],
        "group_id": scene["group_id"],
        "summary": scene["scene_summary"],
    }
    environment_constraints = {
        "location_scope": scene["location_scope"],
        "channel_scope": scene["channel_scope"],
        "visibility_scope": scene["visibility_scope"],
        "time_scope": scene["time_scope"],
        "role_scope": scene["role_scope"],
        "access_scope": scene["access_scope"],
        "privacy_scope": scene["privacy_scope"],
        "activation_barrier": scene["activation_barrier"],
    }
    participants = [
        {
            "person_id": row["person_id"],
            "display_name": person_names.get(row["person_id"], row["person_id"]),
            "scene_role": "participant",
            "speak_eligibility": "allowed" if row["is_speaking"] else "discouraged",
        }
        for row in participants_rows
    ]
    response_policy = _build_response_policy(scene, participants_rows, activation_map)
    conn.close()

    package = {
        "scene_summary": scene_summary,
        "group_context": {
            "group_id": group["group_id"],
            "group_type": group["group_type"],
            "name": group["name"],
            "summary": group["summary"],
        } if group else None,
        "environment_constraints": environment_constraints,
        "participants": participants,
        "active_relations": active_relations,
        "relevant_memories": relevant_memories,
        "current_states": current_states,
        "activation_map": activation_map,
        "response_policy": response_policy,
        "safety_and_budget": {**safety_and_budget, **branch_summary},
    }
    if input_hash:
        cache_id = f"cache_{uuid.uuid4().hex}"
        created_at_dt = datetime.now(UTC)
        created_at = created_at_dt.isoformat()
        expires_at = None
        if cache_ttl_seconds is not None:
            expires_at = (created_at_dt + timedelta(seconds=cache_ttl_seconds)).isoformat()
        conn = sqlite3.connect(db_path)
        conn.execute(
            """
            INSERT INTO retrieval_cache(
                cache_id, scene_id, cache_type, input_hash, payload_json, expires_at, created_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cache_id,
                scene_id,
                "runtime_retrieval",
                input_hash,
                json.dumps(package, ensure_ascii=False),
                expires_at,
                created_at,
            ),
        )
        conn.commit()
        conn.close()
    return package
