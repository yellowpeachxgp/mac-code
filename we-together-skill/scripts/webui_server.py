"""Host-local React WebUI server.

Example:
  WE_TOGETHER_WEBUI_TOKEN=dev-token \
    .venv/bin/python scripts/webui_server.py --root . --host 0.0.0.0 --port 7788
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from we_together.webui.server import WebUIConfig, create_server, resolve_token


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the we-together host-local WebUI.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--tenant-id", default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7788)
    parser.add_argument("--token", default=None)
    parser.add_argument("--static-dir", default=None)
    parser.add_argument("--rate-limit-per-minute", type=int, default=120)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    static_dir = Path(args.static_dir).resolve() if args.static_dir else repo_root / "webui" / "dist"
    config = WebUIConfig(
        root=Path(args.root),
        tenant_id=args.tenant_id,
        host=args.host,
        port=args.port,
        token=resolve_token(args.token),
        static_dir=static_dir if static_dir.exists() else None,
        rate_limit_per_minute=args.rate_limit_per_minute,
    )
    server = create_server(config)
    print(
        f"we-together WebUI serving http://{args.host}:{args.port} "
        f"tenant={args.tenant_id or 'default'} root={server.tenant_root}"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
