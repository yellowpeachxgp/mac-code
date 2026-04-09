from datetime import UTC, datetime
import hashlib


def build_snapshot(
    snapshot_id: str,
    based_on_snapshot_id: str | None,
    trigger_event_id: str | None,
    summary: str,
    graph_hash: str,
) -> dict:
    return {
        "snapshot_id": snapshot_id,
        "based_on_snapshot_id": based_on_snapshot_id,
        "trigger_event_id": trigger_event_id,
        "summary": summary,
        "graph_hash": graph_hash,
        "created_at": datetime.now(UTC).isoformat(),
    }


def build_snapshot_entities(
    snapshot_id: str,
    entities: list[tuple[str, str]],
) -> list[dict]:
    rows = []
    seen = set()
    for entity_type, entity_id in entities:
        key = (entity_type, entity_id)
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "snapshot_id": snapshot_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "entity_hash": hashlib.sha256(f"{entity_type}:{entity_id}".encode()).hexdigest(),
            }
        )
    return rows
