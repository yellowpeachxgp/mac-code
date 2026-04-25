"""Patch-first write layer for the host-local WebUI."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from we_together.db.connection import connect
from we_together.llm import get_llm_client
from we_together.services.chat_service import run_turn
from we_together.services.patch_applier import apply_patch_record
from we_together.services.patch_service import build_patch
from we_together.services.scene_service import (
    add_scene_participant,
    archive_scene,
    close_scene,
    create_scene,
)
from we_together.services.world_service import (
    register_object,
    register_place,
    register_project,
    set_project_status,
    transfer_object,
)
from we_together.webui import queries


def _db_path(root: Path) -> Path:
    return root / "db" / "main.sqlite3"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _new_audit_event_id() -> str:
    return f"webui_event_{uuid.uuid4().hex}"


def record_webui_audit_event(
    db_path: Path,
    *,
    summary: str,
    scene_id: str | None = None,
    metadata: dict | None = None,
) -> str:
    event_id = _new_audit_event_id()
    now = _now()
    conn = connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO events(
                event_id, event_type, source_type, scene_id, timestamp, summary,
                visibility_level, confidence, is_structured,
                raw_evidence_refs_json, metadata_json, created_at
            ) VALUES(?, 'webui_audit', 'webui', ?, ?, ?, 'operator', 1.0, 1,
                     '[]', ?, ?)
            """,
            (
                event_id,
                scene_id,
                now,
                summary,
                json.dumps(metadata or {}, ensure_ascii=False),
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return event_id


FIELD_MAP = {
    "person": {
        "primary_name": "primary_name",
        "persona": "persona_summary",
        "persona_summary": "persona_summary",
        "status": "status",
        "metadata_json": "metadata_json",
    },
    "relation": {
        "core_type": "core_type",
        "summary": "summary",
        "strength": "strength",
        "status": "status",
    },
    "memory": {
        "summary": "summary",
        "relevance_score": "relevance_score",
        "status": "status",
    },
    "group": {
        "name": "name",
        "summary": "summary",
        "status": "status",
        "metadata_json": "metadata_json",
    },
}


def _normalize_fields(entity_type: str, fields: dict) -> dict:
    field_map = FIELD_MAP.get(entity_type)
    if field_map is None:
        raise ValueError(f"unsupported entity type: {entity_type}")
    normalized = {}
    for key, value in fields.items():
        if key not in field_map:
            raise ValueError(f"field not editable for {entity_type}: {key}")
        column = field_map[key]
        if column == "metadata_json" and isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        normalized[column] = value
    if not normalized:
        raise ValueError("at least one editable field is required")
    return normalized


def _apply_patch(root: Path, patch: dict) -> dict:
    db_path = _db_path(root)
    apply_patch_record(db_path=db_path, patch=patch)
    return {
        "event_id": patch["source_event_id"],
        "patch_id": patch["patch_id"],
        "snapshot_id": None,
        "summary": queries.summary(root),
    }


def update_entity(root: Path, entity_type: str, entity_id: str, fields: dict) -> dict:
    db_path = _db_path(root)
    normalized = _normalize_fields(entity_type, fields)
    event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI update {entity_type} {entity_id}",
        metadata={"entity_type": entity_type, "entity_id": entity_id, "fields": sorted(normalized)},
    )
    patch = build_patch(
        source_event_id=event_id,
        target_type=entity_type,
        target_id=entity_id,
        operation="update_entity",
        payload=normalized,
        confidence=1.0,
        reason="webui patch-first entity update",
    )
    return _apply_patch(root, patch)


def archive_entity(root: Path, entity_type: str, entity_id: str, *, reactivate: bool = False) -> dict:
    db_path = _db_path(root)
    event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI {'reactivate' if reactivate else 'archive'} {entity_type} {entity_id}",
        metadata={"entity_type": entity_type, "entity_id": entity_id, "reactivate": reactivate},
    )
    if reactivate:
        patch = build_patch(
            source_event_id=event_id,
            target_type=entity_type,
            target_id=entity_id,
            operation="update_entity",
            payload={"status": "active"},
            confidence=1.0,
            reason="webui reactivate entity",
        )
    else:
        patch = build_patch(
            source_event_id=event_id,
            target_type=entity_type,
            target_id=entity_id,
            operation="mark_inactive",
            payload={},
            confidence=1.0,
            reason="webui archive entity",
        )
    return _apply_patch(root, patch)


def link_entities(root: Path, payload: dict, *, unlink: bool = False) -> dict:
    required = ["from_type", "from_id", "relation_type", "to_type", "to_id"]
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError(f"missing link fields: {', '.join(missing)}")
    db_path = _db_path(root)
    event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI {'unlink' if unlink else 'link'} entities",
        metadata={key: payload.get(key) for key in required},
    )
    patch = build_patch(
        source_event_id=event_id,
        target_type="entity_link",
        target_id=None,
        operation="unlink_entities" if unlink else "link_entities",
        payload={
            "from_type": payload["from_type"],
            "from_id": payload["from_id"],
            "relation_type": payload["relation_type"],
            "to_type": payload["to_type"],
            "to_id": payload["to_id"],
            "weight": payload.get("weight"),
            "metadata_json": payload.get("metadata_json", {}),
        },
        confidence=1.0,
        reason="webui entity link update",
    )
    return _apply_patch(root, patch)


