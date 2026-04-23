from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_codex_skill_family_directories_exist():
    for rel in [
        "codex_skill",
        "codex_skill_dev",
        "codex_skill_runtime",
        "codex_skill_ingest",
    ]:
        assert (REPO_ROOT / rel).is_dir(), rel


def test_codex_skill_family_has_required_layout():
    required = [
        "SKILL.md",
        "agents/openai.yaml",
        "prompts/dev.md",
        "prompts/runtime.md",
        "prompts/ingest.md",
        "references/triggers.md",
        "references/intent-examples.md",
        "references/local-runtime.template.md",
    ]
    for root_name in [
        "codex_skill",
        "codex_skill_dev",
        "codex_skill_runtime",
        "codex_skill_ingest",
    ]:
        root = REPO_ROOT / root_name
        for rel in required:
            assert (root / rel).exists(), f"{root_name}/{rel}"


def test_router_skill_keeps_balanced_non_trigger_boundary():
    text = _read(REPO_ROOT / "codex_skill" / "SKILL.md")
    assert "Do not use for generic social graph theory" in text
    assert "裸词请求" in text
    assert "先读取 `references/local-runtime.md`" in text
    assert "路由层" in text


def test_dev_skill_is_scoped_to_project_development():
    text = _read(REPO_ROOT / "codex_skill_dev" / "SKILL.md")
    assert "当前状态" in text
    assert "交接文档" in text
    assert "继续 Phase" in text
    assert "图谱摘要" not in text
    assert "先读取 `references/local-runtime.md`" in text


def test_runtime_skill_is_scoped_to_graph_runtime():
    text = _read(REPO_ROOT / "codex_skill_runtime" / "SKILL.md")
    assert "图谱摘要" in text
    assert "不变式" in text
    assert "self_describe" in text or "自描述" in text
    assert "继续 Phase" not in text
    assert "先读取 `references/local-runtime.md`" in text


def test_ingest_skill_is_scoped_to_bootstrap_and_imports():
    text = _read(REPO_ROOT / "codex_skill_ingest" / "SKILL.md")
    assert "导入材料" in text
    assert "bootstrap" in text
    assert "import" in text
    assert "当前状态" not in text
    assert "先读取 `references/local-runtime.md`" in text


def test_intent_example_corpora_include_positive_and_negative_cases():
    for root_name in [
        "codex_skill",
        "codex_skill_dev",
        "codex_skill_runtime",
        "codex_skill_ingest",
    ]:
        text = _read(REPO_ROOT / root_name / "references" / "intent-examples.md")
        assert "## Positive" in text
        assert "## Negative" in text
        assert "we-together" in text
