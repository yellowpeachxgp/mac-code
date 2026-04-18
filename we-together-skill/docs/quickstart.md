# Quickstart — 5 分钟从零到跑起一个小社会图谱

> 适用于 we-together-skill v0.9.0 及以上。

## 0. 环境

- Python 3.11+
- 可选：Docker（见 `docker/README.md`）

## 1. 安装

```bash
git clone https://github.com/yellowpeach/we-together-skill
cd we-together-skill
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

或 pip 包（未来 PyPI 发布后）：

```bash
pip install we-together-skill
```

## 2. 初始化 + 灌 demo 数据

```bash
we-together bootstrap --root ./data
we-together seed-demo --root ./data
we-together graph-summary --root ./data
```

输出应包含：`person_count: 8`, `relation_count: 8`, `scene_count: 3` 等字段。

## 3. 查看时间线

```bash
# 找一个 person_id（假设叫 alice_id）
we-together timeline --root ./data --person-id <alice_id>
```

输出：近 20 个事件、活跃关系、persona_summary 演变（Phase 15 能力）。

## 4. 跑一次对话

```bash
we-together build-pkg --root ./data --scene-id <work_scene_id>
we-together dialogue-turn --root ./data --scene-id <work_scene_id> --input "大家下周有安排吗？"
```

## 5. 观察图谱变化

```bash
we-together snapshot list --root ./data
we-together snapshot replay --root ./data --target <snapshot_id>
we-together graph-summary --root ./data
```

## 6. 做一次维护（可选）

```bash
we-together daily-maint --root ./data --skip-llm   # 跳过 LLM 步骤
```

## 7. What-if 社会模拟（teaser, Phase 17）

```bash
we-together what-if --root ./data --scene-id <work_scene_id> --hypothesis "Bob 换团队"
```

## 常见问题

### 我没有 LLM API key 怎么办？

默认 `WE_TOGETHER_LLM_PROVIDER=mock` 就能跑完整个链路（使用 MockLLMClient）。所有功能测试都用 mock，所以真实 API key 不是必需的。

### db 已初始化了，能不能换目录？

`--root` 参数指向的目录就是数据目录。换一个目录重新跑 `bootstrap` 即可，多租户可用 `WE_TOGETHER_TENANT_ID` 环境变量。

### 如何升级 schema？

已应用 migration 的 db 启动时会走 `check_schema_version`；如果本地 migration 目录少了已应用版本的文件，会抛 `SchemaVersionError`。**升级时增量加 migration 文件**，不要删除旧文件。

### 测试能跑过吗？

```bash
pytest -q
```

v0.9.0 基线：**288 passed**（或更高）。

## 下一步阅读

- [`docs/onboarding.md`](onboarding.md) — 交互式 onboard 细节
- [`docs/CHANGELOG.md`](CHANGELOG.md) — 历史版本
- [`docs/superpowers/state/current-status.md`](superpowers/state/current-status.md) — 能力边界
- [`examples/claude-code-skill/`](../examples/claude-code-skill/) — Claude Code 接入样例
- [`examples/feishu-bot/`](../examples/feishu-bot/) — 飞书机器人样例
- [`docker/README.md`](../docker/README.md) — Docker 一键部署
