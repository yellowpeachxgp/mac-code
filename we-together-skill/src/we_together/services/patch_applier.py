from datetime import UTC, datetime
import json
from pathlib import Path

from we_together.db.connection import connect


def _ensure_patch_record(conn, patch: dict) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO patches(
            patch_id, source_event_id, target_type, target_id,
            operation, payload_json, confidence, reason, status,
            created_at, applied_at
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            patch["patch_id"],
            patch["source_event_id"],
            patch["target_type"],
            patch["target_id"],
            patch["operation"],
            json.dumps(patch["payload_json"], ensure_ascii=False),
            patch["confidence"],
            patch["reason"],
            patch.get("status", "pending"),
            patch["created_at"],
            patch.get("applied_at"),
        ),
    )


def apply_patch_record(db_path: Path, patch: dict) -> None:
    conn = connect(db_path)
    _ensure_patch_record(conn, patch)
    payload = patch["payload_json"]
    now = datetime.now(UTC).isoformat()

    if patch["operation"] == "create_memory":
        conn.execute(
            """
            INSERT OR REPLACE INTO memories(
                memory_id, memory_type, summary, emotional_tone, relevance_score,
                confidence, is_shared, status, metadata_json, created_at, updated_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["memory_id"],
                payload["memory_type"],
                payload["summary"],
                payload.get("emotional_tone"),
                payload.get("relevance_score"),
                payload.get("confidence"),
                payload.get("is_shared", 0),
                payload.get("status", "active"),
                json.dumps(payload.get("metadata_json", {}), ensure_ascii=False),
                now,
                now,
            ),
        )
    elif patch["operation"] == "update_state":
        conn.execute(
            """
            INSERT OR REPLACE INTO states(
                state_id, scope_type, scope_id, state_type, value_json,
                confidence, is_inferred, decay_policy, source_event_refs_json,
                created_at, updated_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["state_id"],
                payload["scope_type"],
                payload["scope_id"],
                payload["state_type"],
                json.dumps(payload["value_json"], ensure_ascii=False),
                payload.get("confidence"),
                payload.get("is_inferred", 1),
                payload.get("decay_policy"),
                json.dumps(payload.get("source_event_refs_json", []), ensure_ascii=False),
                now,
                now,
            ),
        )
    elif patch["operation"] == "link_entities":
        conn.execute(
            """
            DELETE FROM entity_links
            WHERE from_type = ?
            AND from_id = ?
            AND relation_type = ?
            AND to_type = ?
            AND to_id = ?
            """,
            (
                payload["from_type"],
                payload["from_id"],
                payload["relation_type"],
                payload["to_type"],
                payload["to_id"],
            ),
        )
        conn.execute(
            """
            INSERT INTO entity_links(
                from_type, from_id, relation_type, to_type, to_id, weight, metadata_json
            ) VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["from_type"],
                payload["from_id"],
                payload["relation_type"],
                payload["to_type"],
                payload["to_id"],
                payload.get("weight"),
                json.dumps(payload.get("metadata_json", {}), ensure_ascii=False),
            ),
        )
    elif patch["operation"] == "create_local_branch":
        conn.execute(
            """
            INSERT OR REPLACE INTO local_branches(
                branch_id, scope_type, scope_id, status, reason,
                created_from_event_id, created_at, resolved_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["branch_id"],
                payload["scope_type"],
                payload["scope_id"],
                payload.get("status", "open"),
                payload.get("reason"),
                payload.get("created_from_event_id"),
                payload.get("created_at", now),
                payload.get("resolved_at"),
            ),
        )
        branch_candidates = payload.get("branch_candidates") or []
        if branch_candidates:
            conn.executemany(
                """
                INSERT OR REPLACE INTO branch_candidates(
                    candidate_id, branch_id, label, payload_json,
                    confidence, status, created_at
                ) VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        candidate["candidate_id"],
                        payload["branch_id"],
                        candidate.get("label"),
                        json.dumps(candidate["payload_json"], ensure_ascii=False),
                        candidate.get("confidence"),
                        candidate.get("status", "open"),
                        candidate.get("created_at", now),
                    )
                    for candidate in branch_candidates
                ],
            )
    elif patch["operation"] == "resolve_local_branch":
        conn.execute(
            """
            UPDATE local_branches
            SET status = ?, reason = ?, resolved_at = ?
            WHERE branch_id = ?
            """,
            (
                payload.get("status", "resolved"),
                payload.get("reason"),
                payload.get("resolved_at", now),
                payload["branch_id"],
            ),
        )
    elif patch["operation"] == "unlink_entities":
        conn.execute(
            """
            DELETE FROM entity_links
            WHERE from_type = ?
            AND from_id = ?
            AND relation_type = ?
            AND to_type = ?
            AND to_id = ?
            """,
            (
                payload["from_type"],
                payload["from_id"],
                payload["relation_type"],
                payload["to_type"],
                payload["to_id"],
            ),
        )
    elif patch["operation"] == "mark_inactive":
        table_by_target = {
            "memory": "memories",
            "relation": "relations",
            "person": "persons",
            "group": "groups",
        }
        table_name = table_by_target.get(patch["target_type"])
        if table_name is None or patch["target_id"] is None:
            conn.execute(
                "UPDATE patches SET status = ?, applied_at = ? WHERE patch_id = ?",
                ("failed", now, patch["patch_id"]),
            )
            conn.commit()
            conn.close()
            raise ValueError(f"Unsupported mark_inactive target: {patch['target_type']}")

        id_column = f"{patch['target_type']}_id"
        conn.execute(
            f"UPDATE {table_name} SET status = ?, updated_at = ? WHERE {id_column} = ?",
            ("inactive", now, patch["target_id"]),
        )
    else:
        conn.execute(
            "UPDATE patches SET status = ?, applied_at = ? WHERE patch_id = ?",
            ("failed", now, patch["patch_id"]),
        )
        conn.commit()
        conn.close()
        raise ValueError(f"Unsupported patch operation: {patch['operation']}")

    conn.execute(
        "UPDATE patches SET status = ?, applied_at = ? WHERE patch_id = ?",
        ("applied", now, patch["patch_id"]),
    )
    conn.commit()
    conn.close()