def create_memory(root: Path, payload: dict) -> dict:
    summary = payload.get("summary")
    if not summary:
        raise ValueError("summary is required")
    db_path = _db_path(root)
    memory_id = payload.get("memory_id") or f"memory_{uuid.uuid4().hex}"
    event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI create memory {memory_id}",
        metadata={"memory_id": memory_id},
    )
    patch = build_patch(
        source_event_id=event_id,
        target_type="memory",
        target_id=memory_id,
        operation="create_memory",
        payload={
            "memory_id": memory_id,
            "memory_type": payload.get("memory_type", "shared_memory"),
            "summary": summary,
            "relevance_score": payload.get("relevance_score", 0.7),
            "confidence": payload.get("confidence", 1.0),
            "is_shared": 1 if payload.get("is_shared", True) else 0,
            "status": payload.get("status", "active"),
            "metadata_json": payload.get("metadata_json", {"source": "webui"}),
        },
        confidence=1.0,
        reason="webui create memory",
    )
    result = _apply_patch(root, patch)
    owner_person_ids = payload.get("owner_person_ids") or []
    if owner_person_ids:
        conn = connect(db_path)
        try:
            for person_id in owner_person_ids:
                conn.execute(
                    "INSERT INTO memory_owners(memory_id, owner_type, owner_id, role_label) VALUES(?, 'person', ?, NULL)",
                    (memory_id, person_id),
                )
            conn.commit()
        finally:
            conn.close()
    result["memory_id"] = memory_id
    return result


def resolve_branch(root: Path, branch_id: str, payload: dict) -> dict:
    candidate_id = payload.get("candidate_id")
    if not candidate_id:
        raise ValueError("candidate_id is required")
    db_path = _db_path(root)
    event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI resolve branch {branch_id}",
        metadata={"branch_id": branch_id, "candidate_id": candidate_id},
    )
    patch = build_patch(
        source_event_id=event_id,
        target_type="local_branch",
        target_id=branch_id,
        operation="resolve_local_branch",
        payload={
            "branch_id": branch_id,
            "selected_candidate_id": candidate_id,
            "status": payload.get("status", "resolved"),
            "reason": payload.get("reason", "operator resolution via WebUI"),
        },
        confidence=1.0,
        reason="webui operator-gated branch resolution",
    )
    return _apply_patch(root, patch)


def chat_turn(root: Path, payload: dict, *, llm_client=None) -> dict:
    scene_id = payload.get("scene_id")
    user_input = payload.get("input") or payload.get("user_input")
    if not scene_id or not user_input:
        raise ValueError("scene_id and input are required")
    result = run_turn(
        db_path=_db_path(root),
        scene_id=scene_id,
        user_input=user_input,
        llm_client=llm_client or get_llm_client(),
        adapter_name=payload.get("adapter_name", "openai_compat"),
        history=payload.get("history"),
        speaking_person_ids=payload.get("speaking_person_ids"),
    )
    response = result.get("response") or {}
    return {
        "text": response.get("text", ""),
        "speaker_person_id": response.get("speaker_person_id"),
        "event_id": result.get("event_id"),
        "snapshot_id": result.get("snapshot_id"),
        "applied_patch_count": result.get("applied_patch_count", 0),
        "retrieval_package": result.get("request", {}).get("retrieval_package"),
        "summary": queries.summary(root),
    }


def create_scene_action(root: Path, payload: dict) -> dict:
    db_path = _db_path(root)
    scene_id = create_scene(
        db_path,
        scene_type=payload.get("scene_type", "private_chat"),
        scene_summary=payload.get("scene_summary", ""),
        environment=payload.get("environment", {}),
        group_id=payload.get("group_id"),
    )
    audit_event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI create scene {scene_id}",
        scene_id=scene_id,
        metadata={"scene_id": scene_id},
    )
    return {"scene_id": scene_id, "audit_event_id": audit_event_id, "summary": queries.summary(root)}


def add_participant_action(root: Path, scene_id: str, payload: dict) -> dict:
    person_id = payload.get("person_id")
    if not person_id:
        raise ValueError("person_id is required")
    db_path = _db_path(root)
    add_scene_participant(
        db_path,
        scene_id=scene_id,
        person_id=person_id,
        activation_state=payload.get("activation_state", "explicit"),
        activation_score=float(payload.get("activation_score", 1.0)),
        is_speaking=bool(payload.get("is_speaking", False)),
    )
    audit_event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI add participant {person_id} to {scene_id}",
        scene_id=scene_id,
        metadata={"scene_id": scene_id, "person_id": person_id},
    )
    return {"scene_id": scene_id, "person_id": person_id, "audit_event_id": audit_event_id, "summary": queries.summary(root)}


