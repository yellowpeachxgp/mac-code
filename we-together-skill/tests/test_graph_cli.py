from pathlib import Path
import subprocess
import json


def test_graph_summary_cli_shows_people_and_relations(temp_project_with_migrations):
    repo_root = Path(__file__).resolve().parents[1]
    python = str(repo_root / ".venv" / "bin" / "python")

    subprocess.run(
        [python, str(repo_root / "scripts" / "bootstrap.py"), "--root", str(temp_project_with_migrations)],
        capture_output=True,
        text=True,
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        [
            python,
            str(repo_root / "scripts" / "import_narration.py"),
            "--root",
            str(temp_project_with_migrations),
            "--text",
            "小王和小李以前是同事，现在还是朋友。",
            "--source-name",
            "manual-note",
        ],
        capture_output=True,
        text=True,
        cwd=repo_root,
        check=True,
    )
    graph = subprocess.run(
        [
            python,
            str(repo_root / "scripts" / "graph_summary.py"),
            "--root",
            str(temp_project_with_migrations),
        ],
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    assert graph.returncode == 0, graph.stderr
    payload = json.loads(graph.stdout)
    assert payload["person_count"] >= 2
    assert payload["identity_count"] >= 2
    assert payload["relation_count"] >= 1


def test_graph_summary_cli_reports_branch_snapshot_and_runtime_counts(temp_project_with_migrations):
    repo_root = Path(__file__).resolve().parents[1]
    python = str(repo_root / ".venv" / "bin" / "python")

    subprocess.run(
        [python, str(repo_root / "scripts" / "bootstrap.py"), "--root", str(temp_project_with_migrations)],
        capture_output=True,
        text=True,
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        [
            python,
            str(repo_root / "scripts" / "import_narration.py"),
            "--root",
            str(temp_project_with_migrations),
            "--text",
            "小王和小李以前是同事，现在还是朋友。",
            "--source-name",
            "manual-note",
        ],
        capture_output=True,
        text=True,
        cwd=repo_root,
        check=True,
    )

    create_scene = subprocess.run(
        [
            python,
            str(repo_root / "scripts" / "create_scene.py"),
            "--root",
            str(temp_project_with_migrations),
            "--scene-type",
            "private_chat",
            "--summary",
            "graph summary scene",
            "--location-scope",
            "remote",
            "--channel-scope",
            "private_dm",
            "--visibility-scope",
            "mutual_visible",
            "--participant",
            "person_alice",
        ],
        capture_output=True,
        text=True,
        cwd=repo_root,
        check=True,
    )
    scene_id = json.loads(create_scene.stdout)["scene_id"]

    subprocess.run(
        [
            python,
            str(repo_root / "scripts" / "build_retrieval_package.py"),
            "--root",
            str(temp_project_with_migrations),
            "--scene-id",
            scene_id,
            "--input-hash",
            "graph_summary_hash",
        ],
        capture_output=True,
        text=True,
        cwd=repo_root,
        check=True,
    )

    graph = subprocess.run(
        [
            python,
            str(repo_root / "scripts" / "graph_summary.py"),
            "--root",
            str(temp_project_with_migrations),
        ],
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    assert graph.returncode == 0, graph.stderr
    payload = json.loads(graph.stdout)

    assert payload["snapshot_entity_count"] >= 1
    assert payload["retrieval_cache_count"] >= 1
    assert payload["scene_active_relation_count"] >= 0
    assert payload["open_local_branch_count"] == 0
