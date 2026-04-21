"""多租户支持：按 tenant_id 路由到独立 db 目录。

路径约定:
  <root>/tenants/<tenant_id>/db/main.sqlite3

默认 tenant = 'default'，对应 <root>/db/main.sqlite3（向后兼容）。
"""
from __future__ import annotations

import re
from pathlib import Path

DEFAULT_TENANT_ID = "default"
TENANT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def normalize_tenant_id(tenant_id: str | None = None) -> str:
    tenant_id = (tenant_id or DEFAULT_TENANT_ID).strip() or DEFAULT_TENANT_ID
    if tenant_id == DEFAULT_TENANT_ID:
        return DEFAULT_TENANT_ID
    if tenant_id in {".", ".."}:
        raise ValueError(f"invalid tenant_id: {tenant_id!r}")
    if "/" in tenant_id or "\\" in tenant_id:
        raise ValueError(f"invalid tenant_id: {tenant_id!r}")
    if not TENANT_ID_RE.fullmatch(tenant_id):
        raise ValueError(f"invalid tenant_id: {tenant_id!r}")
    return tenant_id


def resolve_tenant_db_path(root: Path, tenant_id: str | None = None) -> Path:
    tenant_id = normalize_tenant_id(tenant_id)
    if tenant_id == DEFAULT_TENANT_ID:
        return root / "db" / "main.sqlite3"
    return root / "tenants" / tenant_id / "db" / "main.sqlite3"


def resolve_tenant_root(root: Path, tenant_id: str | None = None) -> Path:
    tenant_id = normalize_tenant_id(tenant_id)
    if tenant_id == DEFAULT_TENANT_ID:
        return root
    return root / "tenants" / tenant_id
