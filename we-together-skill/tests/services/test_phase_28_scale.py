import sqlite3
from datetime import UTC, datetime

from we_together.db.backends import PGBackend, SQLiteBackend
from we_together.db.bootstrap import bootstrap_project
from we_together.llm.providers.embedding import MockEmbeddingClient
from we_together.services.embedding_cache import EmbeddingLRUCache
from we_together.services.embedding_recall import associate_by_embedding
from we_together.services.memory_cluster_service import cluster_memories
from we_together.services.vector_index import VectorIndex
from we_together.services.vector_similarity import encode_vec


# --- VI-1: VectorIndex ---

def test_vector_index_build_and_query(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    client = MockEmbeddingClient(dim=16)

    # 插入 3 条 memory + embedding
    c = sqlite3.connect(db)
    now = datetime.now(UTC).isoformat()
    for i, text in enumerate(["工作讨论", "家庭聚餐", "旅行攻略"]):
        c.execute(
            """INSERT INTO memories(memory_id, memory_type, summary, relevance_score,
               confidence, is_shared, status, metadata_json, created_at, updated_at)
               VALUES(?, 'shared_memory', ?, 0.7, 0.7, 1, 'active', '{}', ?, ?)""",
            (f"m_vi_{i}", text, now, now),
        )
        vec = client.embed([text])[0]
        c.execute(
            """INSERT INTO memory_embeddings(memory_id, model_name, dim, vec,
               created_at) VALUES(?, ?, ?, ?, ?)""",
            (f"m_vi_{i}", client.provider, client.dim, encode_vec(vec), now),
        )
    c.commit(); c.close()

    idx = VectorIndex.build(db, target="memory")
    assert idx.size() == 3
    q_vec = client.embed(["工作讨论"])[0]
    results = idx.query(q_vec, k=2)
    assert results[0][0] == "m_vi_0"


def test_vector_index_hierarchical(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    client = MockEmbeddingClient(dim=16)

    c = sqlite3.connect(db)
    now = datetime.now(UTC).isoformat()
    # 两 person：Alice 有 2 条 memory，Bob 1 条
    c.execute(
        "INSERT INTO persons(person_id, primary_name, status, confidence, "
        "metadata_json, created_at, updated_at) "
        "VALUES('p_a', 'Alice', 'active', 0.8, '{}', ?, ?)",
        (now, now),
    )
    c.execute(
        "INSERT INTO persons(person_id, primary_name, status, confidence, "
        "metadata_json, created_at, updated_at) "
        "VALUES('p_b', 'Bob', 'active', 0.8, '{}', ?, ?)",
        (now, now),
    )
    for i, (text, owner) in enumerate([
        ("alice work", "p_a"),
        ("alice life", "p_a"),
        ("bob work", "p_b"),
    ]):
        mid = f"m_h_{i}"
        c.execute(
            """INSERT INTO memories(memory_id, memory_type, summary, relevance_score,
               confidence, is_shared, status, metadata_json, created_at, updated_at)
               VALUES(?, 'shared_memory', ?, 0.7, 0.7, 1, 'active', '{}', ?, ?)""",
            (mid, text, now, now),
        )
        c.execute(
            "INSERT INTO memory_owners(memory_id, owner_type, owner_id, role_label) "
            "VALUES(?, 'person', ?, NULL)",
            (mid, owner),
        )
        vec = client.embed([text])[0]
        c.execute(
            """INSERT INTO memory_embeddings(memory_id, model_name, dim, vec,
               created_at) VALUES(?, ?, ?, ?, ?)""",
            (mid, client.provider, client.dim, encode_vec(vec), now),
        )
    c.commit(); c.close()

    # 按 p_a 过滤 → 应该只含 alice memories
    q = client.embed(["alice work"])[0]
    filtered = VectorIndex.hierarchical_query(
        db, q, target="memory", filter_person_ids=["p_a"], k=5,
    )
    ids = [mid for mid, _ in filtered]
    assert "m_h_0" in ids and "m_h_1" in ids
    assert "m_h_2" not in ids


# --- VI-2 associative 层级 ---

def test_associate_by_embedding_with_filter(temp_project_with_migrations):
    """使用 filter_person_ids 时自动走 hierarchical。"""
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    client = MockEmbeddingClient(dim=16)

    c = sqlite3.connect(db)
    now = datetime.now(UTC).isoformat()
    c.execute(
        "INSERT INTO persons(person_id, primary_name, status, confidence, "
        "metadata_json, created_at, updated_at) VALUES('pp', 'X', 'active', 0.8, '{}', ?, ?)",
        (now, now),
    )
    c.execute(
        """INSERT INTO memories(memory_id, memory_type, summary, relevance_score,
           confidence, is_shared, status, metadata_json, created_at, updated_at)
           VALUES('m_flt', 'shared_memory', 'seed', 0.7, 0.7, 1, 'active', '{}', ?, ?)""",
        (now, now),
    )
    c.execute(
        "INSERT INTO memory_owners(memory_id, owner_type, owner_id, role_label) "
        "VALUES('m_flt', 'person', 'pp', NULL)",
    )
    vec = client.embed(["seed"])[0]
    c.execute(
        """INSERT INTO memory_embeddings(memory_id, model_name, dim, vec, created_at)
           VALUES('m_flt', ?, ?, ?, ?)""",
        (client.provider, client.dim, encode_vec(vec), now),
    )
    c.commit(); c.close()

    r = associate_by_embedding(
        db, seed_text="seed", embedding_client=client,
        filter_person_ids=["pp"], top_k=1,
    )
    assert r["mode"] == "hierarchical"
    assert r["associated"] == ["m_flt"]


# --- VI-5 Cache ---

def test_lru_cache_hit_miss():
    cache = EmbeddingLRUCache(maxsize=4, ttl_seconds=60)
    client = MockEmbeddingClient(dim=8)
    r1 = cache.embed_with_cache(["a", "b", "a"], client)
    assert len(r1) == 3
    assert cache.misses == 2
    assert cache.hits == 1
    assert abs(cache.hit_rate() - (1/3)) < 1e-6


def test_lru_cache_evicts_oldest():
    cache = EmbeddingLRUCache(maxsize=2, ttl_seconds=60)
    client = MockEmbeddingClient(dim=4)
    cache.embed_with_cache(["a"], client)
    cache.embed_with_cache(["b"], client)
    cache.embed_with_cache(["c"], client)  # evict a
    assert cache.get("a") is None
    assert cache.get("b") is not None
    assert cache.get("c") is not None


# --- VI-6 Backends ---

def test_sqlite_backend_connect(tmp_path):
    p = tmp_path / "x.sqlite"
    b = SQLiteBackend(p)
    assert b.name == "sqlite"
    # 空路径也能 connect（会自动创建）
    conn = b.connect()
    conn.close()


def test_pg_backend_requires_dep():
    import pytest
    try:
        import psycopg  # noqa: F401
        pytest.skip("psycopg installed, skip negative test")
    except ImportError:
        with pytest.raises(RuntimeError):
            PGBackend(dsn="postgres://localhost/x")


# --- VI-8 Cluster 双模 ---

def test_cluster_embedding_mode(temp_project_with_migrations):
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    client = MockEmbeddingClient(dim=16)
    c = sqlite3.connect(db)
    now = datetime.now(UTC).isoformat()
    # 两个文本相同的 memory 应该聚成一组（cosine=1）
    for i, text in enumerate(["same text", "same text", "other text"]):
        mid = f"m_cl_{i}"
        c.execute(
            """INSERT INTO memories(memory_id, memory_type, summary, relevance_score,
               confidence, is_shared, status, metadata_json, created_at, updated_at)
               VALUES(?, 'shared_memory', ?, 0.7, 0.7, 1, 'active', '{}', ?, ?)""",
            (mid, text, now, now),
        )
        vec = client.embed([text])[0]
        c.execute(
            """INSERT INTO memory_embeddings(memory_id, model_name, dim, vec,
               created_at) VALUES(?, ?, ?, ?, ?)""",
            (mid, client.provider, client.dim, encode_vec(vec), now),
        )
    c.commit(); c.close()

    clusters = cluster_memories(
        db, use_embedding=True, embedding_similarity_threshold=0.99,
        min_cluster_size=2,
    )
    # m_cl_0 + m_cl_1 应聚成一组
    found = False
    for cl in clusters:
        if set(cl["memory_ids"]) == {"m_cl_0", "m_cl_1"}:
            found = True
            assert cl["method"] == "embedding"
    assert found


def test_cluster_jaccard_fallback(temp_project_with_migrations):
    """无 embedding 时 use_embedding=True 也能 fallback 到 Jaccard。"""
    bootstrap_project(temp_project_with_migrations)
    db = temp_project_with_migrations / "db" / "main.sqlite3"
    c = sqlite3.connect(db)
    now = datetime.now(UTC).isoformat()
    for pid in ["p1", "p2"]:
        c.execute(
            "INSERT INTO persons(person_id, primary_name, status, confidence, "
            "metadata_json, created_at, updated_at) VALUES(?, ?, 'active', 0.8, '{}', ?, ?)",
            (pid, pid, now, now),
        )
    for i in range(3):
        c.execute(
            """INSERT INTO memories(memory_id, memory_type, summary, relevance_score,
               confidence, is_shared, status, metadata_json, created_at, updated_at)
               VALUES(?, 'shared_memory', 'x', 0.7, 0.7, 1, 'active', '{}', ?, ?)""",
            (f"m_j_{i}", now, now),
        )
    for mid in ["m_j_0", "m_j_1"]:
        for pid in ["p1", "p2"]:
            c.execute(
                "INSERT INTO memory_owners(memory_id, owner_type, owner_id, role_label) "
                "VALUES(?, 'person', ?, NULL)",
                (mid, pid),
            )
    c.commit(); c.close()

    clusters = cluster_memories(db, use_embedding=True)
    # 无 embedding → fallback jaccard；0/1 共享 owners 应聚
    ok = any(set(c["memory_ids"]) >= {"m_j_0", "m_j_1"} for c in clusters)
    assert ok