def set_scene_status_action(root: Path, scene_id: str, status: str) -> dict:
    db_path = _db_path(root)
    if status == "closed":
        close_scene(db_path, scene_id)
    elif status == "archived":
        archive_scene(db_path, scene_id)
    else:
        raise ValueError("scene status must be closed or archived")
    audit_event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI set scene {scene_id} {status}",
        scene_id=scene_id,
        metadata={"scene_id": scene_id, "status": status},
    )
    return {"scene_id": scene_id, "status": status, "audit_event_id": audit_event_id, "summary": queries.summary(root)}


def create_world_object(root: Path, payload: dict) -> dict:
    db_path = _db_path(root)
    result = register_object(
        db_path,
        kind=payload.get("kind", "artifact"),
        name=payload.get("name"),
        description=payload.get("description"),
        owner_type=payload.get("owner_type"),
        owner_id=payload.get("owner_id"),
        location_place_id=payload.get("location_place_id"),
        effective_from=payload.get("effective_from"),
        effective_until=payload.get("effective_until"),
        metadata=payload.get("metadata") or payload.get("metadata_json"),
    )
    audit_event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI create world object {result['object_id']}",
        metadata={"object_id": result["object_id"]},
    )
    return {**result, "audit_event_id": audit_event_id, "summary": queries.summary(root)}


def create_world_place(root: Path, payload: dict) -> dict:
    db_path = _db_path(root)
    result = register_place(
        db_path,
        name=payload.get("name"),
        scope=payload.get("scope"),
        description=payload.get("description"),
        parent_place_id=payload.get("parent_place_id"),
        effective_from=payload.get("effective_from"),
        effective_until=payload.get("effective_until"),
        metadata=payload.get("metadata") or payload.get("metadata_json"),
    )
    audit_event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI create world place {result['place_id']}",
        metadata={"place_id": result["place_id"]},
    )
    return {**result, "audit_event_id": audit_event_id, "summary": queries.summary(root)}


def create_world_project(root: Path, payload: dict) -> dict:
    db_path = _db_path(root)
    result = register_project(
        db_path,
        name=payload.get("name"),
        goal=payload.get("goal"),
        description=payload.get("description"),
        priority=payload.get("priority"),
        started_at=payload.get("started_at"),
        due_at=payload.get("due_at"),
        participants=payload.get("participants"),
        metadata=payload.get("metadata") or payload.get("metadata_json"),
    )
    audit_event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI create world project {result['project_id']}",
        metadata={"project_id": result["project_id"]},
    )
    return {**result, "audit_event_id": audit_event_id, "summary": queries.summary(root)}


def update_world_project_status(root: Path, project_id: str, payload: dict) -> dict:
    db_path = _db_path(root)
    result = set_project_status(db_path, project_id, payload.get("status", "active"))
    audit_event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI set project {project_id} status {result['status']}",
        metadata={"project_id": project_id, "status": result["status"]},
    )
    return {**result, "audit_event_id": audit_event_id, "summary": queries.summary(root)}


def update_world_object_owner(root: Path, object_id: str, payload: dict) -> dict:
    owner_type = payload.get("owner_type")
    owner_id = payload.get("owner_id")
    if not owner_type or not owner_id:
        raise ValueError("owner_type and owner_id are required")
    db_path = _db_path(root)
    audit_event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI transfer object {object_id} to {owner_type}:{owner_id}",
        metadata={"object_id": object_id, "owner_type": owner_type, "owner_id": owner_id},
    )
    result = transfer_object(
        db_path,
        object_id=object_id,
        new_owner_type=owner_type,
        new_owner_id=owner_id,
        event_id=audit_event_id,
    )
    return {**result, "audit_event_id": audit_event_id, "summary": queries.summary(root)}


def update_world_object_status(root: Path, object_id: str, payload: dict) -> dict:
    status = payload.get("status")
    valid_statuses = {"active", "inactive", "lost", "destroyed"}
    if status not in valid_statuses:
        raise ValueError(f"object status must be in {sorted(valid_statuses)}")
    db_path = _db_path(root)
    audit_event_id = record_webui_audit_event(
        db_path,
        summary=f"WebUI set object {object_id} status {status}",
        metadata={"object_id": object_id, "status": status},
    )
    conn = connect(db_path)
    try:
        cursor = conn.execute(
            "UPDATE objects SET status=?, updated_at=datetime('now') WHERE object_id=?",
            (status, object_id),
        )
        if cursor.rowcount != 1:
            raise ValueError(f"object not found: {object_id}")
        conn.commit()
    finally:
        conn.close()
    return {
        "object_id": object_id,
        "status": status,
        "audit_event_id": audit_event_id,
        "summary": queries.summary(root),
    }
