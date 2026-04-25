"""Read-only query layer for the host-local WebUI."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from urllib.parse import parse_qs

from we_together import __version__
from we_together.db.connection import connect
from we_together.runtime.sqlite_retrieval import build_runtime_retrieval_package_from_db
from we_together.services.snapshot_service import list_snapshots
from we_together.services.tenant_router import infer_tenant_id_from_root
from we_together.services.world_service import active_world_for_scene


def _db_path(root: Path) -> Path:
    return root / "db" / "main.sqlite3"


def _loads(value: str | None, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default


def _rows(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def health(root: Path, auth_mode: str) -> dict:
    return {
        "version": __version__,
        "tenant_id": infer_tenant_id_from_root(root),
        "root": str(root),
        "auth_mode": auth_mode,
    }


def bootstrap(root: Path, auth_mode: str) -> dict:
    return {
        "version": __version__,
        "tenant_id": infer_tenant_id_from_root(root),
        "auth_mode": auth_mode,
        "capabilities": {
            "graph": True,
            "chat": True,
            "world": True,
            "review": True,
            "editor": True,
            "metrics": True,
        },
        "feature_flags": {
            "patch_first_editor": True,
            "operator_gated_branch_resolve": True,
            "world_service_audit_events": True,
            "static_spa_public_api_token_required": True,
        },
    }


def summary(root: Path) -> dict:
    db = _db_path(root)
    conn = connect(db)
    try:
        row = conn.execute(
            """
            SELECT
              (SELECT COUNT(*) FROM persons WHERE status='active'),
              (SELECT COUNT(*) FROM relations WHERE status='active'),
              (SELECT COUNT(*) FROM groups WHERE status='active'),
              (SELECT COUNT(*) FROM scenes WHERE status='active'),
              (SELECT COUNT(*) FROM events),
              (SELECT COUNT(*) FROM memories WHERE status='active'),
              (SELECT COUNT(*) FROM patches),
              (SELECT COUNT(*) FROM snapshots),
              (SELECT COUNT(*) FROM local_branches WHERE status='open'),
              (SELECT COUNT(*) FROM objects WHERE status='active'),
              (SELECT COUNT(*) FROM places WHERE status='active'),
              (SELECT COUNT(*) FROM projects WHERE status='active')
            """
        ).fetchone()
    finally:
        conn.close()
    return {
        "tenant_id": infer_tenant_id_from_root(root),
        "person_count": row[0],
        "relation_count": row[1],
        "group_count": row[2],
        "scene_count": row[3],
        "event_count": row[4],
        "memory_count": row[5],
        "patch_count": row[6],
        "snapshot_count": row[7],
        "branch_count": row[8],
        "world": {
            "object_count": row[9],
            "place_count": row[10],
            "project_count": row[11],
        },
    }


def scenes(root: Path, *, limit: int = 100) -> dict:
    conn = connect(_db_path(root))
    try:
        rows = _rows(
            conn,
            """
            SELECT s.scene_id, s.scene_type, s.scene_summary, s.group_id, s.status,
                   s.created_at, s.updated_at,
                   (SELECT COUNT(*) FROM scene_participants sp
                    WHERE sp.scene_id = s.scene_id) AS participant_count
            FROM scenes s
            ORDER BY s.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )
    finally:
        conn.close()
    return {"scenes": rows}


