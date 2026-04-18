"""Phase 38 — 消费就绪 (CR slices)。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def test_getting_started_doc_exists():
    p = REPO_ROOT / "docs" / "getting-started.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    assert "bootstrap" in text
    assert "mcp_server" in text


def test_host_docs_exist():
    for host in ["claude-desktop", "claude-code", "openai-assistants"]:
        p = REPO_ROOT / "docs" / "hosts" / f"{host}.md"
        assert p.exists(), f"missing host doc: {host}"


def test_dashboard_script_importable():
    import importlib.util
    p = REPO_ROOT / "scripts" / "dashboard.py"
    spec = importlib.util.spec_from_file_location("wt_dashboard", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert callable(m._summary)
    assert callable(m._recent_ticks)
    assert "we-together" in m.DASHBOARD_HTML


def test_dashboard_summary_works(temp_project_with_migrations):
    from we_together.db.bootstrap import bootstrap_project
    import importlib.util
    bootstrap_project(temp_project_with_migrations)
    p = REPO_ROOT / "scripts" / "dashboard.py"
    spec = importlib.util.spec_from_file_location("wt_dashboard2", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    s = m._summary(temp_project_with_migrations)
    assert "persons" in s
    assert isinstance(s["persons"], int)
    t = m._recent_ticks(temp_project_with_migrations)
    assert "ticks" in t


def test_skill_host_smoke_all_steps(tmp_path):
    import importlib.util
    p = REPO_ROOT / "scripts" / "skill_host_smoke.py"
    spec = importlib.util.spec_from_file_location("wt_smoke", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    report = m.run_smoke(tmp_path)
    steps = {r["step"]: r["ok"] for r in report["results"]}
    assert steps.get("bootstrap") is True
    assert steps.get("seed_society_c") is True
    assert steps.get("dashboard_summary") is True


def test_metrics_endpoint_prometheus_format():
    from we_together.observability.metrics import (
        counter_inc, export_prometheus_text, reset,
    )
    reset()
    counter_inc("we_together_tick_total", 1.0, {"phase": "test"})
    text = export_prometheus_text()
    assert "we_together_tick_total" in text
    reset()


def test_mcp_adapter_tool_count_post_phase33():
    """Phase 38 验收：Phase 33 已把 tools 扩展到 6 个"""
    from we_together.runtime.adapters.mcp_adapter import (
        build_mcp_tools, build_mcp_resources, build_mcp_prompts,
    )
    assert len(build_mcp_tools()) == 6
    assert len(build_mcp_resources()) == 2
    assert len(build_mcp_prompts()) == 1


def test_skill_schema_is_still_v1():
    """Phase 38 新增功能不能破坏 schema v1（ADR 0034 不变式 #19）"""
    from we_together.runtime.skill_runtime import SKILL_SCHEMA_VERSION
    assert SKILL_SCHEMA_VERSION == "1"
