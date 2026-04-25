"""Browser smoke for the Phase 73 WebUI.

Runs a real browser through playwright-cli:
  seed_demo -> start WebUI -> enter token -> assert graph -> open drawer -> screenshot.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from seed_demo import seed_society_c

from we_together.webui.server import WebUIConfig, create_server


def _playwright_cli_command() -> list[str]:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    wrapper = codex_home / "skills" / "playwright" / "scripts" / "playwright_cli.sh"
    if wrapper.exists():
        return ["bash", str(wrapper)]
    return ["npx", "--yes", "--package", "@playwright/cli", "playwright-cli"]


def _run_cli(base_cmd: list[str], args: list[str], *, env: dict[str, str]) -> str:
    completed = subprocess.run(
        [*base_cmd, *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    if completed.returncode != 0:
        raise RuntimeError(f"playwright-cli {' '.join(args)} failed:\n{output}")
    return output


def _wait_for_snapshot(base_cmd: list[str], *, env: dict[str, str], needle: str, attempts: int = 8) -> str:
    last = ""
    for _ in range(attempts):
        time.sleep(0.4)
        last = _run_cli(base_cmd, ["snapshot"], env=env)
        if needle in last:
            return last
    raise RuntimeError(f"snapshot did not contain {needle!r}:\n{last}")


def run_smoke(root: Path, *, token: str, output_dir: Path, headed: bool = False) -> dict:
    static_dir = ROOT / "webui" / "dist"
    if not static_dir.exists():
        raise RuntimeError("webui/dist not found; run `cd webui && npm run build` first.")

    seed_society_c(root)
    server = create_server(
        WebUIConfig(root=root, host="127.0.0.1", port=0, token=token, static_dir=static_dir)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    base_url = f"http://{host}:{port}"
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot = (output_dir / "webui-graph-workspace.png").resolve()
    cli_tmp = Path("/tmp/wtpw")
    cli_tmp.mkdir(parents=True, exist_ok=True)
    session = f"wt{uuid.uuid4().hex[:4]}"
    env = {
        **os.environ,
        "PLAYWRIGHT_CLI_SESSION": session,
        "TMPDIR": str(cli_tmp),
        "TMP": str(cli_tmp),
        "TEMP": str(cli_tmp),
    }
    cli = _playwright_cli_command()

    try:
        open_args = ["open", base_url]
        if headed:
            open_args.append("--headed")
        _run_cli(cli, open_args, env=env)
        _run_cli(cli, ["resize", "1440", "980"], env=env)
        _wait_for_snapshot(cli, env=env, needle="连接 we-together")
        _run_cli(cli, ["fill", 'input[placeholder="输入 Bearer token"]', token], env=env)
        _run_cli(cli, ["click", "text=进入工作台"], env=env)
        graph_snapshot = _wait_for_snapshot(cli, env=env, needle="图谱工作台")
        if "Alice" not in graph_snapshot:
            raise RuntimeError(f"graph snapshot did not contain seeded person Alice:\n{graph_snapshot}")
        match = re.search(r'button "person Alice" \[ref=(e\d+)\]', graph_snapshot)
        if not match:
            match = re.search(r'button "Alice" \[ref=(e\d+)\]', graph_snapshot)
        if not match:
            raise RuntimeError(f"could not find Alice button ref in snapshot:\n{graph_snapshot}")
        _run_cli(cli, ["click", match.group(1)], env=env)
        drawer_snapshot = _wait_for_snapshot(cli, env=env, needle="标签")
        if "person_" not in drawer_snapshot or "类型" not in drawer_snapshot:
            raise RuntimeError(f"drawer snapshot did not expose person detail:\n{drawer_snapshot}")
        _run_cli(cli, ["screenshot", "--filename", str(screenshot), "--full-page"], env=env)
    finally:
        try:
            _run_cli(cli, ["close"], env=env)
        except Exception:
            pass
        server.shutdown()
        server.server_close()

    return {
        "ok": True,
        "base_url": base_url,
        "root": str(root),
        "screenshot": str(screenshot),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run WebUI Playwright browser smoke.")
    parser.add_argument("--root", default=None)
    parser.add_argument("--token", default="dev-token")
    parser.add_argument("--output-dir", default=str(ROOT / "output" / "playwright"))
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()

    if args.root:
        root = Path(args.root).resolve()
        root.mkdir(parents=True, exist_ok=True)
        report = run_smoke(
            root,
            token=args.token,
            output_dir=Path(args.output_dir).resolve(),
            headed=args.headed,
        )
    else:
        with tempfile.TemporaryDirectory(prefix="wt-webui-browser-") as tmp:
            report = run_smoke(
                Path(tmp),
                token=args.token,
                output_dir=Path(args.output_dir).resolve(),
                headed=args.headed,
            )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
