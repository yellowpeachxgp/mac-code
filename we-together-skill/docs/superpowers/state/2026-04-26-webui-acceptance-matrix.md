# Phase 73 WebUI 验收矩阵

日期：2026-04-26

| 编号 | Area | 验收项 | 当前证据 |
|---|---|---|---|
| A01 | Design | WebUI 设计文档 | `docs/superpowers/specs/2026-04-26-host-local-react-webui.md` |
| A02 | ADR | ADR 0074 | `docs/superpowers/decisions/0074-phase-73-host-local-webui.md` |
| A03 | Status | HANDOFF/current-status 更新 | Phase 73 条目 |
| A04 | Matrix | 验收矩阵 | 本文件 |
| A05 | Backend package | `src/we_together/webui/` | `auth.py`, `queries.py`, `actions.py`, `server.py` |
| A06 | Server script | `scripts/webui_server.py` | stdlib HTTPServer |
| A07 | Legacy dashboard | `scripts/dashboard.py` 保留 | 文档标记为 legacy minimal dashboard |
| A08 | Health | `/healthz` | backend pytest |
| A09 | Bootstrap | `/api/bootstrap` | backend pytest |
| A10 | Tenant | `resolve_tenant_root` | `WebUIConfig.tenant_id` |
| A11 | Bearer | `/api/*` token | backend pytest |
| A12 | Token source | `--token`, `WE_TOGETHER_WEBUI_TOKEN` | `resolve_token()` |
| A13 | LAN guard | 非 loopback 无 token 失败 | backend pytest |
| A14 | Rate limit | `RateLimiter` 120/min | `webui.auth.BearerTokenAuth` |
| A15 | JSON error | `ok=false/error` | backend pytest |
| B01-B12 | Read APIs | summary/scenes/graph/entity/events/patches/snapshots/retrieval/world/branches/metrics | backend pytest + implementation |
| C01-C15 | Write APIs | entity patch/link/unlink/chat/world create/object status/object owner/project status/branch | backend pytest + implementation |
| D01-D15 | Frontend shell | Vite React TS + token gate + graph workspace + drawer + diff | `webui/src/App.tsx`, `webui/src/App.test.tsx` |
| E01-E12 | Product pages | Graph/Chat/World/Review/Editor/Timeline/Metrics | `webui/src/App.tsx` |
| F01-F07 | Backend tests | auth/read/write/chat/world create+update/branch/static | `tests/webui/test_webui_backend.py`（12 tests） |
| F08 | Frontend tests | token gate, graph render, edit submit, chat turn, world update, review resolve | `webui/src/App.test.tsx`（6 tests） |
| F09 | Host smoke | seed/start/curl | `scripts/webui_smoke.py` |
| F10 | Screenshot | Playwright real browser：token gate → graph non-empty → Alice detail drawer → screenshot | `scripts/webui_playwright_smoke.py`；输出 `output/playwright/webui-graph-workspace.png` |
| F11 | Full pytest | 826 passed / 4 skipped | 已验证：`.venv/bin/python -m pytest -q` |
| F12-F14 | Docs | LAN token / scripts / getting-started | 文档更新 |
| F15 | Commit | `feat: add host-local React WebUI workbench` + follow-up completion commit | 以 git history 中最终 Phase 73 follow-up commit 为准 |
