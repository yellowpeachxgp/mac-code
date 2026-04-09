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
