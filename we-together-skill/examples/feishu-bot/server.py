"""飞书机器人 webhook server (stdlib 实现)。

接收飞书 event webhook，经 feishu_adapter 转换为 SkillRequest，
再走 chat_service.run_turn（本地 mock LLM 或真实 LLM provider）。

启动:
  python examples/feishu-bot/server.py --root ~/.we-together --scene-id <scene_id>
  # 反向代理（ngrok）指向 http://127.0.0.1:7000

环境变量:
  FEISHU_SIGNING_SECRET  飞书签名密钥（可选；设置后启用验签）
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# 让脚本能找到源码
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from we_together.runtime.adapters.feishu_adapter import (
    format_reply,
    parse_webhook_payload,
    verify_signature,
)
from we_together.runtime.skill_runtime import SkillResponse


def _make_handler(*, db_path: Path, scene_id: str, secret: str | None):
    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            if secret:
                ts = self.headers.get("X-Lark-Request-Timestamp", "")
                nonce = self.headers.get("X-Lark-Request-Nonce", "")
                sig = self.headers.get("X-Lark-Signature", "")
                if not verify_signature(secret=secret, timestamp=ts, nonce=nonce,
                                         body=body, signature=sig):
                    self.send_response(401); self.end_headers()
                    self.wfile.write(b'{"error":"signature"}')
                    return

            try:
                raw = json.loads(body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self.send_response(400); self.end_headers()
                return

            # URL verification challenge
            if raw.get("type") == "url_verification":
                resp = {"challenge": raw.get("challenge", "")}
                self._send(200, resp)
                return

            req = parse_webhook_payload(raw, scene_id=scene_id)
            # 这里只做 echo + 记录日志，实际调用留给外层 runtime 或 mock
            resp = SkillResponse(
                text=f"[we-together echo] 收到：{req.user_input}",
                speaker_person_id=None,
            )
            chat_id = (raw.get("message") or {}).get("chat_id", "")
            self._send(200, format_reply(resp, chat_id=chat_id))

        def _send(self, code: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a, **kw):
            pass
    return H


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--scene-id", required=True)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=7000)
    args = ap.parse_args()
    db_path = Path(args.root).resolve() / "db" / "main.sqlite3"
    secret = os.environ.get("FEISHU_SIGNING_SECRET")

    srv = HTTPServer(
        (args.host, args.port),
        _make_handler(db_path=db_path, scene_id=args.scene_id, secret=secret),
    )
    print(f"feishu webhook listening on http://{args.host}:{args.port}  "
          f"(signing={'on' if secret else 'off'})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
