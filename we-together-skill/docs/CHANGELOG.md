# CHANGELOG

本 CHANGELOG 记录 we-together-skill 的阶段性里程碑。

## v0.10.0 — 2026-04-19

第三轮一次性无人值守推进：Phase 18-21。349 passed (+31)，新增 5 个 ADR（0015-0019）。

### Phase 18 — 生态对接真实化

- MCP stdio server (`scripts/mcp_server.py`) 接 Claude Code
- 飞书 bot 绑真实 `chat_service.run_turn`（examples/feishu-bot）
- PyPI 发布工程：MANIFEST.in / build_wheel.sh / publish.md checklist
- `.github/workflows/docker.yml`
- Obsidian md 双向同步（importer + exporter）

### Phase 19 — 多模态深化

- `AudioTranscriber` Protocol + MockAudioTranscriber + WhisperTranscriber stub
- `audio_importer` / `video_importer` / `document_importer` / `screenshot_series_importer`
- 多模态 dedup: pHash + audio fingerprint + 汉明距离近似去重
- `benchmarks/multimodal_groundtruth.json`

### Phase 20 — 社会模拟完整版

- `simulation/conflict_predictor` (SM-2)
- `simulation/scene_scripter` (SM-3)
- `services/retire_person_service` (SM-4)
- `simulation/era_evolution.simulate_era` (SM-5)
- `scripts/simulate.py` 合一 CLI

### Phase 21 — Eval 扩展

- `eval/condenser_eval` + `eval/persona_drift_eval`
- 4 个新 benchmark: condense / persona_drift / society_d / society_work
- Eval 结果统一形状 `{benchmark, total, passed, pass_rate, cases}`

### v0.9.1 — 热修

- eval groundtruth core_type 对齐 seed_society_c（`work/intimacy/friendship/...`），precision/recall/f1 从 0.0 → 1.0
- what-if mock 模式下给占位 prediction + `mock_mode` 字段
- `eval/baseline.json` 首版真实基线

### ADR 新增

- 0015: Phase 18 生态对接
- 0016: Phase 19 多模态
- 0017: Phase 20 社会模拟
- 0018: Phase 21 eval 扩展
- 0019: Phase 18-21 综合 + 不变式扩展至 12 条

---

## v0.9.0 — 2026-04-18

第二轮一次性无人值守推进：Phase 13-17。318 passed (+37)，新增 5 个 ADR（0010-0014）。

### Phase 13 — 产品化与 Onboarding

- `we-together` pip 包 + 统一 CLI (`src/we_together/cli.py`)
- Docker 多阶段 + compose（app+metrics+branch-console） + README
- `services/onboarding_flow` 5 步状态机 + `scripts/onboard.py --dry-run`
- `examples/claude-code-skill/` + `examples/feishu-bot/`（stdlib webhook）
- `docs/quickstart.md` 5 分钟从零到跑

### Phase 14 — 评估与质量

- `benchmarks/society_c_groundtruth.json`
- `src/we_together/eval/`（groundtruth_loader / metrics / relation_inference / llm_judge / regression）
- `scripts/eval_relation.py` + baseline / regression 门禁

### Phase 15 — 时间维度

- migration 0009 `persona_history` + 0010 `event_causality`
- `services/persona_history_service` / `relation_history_service` / `event_causality_service` / `memory_recall_service`
- `runtime_retrieval` 新增 `as_of` 参数（跳过 cache）
- `scripts/timeline.py` + `scripts/relation_timeline.py`

### Phase 17 — What-if Teaser

- `src/we_together/simulation/what_if_service`（LLM 推演，不改图谱）
- `scripts/what_if.py`

### EXT 收口

- `services/patch_transactional.apply_patches_transactional`（事务 ROLLBACK）
- `services/rbac_service`（Role/Scope/TokenRegistry）
- `observability/sinks`（StdoutSink + OTLPStubSink + Protocol）
- `event_bus_service` 加 LocalFileBackend + NATSStubBackend

### ADR 新增

- 0010: Phase 13 产品化
- 0011: Phase 14 评估
- 0012: Phase 15 时间维度
- 0013: Phase 17 what-if teaser
- 0014: Phase 13-17 综合 + 不变式扩展至 10 条

---

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
