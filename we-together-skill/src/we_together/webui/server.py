"""Stdlib HTTP server for the host-local WebUI."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from we_together.observability.metrics import export_prometheus_text
from we_together.services.tenant_router import resolve_tenant_root
from we_together.webui import actions, queries
from we_together.webui.auth import BearerTokenAuth, is_loopback_host

FALLBACK_HTML = """<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>we-together WebUI</title></head>
<body><main id="root"><h1>we-together WebUI</h1><p>React build not found. Run the Vite build under webui/.</p></main></body>
</html>
"""


@dataclass
class WebUIConfig:
    root: Path
    host: str = "127.0.0.1"
    port: int = 7788
    tenant_id: str | None = None
    token: str | None = None
    static_dir: Path | None = None
    rate_limit_per_minute: int = 120
    llm_client: object | None = None


class WebUIServer(HTTPServer):
    config: WebUIConfig
    tenant_root: Path
    auth: BearerTokenAuth


def resolve_token(cli_token: str | None = None) -> str | None:
    return cli_token or os.environ.get("WE_TOGETHER_WEBUI_TOKEN")


def validate_startup_security(config: WebUIConfig) -> None:
    if not is_loopback_host(config.host) and not config.token:
        raise ValueError("A bearer token is required when WebUI listens on a non-loopback host.")


def _json_body(ok: bool, payload: dict, *, status: int) -> bytes:
    body = {"ok": ok}
    if ok:
        body["data"] = payload
    else:
        body["error"] = payload
    return json.dumps(body, ensure_ascii=False).encode("utf-8")


def _content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".html": "text/html; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".mjs": "application/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".ico": "image/x-icon",
    }.get(suffix, "application/octet-stream")


def _safe_static_path(static_dir: Path, request_path: str) -> Path | None:
    rel = request_path.lstrip("/") or "index.html"
    if rel.endswith("/"):
        rel += "index.html"
    candidate = (static_dir / rel).resolve()
    static_root = static_dir.resolve()
    try:
        candidate.relative_to(static_root)
    except ValueError:
        return None
    if candidate.exists() and candidate.is_file():
        return candidate
    index = static_root / "index.html"
    return index if index.exists() else None


def make_handler():
    class H(BaseHTTPRequestHandler):
        server: WebUIServer

        def _send_bytes(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, status: int, payload: dict, *, ok: bool = True) -> None:
            self._send_bytes(
                status,
                _json_body(ok, payload, status=status),
                "application/json; charset=utf-8",
            )

        def _error(self, status: int, code: str, message: str) -> None:
            self._send_json(status, {"code": code, "message": message}, ok=False)

        def _require_auth(self) -> bool:
            auth_result = self.server.auth.authenticate(self.headers.get("Authorization"))
            if auth_result.ok:
                return True
            self._error(auth_result.status, auth_result.code, auth_result.message)
            return False

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length") or "0")
            if length <= 0:
                return {}
            raw = self.rfile.read(length)
            if not raw:
                return {}
            return json.loads(raw.decode("utf-8"))

        def _handle_api_get(self, parsed) -> None:
            root = self.server.tenant_root
            path = parsed.path
            query = queries.parse_query(parsed.query)
            if path == "/api/bootstrap":
                self._send_json(200, queries.bootstrap(root, self.server.auth.mode))
            elif path == "/api/summary":
                self._send_json(200, queries.summary(root))
            elif path == "/api/scenes":
                self._send_json(200, queries.scenes(root))
            elif path == "/api/graph":
                self._send_json(
                    200,
                    queries.graph(
                        root,
                        scene_id=(query.get("scene_id") or [None])[0],
                        include=(query.get("include") or [None])[0],
                    ),
                )
            elif path.startswith("/api/entities/"):
                parts = [unquote(part) for part in path.split("/")]
                if len(parts) != 5:
                    self._error(404, "not_found", "Entity route not found.")
                    return
                self._send_json(200, queries.entity_detail(root, parts[3], parts[4]))
            elif path == "/api/events":
                self._send_json(200, queries.events(root, query))
            elif path == "/api/patches":
                self._send_json(200, queries.patches(root, query))
            elif path == "/api/snapshots":
                self._send_json(200, queries.snapshots(root, query))
            elif path == "/api/retrieval-package":
                self._send_json(200, queries.retrieval_package(root, query))
            elif path == "/api/world":
                self._send_json(200, queries.world(root, query))
            elif path == "/api/world/objects":
                self._send_json(200, queries.list_world_objects(root))
            elif path == "/api/world/places":
                self._send_json(200, queries.list_world_places(root))
            elif path == "/api/world/projects":
                self._send_json(200, queries.list_world_projects(root))
            elif path == "/api/branches":
                self._send_json(200, queries.branches(root, query))
            elif path == "/api/metrics":
                self._send_json(200, {"prometheus": export_prometheus_text()})
            else:
                self._error(404, "not_found", "API route not found.")

        def _handle_api_write(self, method: str, parsed) -> None:
            root = self.server.tenant_root
            path = parsed.path
            body = self._read_json()
            if method == "PATCH" and path.startswith("/api/entities/"):
                parts = [unquote(part) for part in path.split("/")]
                if len(parts) != 5:
                    self._error(404, "not_found", "Entity route not found.")
                    return
                fields = body.get("fields") if "fields" in body else body
                self._send_json(200, actions.update_entity(root, parts[3], parts[4], fields))
            elif method == "POST" and path.startswith("/api/entities/") and path.endswith("/archive"):
                parts = [unquote(part) for part in path.split("/")]
                if len(parts) != 6:
                    self._error(404, "not_found", "Entity route not found.")
                    return
                self._send_json(
                    200,
                    actions.archive_entity(root, parts[3], parts[4], reactivate=body.get("action") == "reactivate"),
                )
            elif method == "POST" and path == "/api/entities/link":
                self._send_json(200, actions.link_entities(root, body, unlink=False))
            elif method == "POST" and path == "/api/entities/unlink":
                self._send_json(200, actions.link_entities(root, body, unlink=True))
            elif method == "POST" and path == "/api/memories":
                self._send_json(200, actions.create_memory(root, body))
            elif method == "POST" and path == "/api/chat/run-turn":
                self._send_json(200, actions.chat_turn(root, body, llm_client=self.server.config.llm_client))
            elif method == "POST" and path == "/api/scenes":
                self._send_json(200, actions.create_scene_action(root, body))
            elif method == "POST" and path.startswith("/api/scenes/") and path.endswith("/participants"):
                parts = [unquote(part) for part in path.split("/")]
                if len(parts) != 6:
                    self._error(404, "not_found", "Scene route not found.")
                    return
                self._send_json(200, actions.add_participant_action(root, parts[3], body))
            elif method == "PATCH" and path.startswith("/api/scenes/"):
                parts = [unquote(part) for part in path.split("/")]
                if len(parts) != 4:
                    self._error(404, "not_found", "Scene route not found.")
                    return
                self._send_json(200, actions.set_scene_status_action(root, parts[3], body.get("status", "")))
            elif method == "POST" and path.startswith("/api/branches/") and path.endswith("/resolve"):
                parts = [unquote(part) for part in path.split("/")]
                if len(parts) != 5:
                    self._error(404, "not_found", "Branch route not found.")
                    return
                self._send_json(200, actions.resolve_branch(root, parts[3], body))
            elif method == "POST" and path == "/api/world/objects":
                self._send_json(200, actions.create_world_object(root, body))
            elif method == "POST" and path == "/api/world/places":
                self._send_json(200, actions.create_world_place(root, body))
            elif method == "POST" and path == "/api/world/projects":
                self._send_json(200, actions.create_world_project(root, body))
            elif method == "PATCH" and path.startswith("/api/world/projects/") and path.endswith("/status"):
                parts = [unquote(part) for part in path.split("/")]
                if len(parts) != 6:
                    self._error(404, "not_found", "Project route not found.")
                    return
                self._send_json(200, actions.update_world_project_status(root, parts[4], body))
            elif method == "PATCH" and path.startswith("/api/world/objects/") and path.endswith("/owner"):
                parts = [unquote(part) for part in path.split("/")]
                if len(parts) != 6:
                    self._error(404, "not_found", "Object route not found.")
                    return
                self._send_json(200, actions.update_world_object_owner(root, parts[4], body))
            elif method == "PATCH" and path.startswith("/api/world/objects/") and path.endswith("/status"):
                parts = [unquote(part) for part in path.split("/")]
                if len(parts) != 6:
                    self._error(404, "not_found", "Object route not found.")
                    return
                self._send_json(200, actions.update_world_object_status(root, parts[4], body))
            else:
                self._error(404, "not_found", "API route not found.")

        def _serve_static(self, path: str) -> None:
            static_dir = self.server.config.static_dir
            if static_dir:
                static_file = _safe_static_path(static_dir, path)
                if static_file:
                    self._send_bytes(200, static_file.read_bytes(), _content_type(static_file))
                    return
            self._send_bytes(200, FALLBACK_HTML.encode("utf-8"), "text/html; charset=utf-8")

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            try:
                if parsed.path == "/healthz":
                    self._send_json(200, queries.health(self.server.tenant_root, self.server.auth.mode))
                elif parsed.path == "/metrics":
                    self._send_bytes(
                        200,
                        export_prometheus_text().encode("utf-8"),
                        "text/plain; version=0.0.4; charset=utf-8",
                    )
                elif parsed.path.startswith("/api/"):
                    if self._require_auth():
                        self._handle_api_get(parsed)
                else:
                    self._serve_static(parsed.path)
            except KeyError as exc:
                self._error(404, "not_found", str(exc))
            except Exception as exc:
                self._error(400, "bad_request", str(exc))

        def do_POST(self) -> None:
            self._do_write("POST")

        def do_PATCH(self) -> None:
            self._do_write("PATCH")

        def _do_write(self, method: str) -> None:
            parsed = urlparse(self.path)
            if not parsed.path.startswith("/api/"):
                self._error(404, "not_found", "Route not found.")
                return
            try:
                if self._require_auth():
                    self._handle_api_write(method, parsed)
            except KeyError as exc:
                self._error(404, "not_found", str(exc))
            except json.JSONDecodeError:
                self._error(400, "bad_json", "Request body must be valid JSON.")
            except Exception as exc:
                self._error(400, "bad_request", str(exc))

        def log_message(self, *args, **kwargs):
            return

    return H


def create_server(config: WebUIConfig) -> WebUIServer:
    config.root = Path(config.root).resolve()
    config.token = resolve_token(config.token)
    if config.static_dir is not None:
        config.static_dir = Path(config.static_dir).resolve()
    validate_startup_security(config)
    server = WebUIServer((config.host, config.port), make_handler())
    server.config = config
    server.tenant_root = resolve_tenant_root(config.root, config.tenant_id)
    server.auth = BearerTokenAuth(config.token, rate_limit_per_minute=config.rate_limit_per_minute)
    return server
