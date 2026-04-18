"""Phase 41 — 遗忘 / 压缩 / 拆分 (FO slices)。"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))


def _seed_aged_memory(db: Path, mid: str, owner: str, relevance: float = 0.2,
                       days_ago: int = 60, status: str = "active") -> None:
    conn = sqlite3.connect(db)
    try:
        conn.execute(
            """INSERT INTO memories(memory_id, memory_type, summary, relevance_score,
               confidence, is_shared, status, metadata_json, created_at, updated_at)
               VALUES(?, 'shared_memory', ?, ?, 0.7, 1, ?, '{}',
               datetime('now', ?), datetime('now', ?))""",
            (mid, f"memory {mid}", relevance, status,
             f"-{days_ago} days", f"-{days_ago} days"),
        )
        conn.execute(
            "INSERT INTO memory_owners(memory_id, owner_type, owner_id, role_label) "
            "VALUES(?, 'person', ?, NULL)",
            (mid, owner),
        )
        conn.commit()
    finally:
        conn.close()


def test_forget_score_curve():
    from we_together.services.forgetting_service import _forget_score
    # 新近 + 高相关：接近 0
    assert _forget_score(days_idle=0, relevance=1.0) < 0.05
    # 久远 + 低相关：接近 1
    assert _forget_score(days_idle=365, relevance=0.0) > 0.8
    # 只有一个条件成立：中等
    mid = _forget_score(days_idle=60, relevance=0.3)
    assert 0.3 < mid < 0.8


def test_archive_stale_memories_dry_run(temp_project_with_migrations):
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.forgetting_service import (
        archive_stale_memories, ForgetParams,
    )

    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    _seed_aged_memory(db, "m_old_1", "p1", relevance=0.2, days_ago=90)
    _seed_aged_memory(db, "m_old_2", "p1", relevance=0.3, days_ago=60)
    _seed_aged_memory(db, "m_new_1", "p1", relevance=0.9, days_ago=3)

    r = archive_stale_memories(db, ForgetParams(dry_run=True))
    assert r["dry_run"] is True
    assert r["archived_count"] >= 1

    # 确认 dry_run 没真 archive
    conn = sqlite3.connect(db)
    cnt = conn.execute(
        "SELECT COUNT(*) FROM memories WHERE status='cold'"
    ).fetchone()[0]
    conn.close()
    assert cnt == 0


def test_archive_stale_memories_real(temp_project_with_migrations):
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.forgetting_service import (
        archive_stale_memories, ForgetParams,
    )
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    _seed_aged_memory(db, "m_stale", "p2", relevance=0.1, days_ago=120)

    r = archive_stale_memories(db, ForgetParams(dry_run=False))
    assert r["archived_count"] >= 1

    conn = sqlite3.connect(db)
    s = conn.execute(
        "SELECT status FROM memories WHERE memory_id='m_stale'"
    ).fetchone()[0]
    conn.close()
    assert s == "cold"


def test_reactivate_memory_symmetric(temp_project_with_migrations):
    """不变式 #22: archive 可撤销"""
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.forgetting_service import (
        archive_stale_memories, ForgetParams, reactivate_memory,
    )
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    _seed_aged_memory(db, "m_revive", "p3", relevance=0.05, days_ago=200)
    archive_stale_memories(db, ForgetParams(dry_run=False))

    ok = reactivate_memory(db, "m_revive")
    assert ok is True

    conn = sqlite3.connect(db)
    s = conn.execute(
        "SELECT status FROM memories WHERE memory_id='m_revive'"
    ).fetchone()[0]
    conn.close()
    assert s == "active"


def test_condense_cluster_candidates(temp_project_with_migrations):
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.forgetting_service import condense_cluster_candidates
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    # 同一 person 下 7 条 idle memory
    for i in range(7):
        _seed_aged_memory(db, f"m_cl_{i}", "person_hoarder", relevance=0.5, days_ago=70)
    r = condense_cluster_candidates(db, min_cluster_size=5, idle_days=60)
    assert len(r) == 1
    assert r[0]["person_id"] == "person_hoarder"
    assert r[0]["memory_count"] >= 7