def graph(root: Path, *, scene_id: str | None = None, include: str | None = None) -> dict:
    conn = connect(_db_path(root))
    conn.row_factory = sqlite3.Row
    try:
        persons = _rows(
            conn,
            "SELECT person_id, primary_name, status, summary, persona_summary FROM persons WHERE status != 'merged' ORDER BY primary_name",
        )
        relations = _rows(
            conn,
            "SELECT relation_id, core_type, custom_label, summary, strength, status FROM relations ORDER BY relation_id",
        )
        groups = _rows(
            conn,
            "SELECT group_id, group_type, name, summary, status FROM groups ORDER BY name",
        )
        memories = _rows(
            conn,
            "SELECT memory_id, memory_type, summary, relevance_score, status FROM memories WHERE status='active' ORDER BY updated_at DESC LIMIT 200",
        )
        scene_participants: set[str] = set()
        if scene_id:
            scene_participants = {
                row[0]
                for row in conn.execute(
                    "SELECT person_id FROM scene_participants WHERE scene_id = ?",
                    (scene_id,),
                ).fetchall()
            }

        nodes: list[dict] = []
        for person in persons:
            nodes.append({
                "id": person["person_id"],
                "type": "person",
                "label": person["primary_name"],
                "status": person["status"],
                "active_in_scene": person["person_id"] in scene_participants,
                "data": dict(person),
            })
        for group in groups:
            nodes.append({
                "id": group["group_id"],
                "type": "group",
                "label": group["name"] or group["group_id"],
                "status": group["status"],
                "data": dict(group),
            })
        for memory in memories:
            nodes.append({
                "id": memory["memory_id"],
                "type": "memory",
                "label": memory["summary"][:80],
                "status": memory["status"],
                "data": dict(memory),
            })

        edges: list[dict] = []
        for relation in relations:
            participants = [
                row[0]
                for row in conn.execute(
                    """
                    SELECT DISTINCT ep.person_id
                    FROM event_targets et
                    JOIN event_participants ep ON ep.event_id = et.event_id
                    WHERE et.target_type = 'relation' AND et.target_id = ?
                    ORDER BY ep.person_id
                    LIMIT 2
                    """,
                    (relation["relation_id"],),
                ).fetchall()
            ]
            if len(participants) >= 2:
                edges.append({
                    "id": relation["relation_id"],
                    "type": "relation",
                    "source": participants[0],
                    "target": participants[1],
                    "label": relation["custom_label"] or relation["core_type"],
                    "data": dict(relation),
                })
        for row in conn.execute(
            """
            SELECT group_id, person_id, role_label
            FROM group_members
            WHERE status='active'
            """
        ).fetchall():
            edges.append({
                "id": f"group_member:{row['group_id']}:{row['person_id']}",
                "type": "group_member",
                "source": row["group_id"],
                "target": row["person_id"],
                "label": row["role_label"] or "member",
                "data": dict(row),
            })
        for row in conn.execute(
            """
            SELECT memory_id, owner_type, owner_id, role_label
            FROM memory_owners
            WHERE owner_type='person'
            """
        ).fetchall():
            edges.append({
                "id": f"memory_owner:{row['owner_id']}:{row['memory_id']}",
                "type": "memory_owner",
                "source": row["owner_id"],
                "target": row["memory_id"],
                "label": row["role_label"] or "remembers",
                "data": dict(row),
            })
        for row in conn.execute(
            """
            SELECT from_type, from_id, relation_type, to_type, to_id, weight, metadata_json
            FROM entity_links
            LIMIT 500
            """
        ).fetchall():
            edges.append({
                "id": f"entity_link:{row['from_type']}:{row['from_id']}:{row['relation_type']}:{row['to_type']}:{row['to_id']}",
                "type": "entity_link",
                "source": row["from_id"],
                "target": row["to_id"],
                "label": row["relation_type"],
                "data": {**dict(row), "metadata_json": _loads(row["metadata_json"], {})},
            })
    finally:
        conn.close()
    return {
        "scene_id": scene_id,
        "include": include,
        "nodes": nodes,
        "edges": edges,
    }


ENTITY_TABLES = {
    "person": ("persons", "person_id"),
    "relation": ("relations", "relation_id"),
    "memory": ("memories", "memory_id"),
    "group": ("groups", "group_id"),
}


def entity_detail(root: Path, entity_type: str, entity_id: str) -> dict:
    if entity_type not in ENTITY_TABLES:
        raise ValueError(f"unsupported entity type: {entity_type}")
    table, id_column = ENTITY_TABLES[entity_type]
    conn = connect(_db_path(root))
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            f"SELECT * FROM {table} WHERE {id_column} = ?",
            (entity_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"{entity_type} not found: {entity_id}")
        entity = dict(row)
        for key in ("metadata_json", "environment_json"):
            if key in entity:
                entity[key] = _loads(entity[key], {})
        entity["id"] = entity_id
        entity["type"] = entity_type
        outgoing = _rows(
            conn,
            "SELECT * FROM entity_links WHERE from_type = ? AND from_id = ? LIMIT 100",
            (entity_type, entity_id),
        )
        incoming = _rows(
            conn,
            "SELECT * FROM entity_links WHERE to_type = ? AND to_id = ? LIMIT 100",
            (entity_type, entity_id),
        )
        patches = _rows(
            conn,
            """
            SELECT patch_id, operation, status, confidence, reason, created_at, applied_at
            FROM patches
            WHERE target_type = ? AND target_id = ?
            ORDER BY created_at DESC LIMIT 50
            """,
            (entity_type, entity_id),
        )
    finally:
        conn.close()
    return {"entity": entity, "links": {"outgoing": outgoing, "incoming": incoming}, "patches": patches}


def events(root: Path, query: dict[str, list[str]]) -> dict:
    limit = int((query.get("limit") or ["50"])[0])
    entity_type = (query.get("entity_type") or [None])[0]
    entity_id = (query.get("entity_id") or [None])[0]
    conn = connect(_db_path(root))
    try:
        if entity_type == "person" and entity_id:
            rows = _rows(
                conn,
                """
                SELECT e.*
                FROM events e
                JOIN event_participants ep ON ep.event_id = e.event_id
                WHERE ep.person_id = ?
                ORDER BY e.created_at DESC LIMIT ?
                """,
                (entity_id, limit),
            )
        elif entity_type and entity_id:
            rows = _rows(
                conn,
                """
                SELECT e.*
                FROM events e
                JOIN event_targets et ON et.event_id = e.event_id
                WHERE et.target_type = ? AND et.target_id = ?
                ORDER BY e.created_at DESC LIMIT ?
                """,
                (entity_type, entity_id, limit),
            )
        else:
            rows = _rows(conn, "SELECT * FROM events ORDER BY created_at DESC LIMIT ?", (limit,))
    finally:
        conn.close()
    return {"events": rows}


