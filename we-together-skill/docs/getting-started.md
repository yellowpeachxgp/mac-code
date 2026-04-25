# we-together Getting Started (5 分钟)

从零到第一次 `run_turn` 的 5 分钟路径。

## 0. 前置

```bash
python --version   # 3.11+
git clone <repo> we-together && cd we-together
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## 1. Bootstrap（一次）

```bash
python scripts/bootstrap.py --root .
```

会在 `db/main.sqlite3` 落 15 条 migration + seeds。

## 2. 装一个示例社会（4-10 人）

```bash
python -c "
from scripts.seed_demo import seed_society_c
from pathlib import Path
seed_society_c(Path('.').resolve())
"
```

或跑一遍 e2e smoke：

```bash
python scripts/skill_host_smoke.py --root /tmp/wt-smoke
```

期望 `{"ok": true}`。

## 3. 跑一次对话

```bash
python scripts/chat.py
```

然后在 REPL 里发一句中文，例如 `早上好`。会自动走 retrieval → LLM → patch → snapshot。

## 4. 看图谱

```bash
python scripts/dashboard.py --root . --port 7780
# 浏览器打开 http://127.0.0.1:7780
```

/api/summary + /api/tick + /metrics (Prometheus 文本) 也可以裸调。

`dashboard.py` 是 legacy minimal dashboard。Phase 73 起，推荐使用本地 React WebUI 工作台：

```bash
cd webui && npm install && npm run build && cd ..
WE_TOGETHER_WEBUI_TOKEN=dev-token \
  python scripts/webui_server.py --root . --host 127.0.0.1 --port 7788
# 浏览器打开 http://127.0.0.1:7788，输入 dev-token
```

局域网访问示例：

```bash
WE_TOGETHER_WEBUI_TOKEN='<换成强 token>' \
  python scripts/webui_server.py --root . --host 0.0.0.0 --port 7788
```

注意：监听 `0.0.0.0` 或局域网 IP 时必须配置 token；静态 SPA 可以加载，但 `/api/*` 全部要求 `Authorization: Bearer <token>`。

## 5. 跑一周自动演化

```bash
python scripts/simulate_week.py --ticks 7 --budget 10
# 归档在 benchmarks/tick_runs/<date>.json（Phase 39 落地）
```

## 6. 作为宿主接入 Claude / Codex

参见 [`docs/hosts/claude-code.md`](hosts/claude-code.md) / [`docs/hosts/claude-desktop.md`](hosts/claude-desktop.md) / [`docs/hosts/codex.md`](hosts/codex.md)。

核心指令：

```bash
claude mcp add we-together -- \
  python $(pwd)/scripts/mcp_server.py --root $(pwd)
```

然后 Claude Code / Codex 的 MCP 里会多出 6 个工具：`we_together_run_turn` / `we_together_graph_summary` / `we_together_scene_list` / `we_together_snapshot_list` / `we_together_import_narration` / `we_together_proactive_scan`，以及两条 resources (`we-together://graph/summary` / `we-together://schema/version`) 和一条 prompt 模板 (`we_together_scene_reply`)。

## 7. 故障排查

- **ImportError**：用 venv 装了吗？`pip install -e .[embedding]` 可加 embedding extras
- **sqlite3.OperationalError: no such table**：忘了 bootstrap
- **MCP Claude 无法识别**：版本 `we-together version` 需 ≥ 0.14.0

## 延伸

- ADR 33 条：`docs/superpowers/decisions/`
- 完整 CLI 列表：`scripts/README.md`
- 当前状态：`docs/superpowers/state/current-status.md`