def test_slimming_report(temp_project_with_migrations):
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.forgetting_service import slimming_report
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    _seed_aged_memory(db, "m_A", "p1", relevance=0.9, days_ago=1, status="active")
    _seed_aged_memory(db, "m_C", "p1", relevance=0.1, days_ago=200, status="cold")
    r = slimming_report(db)
    assert r["active"] >= 1
    assert r["cold"] >= 1
    assert 0.0 <= r["active_ratio"] <= 1.0


def test_unmerge_person_roundtrip(temp_project_with_migrations):
    """merge → unmerge 能成功，source 回 active"""
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.entity_unmerge_service import unmerge_person
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"

    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO persons(person_id, primary_name, status, confidence, "
        "metadata_json, created_at, updated_at) VALUES('pS','source','merged',0.5,"
        "?, datetime('now'), datetime('now'))",
        (json.dumps({"merged_into": "pT"}),),
    )
    conn.execute(
        "INSERT INTO persons(person_id, primary_name, status, confidence, "
        "metadata_json, created_at, updated_at) VALUES('pT','target','active',0.8,"
        "'{}', datetime('now'), datetime('now'))"
    )
    conn.commit()
    conn.close()

    r = unmerge_person(db, "pS", reviewer="test", reason="test-reverse")
    assert r["source_pid"] == "pS"
    assert r["target_pid"] == "pT"
    assert r["event_id"].startswith("evt_unmerge_")

    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT status, metadata_json FROM persons WHERE person_id='pS'"
    ).fetchone()
    conn.close()
    assert row[0] == "active"
    meta = json.loads(row[1])
    assert "merged_into" not in meta
    assert "unmerge_history" in meta


def test_unmerge_rejects_non_merged(temp_project_with_migrations):
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.entity_unmerge_service import unmerge_person
    import pytest
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"

    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO persons(person_id, primary_name, status, confidence, "
        "metadata_json, created_at, updated_at) VALUES('pA','A','active',0.8,'{}',"
        "datetime('now'),datetime('now'))"
    )
    conn.commit()
    conn.close()

    with pytest.raises(ValueError, match="not in merged state"):
        unmerge_person(db, "pA")


def test_list_merged_candidates(temp_project_with_migrations):
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.entity_unmerge_service import list_merged_candidates
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO persons(person_id, primary_name, status, confidence, "
        "metadata_json, created_at, updated_at) VALUES('pS1','s1','merged',0.5, "
        "?, datetime('now'), datetime('now'))",
        (json.dumps({"merged_into": "pT1"}),),
    )
    conn.commit()
    conn.close()
    items = list_merged_candidates(db)
    assert len(items) == 1
    assert items[0]["source_pid"] == "pS1"


def test_derive_unmerge_from_contradictions_only_candidates(temp_project_with_migrations):
    """不变式 #18 + #22：contradiction → unmerge candidate 仅是 suggestion，不自动改图"""
    from we_together.db.bootstrap import bootstrap_project
    from we_together.services.entity_unmerge_service import (
        derive_unmerge_candidates_from_contradictions, list_merged_candidates,
    )
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO persons(person_id, primary_name, status, confidence, "
        "metadata_json, created_at, updated_at) VALUES('pS2','s2','merged',0.5, "
        "?, datetime('now'), datetime('now'))",
        (json.dumps({"merged_into": "pT2"}),),
    )
    conn.commit()
    conn.close()

    before = len(list_merged_candidates(db))
    cands = derive_unmerge_candidates_from_contradictions(db)
    after = len(list_merged_candidates(db))

    # 函数调用不自动 unmerge
    assert before == after == 1
    assert len(cands) == 1
    assert "needs human gate" in cands[0]["note"]