def patches(root: Path, query: dict[str, list[str]]) -> dict:
    clauses: list[str] = []
    params: list[str] = []
    for key, column in [("status", "status"), ("operation", "operation"), ("target_type", "target_type"), ("target_id", "target_id")]:
        value = (query.get(key) or [None])[0]
        if value:
            clauses.append(f"{column} = ?")
            params.append(value)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    conn = connect(_db_path(root))
    try:
        rows = _rows(
            conn,
            f"""
            SELECT patch_id, source_event_id, target_type, target_id, operation,
                   payload_json, confidence, reason, status, created_at, applied_at
            FROM patches
            {where}
            ORDER BY created_at DESC
            LIMIT 100
            """,
            tuple(params),
        )
    finally:
        conn.close()
    for row in rows:
        row["payload_json"] = _loads(row.get("payload_json"), {})
    return {"patches": rows}


def snapshots(root: Path, query: dict[str, list[str]]) -> dict:
    limit = int((query.get("limit") or ["50"])[0])
    return {"snapshots": list_snapshots(_db_path(root), limit=limit)}


def retrieval_package(root: Path, query: dict[str, list[str]]) -> dict:
    scene_id = (query.get("scene_id") or [""])[0]
    if not scene_id:
        raise ValueError("scene_id is required")
    return build_runtime_retrieval_package_from_db(_db_path(root), scene_id=scene_id)


def world(root: Path, query: dict[str, list[str]]) -> dict:
    scene_id = (query.get("scene_id") or [""])[0]
    if scene_id:
        return active_world_for_scene(_db_path(root), scene_id)
    return {
        "objects": list_world_objects(root)["objects"],
        "places": list_world_places(root)["places"],
        "projects": list_world_projects(root)["projects"],
    }


def list_world_objects(root: Path) -> dict:
    conn = connect(_db_path(root))
    try:
        rows = _rows(
            conn,
            """
            SELECT object_id, kind, name, description, owner_type, owner_id,
                   location_place_id, status, effective_from, effective_until,
                   metadata_json, created_at, updated_at
            FROM objects
            ORDER BY updated_at DESC LIMIT 200
            """,
        )
    finally:
        conn.close()
    return {"objects": rows}


def list_world_places(root: Path) -> dict:
    conn = connect(_db_path(root))
    try:
        rows = _rows(
            conn,
            """
            SELECT place_id, name, description, scope, parent_place_id, visibility,
                   status, effective_from, effective_until, metadata_json,
                   created_at, updated_at
            FROM places
            ORDER BY updated_at DESC LIMIT 200
            """,
        )
    finally:
        conn.close()
    return {"places": rows}


def list_world_projects(root: Path) -> dict:
    conn = connect(_db_path(root))
    try:
        rows = _rows(
            conn,
            """
            SELECT project_id, name, goal, description, status, priority,
                   started_at, due_at, ended_at, metadata_json, created_at, updated_at
            FROM projects
            ORDER BY updated_at DESC LIMIT 200
            """,
        )
    finally:
        conn.close()
    return {"projects": rows}


def branches(root: Path, query: dict[str, list[str]]) -> dict:
    status = (query.get("status") or ["open"])[0]
    conn = connect(_db_path(root))
    conn.row_factory = sqlite3.Row
    try:
        if status == "all":
            branch_rows = conn.execute(
                "SELECT * FROM local_branches ORDER BY created_at DESC LIMIT 100"
            ).fetchall()
        else:
            branch_rows = conn.execute(
                "SELECT * FROM local_branches WHERE status = ? ORDER BY created_at DESC LIMIT 100",
                (status,),
            ).fetchall()
        out = []
        for branch in branch_rows:
            candidates = _rows(
                conn,
                """
                SELECT candidate_id, label, payload_json, confidence, status, created_at
                FROM branch_candidates
                WHERE branch_id = ?
                ORDER BY confidence DESC
                """,
                (branch["branch_id"],),
            )
            for candidate in candidates:
                candidate["payload_json"] = _loads(candidate.get("payload_json"), {})
            out.append({**dict(branch), "candidates": candidates})
    finally:
        conn.close()
    return {"branches": out}


def parse_query(query_string: str) -> dict[str, list[str]]:
    return parse_qs(query_string, keep_blank_values=False)
