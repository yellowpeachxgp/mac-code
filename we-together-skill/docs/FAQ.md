# FAQ

## 我需要 LLM API key 才能跑吗？

不需要。默认 `WE_TOGETHER_LLM_PROVIDER=mock` 使用 MockLLMClient，所有功能都能用（包括 memory condenser / persona drift / event causality / what-if）。要接入真实 LLM 时设置：

```bash
export WE_TOGETHER_LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# 或 OpenAI-compat（Deepseek / 其它）
export WE_TOGETHER_LLM_PROVIDER=openai_compat
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://...
```

## 怎么部署？

三条路：

1. **pip**: `pip install -e .` → `we-together version`
2. **Docker**: `docker compose -f docker/docker-compose.yml up --build`
3. **直接从源**: `.venv/bin/python scripts/<xxx>.py --root ...`

## 我的微信/iMessage/邮件怎么导入？

| 来源 | 命令 |
|---|---|
| 文本 narration | `we-together ingest narration --text '...'` |
| 结构化对话 | `we-together ingest text-chat --file ...` |
| 单 .eml | `we-together import-email --file ...` |
| MBOX 批量 | 用 `importers/mbox_importer.import_mbox` 直接调（CLI 待接） |
| iMessage chat.db | 用 `importers/imessage_importer` 调（CLI 待接） |
| 微信 明文 db | 用 `importers/wechat_db_importer` 调（加密解密请用外部工具） |

## 出错了去哪看？

1. `scripts/graph_summary.py --root .` 看图谱当前状态
2. `we-together snapshot list --root .` 看快照链
3. `we-together branch-console --root .` 看 open local_branches

## Eval 分数下降了怎么办？

```bash
we-together eval-relation --root . --baseline eval/baseline.json
# exit 3 表示有回归，报告会打印哪些 metric 跌超 tolerance
```

排查思路：先看 `missing_pairs`（应该推出但没推出的）和 `spurious_pairs`（推多了的），再去看具体的 fuse_all / relation_drift 行为。

## 怎么在 Claude Code 里用？

见 `examples/claude-code-skill/README.md`。简言之：打包 `.weskill.zip` → 放到 Claude Code 的 skills 目录。

## 怎么在飞书里用？

见 `examples/feishu-bot/README.md`。启动 `server.py` + ngrok 暴露 webhook。

## 数据会被上传到哪里吗？

**不会**。所有存储都在本地 SQLite（`<root>/db/main.sqlite3`）。LLM 调用只有在用户明确配置 `WE_TOGETHER_LLM_PROVIDER=anthropic/openai_compat` 且提供 API key 时才发生；mock 模式完全离线。
