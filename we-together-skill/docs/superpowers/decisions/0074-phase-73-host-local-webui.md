---
adr: 0074
title: Phase 73 — Host-local WebUI Control Plane
status: Accepted
date: 2026-04-26
---

# ADR 0074: Phase 73 — Host-local WebUI Control Plane

## 状态

Accepted — 2026-04-26

## 背景

`we-together` 已经具备 CLI、MCP、Codex native skill、simulation、world modeling 与 patch-first graph evolution。但用户在日常操作中仍缺少一个“看得见”的宿主机控制面：

- 图谱关系、记忆、scene 激活不直观。
- branch candidate 与 operator-gated resolve 需要更清晰的复核界面。
- world objects / places / projects 与 chat turn 的结果需要被放在同一工作台里。

## 决策

### D1. 采用 host-local React SPA

前端放在 `webui/`：

- Vite
- React
- TypeScript
- React Flow
- lucide-react

后端保持 Python stdlib `HTTPServer`，入口为 `scripts/webui_server.py`，实现放入 `src/we_together/webui/`。

### D2. 局域网访问必须 token

当监听非 loopback host 时，如果未配置 `--token` 或 `WE_TOGETHER_WEBUI_TOKEN`，启动直接失败。

所有 `/api/*` 需要 `Authorization: Bearer <token>`。静态 SPA 可以匿名加载，但不能匿名读写图谱数据。

### D3. 写入必须走边界层

所有 WebUI 写接口进入 `webui.actions`：

- 核心 entity 更新走 `build_patch` + `apply_patch_record`。
- link/unlink/memory/branch resolve 走 patch。
- chat 走 `chat_service.run_turn`。
- scene 走 `scene_service`。
- world 第一版走 `world_service` 并补 `webui_audit` event。

### D4. Dashboard 兼容保留

`scripts/dashboard.py` 继续作为 legacy minimal dashboard 保留，不在 Phase 73 中扩写。

新功能集中在 `scripts/webui_server.py`，避免把旧三路由 dashboard 变成半成品应用服务器。

## 后果

### 正面

- 用户能用浏览器理解图谱 / world / review / timeline。
- 前端不会绕过 patch/event/service 约束。
- 局域网使用有基本 token 与 rate limit 防线。
- 后端依旧无新增 Python runtime 依赖。

### 代价

- 前端引入 Node/Vite 工具链。
- React build 产物默认不提交，需要单独 build。
- stdlib HTTPServer 不适合公网生产流量。

## 验收

- `tests/webui/test_webui_backend.py`
- `webui/src/App.test.tsx`
- `webui npm run build`
- host smoke: seed -> start server -> curl `/healthz`, `/api/summary`, `/api/graph`

## 参考

- Spec: `docs/superpowers/specs/2026-04-26-host-local-react-webui.md`
- Prior auth precedent: `src/we_together/services/federation_security.py`
- Prior HTTP precedent: `scripts/dashboard.py`, `scripts/branch_console.py`
