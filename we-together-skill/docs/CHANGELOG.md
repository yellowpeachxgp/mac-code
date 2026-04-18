# CHANGELOG

本 CHANGELOG 记录 we-together-skill 的阶段性里程碑。

## v0.8.0 — 2026-04-18

一次性无人值守推进完成五个大目标：Phase 8-12。281 passed，新增 8 个 ADR。

### Phase 8 — 图谱活化（Neural Mesh）

- NM-1 多场景并发激活（`runtime/multi_scene_activation`）
- NM-2 记忆聚类 + LLM 凝练（`memory_cluster_service` / `memory_condenser_service`）
- NM-3 Persona drift（`persona_drift_service`）
- NM-4 自发 pair 交互（`self_activate_pair_interactions`）
- NM-5 跨场景 echo（retrieval `cross_scene_echoes`）
- NM-6 冷记忆归档 + 恢复（migration 0007 + `memory_archive_service`）

### Phase 9 — 宿主生态

- HE-1 `SkillRequest.tools` 跨宿主抽象
- HE-2 agent loop（tool_call/result 循环 + events 链）
- HE-3 `.weskill.zip` 打包分发（`packaging/skill_packager`）
- HE-4/5/6/7 飞书 / LangChain / Coze / MCP adapter（纯函数）

### Phase 10 — 真实世界数据化

- RW-1 iMessage 本地 chat.db importer
- RW-2 微信明文 sqlite importer
- RW-3 邮件 MBOX 批处理
- RW-4 VLM image importer + `VisionLLMClient`
- RW-5 社交 JSON dump importer
- RW-6 `evidence_dedup_service` 内容 hash 去重

### Phase 11 — 联邦与协同

- FE-1 migration 0008 `external_person_refs` + `federation_service`
- FE-2 本地 jsonl 事件总线（`event_bus_service`）
- FE-3 裁决 mini-console（stdlib http.server + bearer token）
- FE-4 多租户路径路由（`tenant_router`）

### Phase 12 — 生产化硬化

- HD-1 结构化日志 + trace_id（`observability/logger`）
- HD-2 Metrics + Prometheus 导出
- HD-3 toml 配置系统
- HD-4 `WeTogetherError` 异常层级
- HD-5 `bench_large.py` 大规模压测
- HD-6 schema version 漂移检测
- HD-8 `patch_batch` 批量应用
- HD-9 retrieval cache 预热

### 其他

- ADR 0004-0009 共 6 个新决策文件
- current-status.md 按 Phase 收尾同步（216 → 234 → 254 → 260 → 268 → 281）

## v0.7.0 — 2026-04-17 之前

见 `docs/superpowers/state/current-status.md` Phase 1-7 段落。
