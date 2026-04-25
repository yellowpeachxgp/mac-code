"""Host smoke for the Phase 73 WebUI server.

Runs:
  seed_demo -> start in-process WebUI server -> curl-like HTTP checks.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from seed_demo import seed_society_c

from we_together.webui.server import WebUIConfig, create_server


def _request(base_url: str, path: str, *, token: str | None = None) -> dict:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{base_url}{path}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read().decode("utf-8")
            return {
                "status": response.status,
                "body": json.loads(body) if body.startswith("{") else body,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        return {
            "status": exc.code,
            "body": json.loads(body) if body.startswith("{") else body,
        }


def run_smoke(root: Path, *, token: str = "dev-token") -> dict:
    seed_society_c(root)
    server = create_server(
        WebUIConfig(root=root, host="127.0.0.1", port=0, token=token)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    base_url = f"http://{host}:{port}"
    try:
        checks = {
            "healthz": _request(base_url, "/healthz"),
            "summary_no_token": _request(base_url, "/api/summary"),
            "summary": _request(base_url, "/api/summary", token=token),
            "graph": _request(base_url, "/api/graph", token=token),
        }
    finally:
        server.shutdown()
        server.server_close()

    ok = (
        checks["healthz"]["status"] == 200
        and checks["summary_no_token"]["status"] == 401
        and checks["summary"]["status"] == 200
        and checks["graph"]["status"] == 200
        and len(checks["graph"]["body"]["data"]["nodes"]) > 0
    )
    return {"ok": ok, "base_url": base_url, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run WebUI host smoke.")
    parser.add_argument("--root", required=True)
    parser.add_argument("--token", default="dev-token")
    args = parser.parse_args()
    report = run_smoke(Path(args.root).resolve(), token=args.token)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
