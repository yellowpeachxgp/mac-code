"""federation_client（Phase 42 FD）：从远端 skill 的 HTTP endpoint 拉数据。

用法:
  from we_together.services.federation_client import FederationClient
  c = FederationClient("http://peer.example:7781")
  persons = c.list_persons()
  person = c.get_person("person_alice")
  memories = c.list_memories(owner_id="person_alice")

设计:
- 纯 stdlib urllib.request
- 不依赖 httpx / requests
- 超时默认 5s；失败抛 RuntimeError 含 status + body
- 客户端不做身份映射；交由 federation_fetcher 处理跨图谱 register
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass
class FederationClient:
    base_url: str
    timeout: float = 5.0

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = self.base_url.rstrip("/") + path
        if params:
            url += "?" + urllib.parse.urlencode({
                k: v for k, v in params.items() if v is not None
            })
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "we-together-federation-client/1",
        })
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            raise RuntimeError(
                f"federation GET {path} failed: {e.code} {e.reason}"
            ) from e

    def capabilities(self) -> dict:
        return self._get("/federation/v1/capabilities")

    def list_persons(self, *, limit: int = 50) -> dict:
        return self._get("/federation/v1/persons", {"limit": limit})

    def get_person(self, person_id: str) -> dict | None:
        try:
            return self._get(f"/federation/v1/persons/{person_id}")
        except RuntimeError as e:
            if "404" in str(e):
                return None
            raise

    def list_memories(
        self, *, owner_id: str | None = None, limit: int = 50,
    ) -> dict:
        return self._get(
            "/federation/v1/memories",
            {"owner_id": owner_id, "limit": limit},
        )
