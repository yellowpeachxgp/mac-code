from we_together.services.snapshot_service import build_snapshot, build_snapshot_entities


def test_build_snapshot_creates_structured_snapshot():
    snapshot = build_snapshot(
        snapshot_id="snap_1",
        based_on_snapshot_id=None,
        trigger_event_id="evt_1",
        summary="after import",
        graph_hash="hash_123",
    )

    assert snapshot["snapshot_id"] == "snap_1"
    assert snapshot["trigger_event_id"] == "evt_1"
    assert snapshot["graph_hash"] == "hash_123"


def test_build_snapshot_entities_creates_distinct_rows():
    rows = build_snapshot_entities(
        snapshot_id="snap_1",
        entities=[
            ("person", "person_a"),
            ("person", "person_a"),
            ("memory", "memory_1"),
        ],
    )

    assert len(rows) == 2
    assert rows[0]["snapshot_id"] == "snap_1"
    assert {row["entity_type"] for row in rows} == {"person", "memory"}
