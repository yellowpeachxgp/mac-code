<div align="center">

# we together.skill

> *“Remember me ,when it's time to say goodbye.”*

> *“不是把一个人蒸馏成 Skill，而是把一群人蒸馏成 Skill。”*

<br>

把同事蒸馏成 Skill，只得到工作中的 TA。<br>
把自己蒸馏成 Skill，只得到自我镜像。<br>
把前任蒸馏成 Skill，只得到关系中的一面。<br>
但真实的人从来不是单点存在的。<br>

**`we together` 想做的是更完整的事：**<br>
导入多个人物、多种数据来源、多层关系链路，构建一个能够在 Skill 中运行、对话、演化的小型社会图谱。<br>

图恒宇，你在干什么！<br>
我只想……给丫丫一个完整的生命。<br>

[当前状态](#当前状态) · [设计目标](#设计目标) · [核心架构](#核心架构) · [规划中的数据来源](#规划中的数据来源) · [路线图](#路线图) · [参考项目与工具](#参考项目与工具)

</div>

---

## 当前状态

> 当前仓库已完成 **设计基线 + Phase 1 基础骨架实现**，但完整运行时、多平台导入器和多人共演能力仍未全部完成。

### 代码事实更新（2026-04-22）

> 以下为比正文更可靠的**代码事实快照**：
>
> - 本地测试基线：**761 passed, 4 skipped**
> - ADR：**73**
> - 不变式：**28**（代码注册表）
> - Migrations：**21**
> - 向量后端：`flat_python` + **真 `sqlite_vec`** + **真 `faiss`**
> - 联邦：读路径 + **显式开启的写路径** + `curl` 生产 smoke
> - 年运行：`simulate_year` 已有 usage / cost / monthly artifact 审计骨架
> - 多租户：tenant routing 已接入绝大多数高价值 CLI / 宿主 / 运维入口
>
> 当前仓库已经远超“Phase 1 基础骨架”阶段。若需最新全貌，请优先阅读：
> [`docs/superpowers/state/current-status.md`](docs/superpowers/state/current-status.md)
> [`docs/superpowers/decisions/0073-phase-65-70-synthesis.md`](docs/superpowers/decisions/0073-phase-65-70-synthesis.md)
> [`docs/superpowers/state/2026-04-22-phase-65-70-progress.md`](docs/superpowers/state/2026-04-22-phase-65-70-progress.md)

当前已经完成：

- 明确项目定位为 **Skill-first 的社会图谱系统**
- 确定第一阶段锚点场景为 **C：混合小社会**
- 确定采用 **统一社会图谱内核 + 领域投影** 架构
- 确定导入策略为 **默认全自动、自动入图谱**
- 确定演化策略为 **先写事件，再归并入图谱**
- 确定留痕策略为 **Git 式混合模型**
- 确定第一阶段只支持 **局部分支**，不支持整图分叉
- 已落地 Phase 1 内核的首批 Python 工程骨架
- 已落地 SQLite 主库迁移执行器与基础 schema
- 已接入基础枚举 seed 初始化
- `bootstrap` 已能对空白外部 `--root` 自动补齐内置 migrations / seeds，并保持 seed 装载幂等
- 已落地 narration importer、patch 构造器、identity 融合评分基线、runtime retrieval package 基线
- 已落地最小 CLI 工作流：`bootstrap -> create_scene -> import_narration -> build_retrieval_package`
- 已接通群组创建与目录级导入 CLI，可直接构建 group 并批量扫描 `.txt` / `.md` / `.eml`
- narration 导入已能从简单口述文本中自动抽取人物与关系并落入图谱
- 已接通 `text_chat` importer，可从通用聊天文本中抽取发言人、事件与基础关系
- `text_chat` 导入现在会为每条消息补齐 `event_participants`，以支撑后续关系与运行时检索
- 已接通 `auto import` 入口，可在 narration 与 text_chat 之间自动判别
- 已接通 `email` importer，可从 `.eml` 文件中抽取发件人、主题、正文并落图谱
- 已接通文件级 `auto import`，可对本地文本文件与 `.eml` 文件自动分流
- 各导入链已开始落地 `IdentityLink`，图谱中可见跨来源身份映射
- 从 SQLite 生成的 retrieval package 已能回填参与者真实姓名，并带出当前场景下的已知关系
- narration / text_chat 导入已能沉淀共享记忆，并在 retrieval package 中参与当前场景上下文
- email 导入现在也通过推理 patch 生成共享 memory，并把发件人 link 到该 memory
- 已落地最小 `patch applier`，可通过统一入口应用 `create_memory` 与 `update_state` 这类结构化变更
- retrieval package 已开始回填 `current_states`、关系参与者以及群组场景下的 `latent` 激活角色
- 运行时 `response_policy` 已由单纯 scene participant 静态推断，升级为基于显性/潜伏激活的有界收敛
- shared memory 已可在非 group 场景下触发额外 `latent` 角色，形成更接近真实社交语境的有界激活
- active relation 已可在非 group 场景下触发额外 `latent` 角色，且 `strict` activation barrier 会阻断派生激活
- event participants 已可触发额外 `latent` 角色，并纳入 activation budget 统计
- retrieval package 已开始输出可解释的 `activation_budget` / `propagation_depth` / `source_weights` / `event_decay_days` 信息
- retrieval package 现已按 `relation/event/group/memory` 输出来源级 used / blocked 统计
- `patch applier` 已扩到 `link_entities`、`unlink_entities`、`create_local_branch`、`resolve_local_branch`
- `create_local_branch` 已可同时写入 `branch_candidates`
- `patch applier` 已支持 `mark_inactive`，可让 relation / memory 等对象退出当前活跃图谱
- unsupported patch operation 已会留痕为 `failed`
- narration 导入已开始通过推理出的结构化 patch 落 `create_memory` / `link_entities`
- text_chat 导入现已通过推理 patch 构建共享 memory 与 relation link
- narration / text_chat / email 导入现已可通过推理 patch 落部分 `update_state`
- 运行时 `current_states` 已可读到导入阶段推理出的 person / relation 状态
- `auto` / `file` 路由已继承上述 state inference 行为
- runtime 已会忽略被标记为 `inactive` 的 relation / memory
- runtime `safety_and_budget` 已暴露 open local branch 风险数量、branch id 列表与候选总数
- narration / text_chat / email 导入现已开始写入 `snapshot_entities`
- runtime retrieval 已支持按 `scene + input_hash` 写入和命中 `retrieval_cache`，并在 scene / patch 变更后失效
- `build_retrieval_package.py` 已支持 `--input-hash`
- group 相关变更也会触发 retrieval cache 失效
- retrieval build 现已同步刷新 `scene_active_relations`
- retrieval package CLI 在 scene 不存在时已能干净失败并输出明确错误，而不是抛出 traceback
- 文件/目录导入服务已具备清晰失败路径，并会返回 `skipped_count` / `skipped_files`
- 文件/目录导入 CLI 在目标路径缺失时已能干净失败并输出明确错误
- graph summary 已可展示 snapshot/cache/runtime 派生计数
- retrieval cache 已支持默认 TTL（1 小时），CLI 支持 `--cache-ttl` 参数
- graph summary 已扩展 memory/state/patch 计数与 candidate 状态分布
- resolve_local_branch 已可将 selected candidate 的 effect_patches 应用到主图谱
- ingestion 共用 SQL 已抽取为 ingestion_helpers，减少 narration/text_chat/email 三条链路的代码重复
- retrieval package 的 participants 已丰富 persona_summary / style_summary / boundary_summary 人物摘要
- 已闭合对话演化循环：dialogue_service.record_dialogue_event() 记录对话事件 + infer_dialogue_patches() 推理 state/memory patch
- snapshot 已支持 list_snapshots() 历史遍历和 rollback_to_snapshot() 回滚（标记后续 patch + 清理 states）
- patch applier 已支持 update_entity，可对 person/relation/group/memory 做字段级增量更新
- 新增 record_dialogue.py 和 snapshot.py CLI
- patch applier 已支持 merge_entities，可迁移全部外键引用并标记源 person 为 merged
- identity_fusion_service 已新增 find_and_merge_duplicates() 自动发现并合并重复人物
- 新增 merge_duplicates.py CLI
- 对话端到端闭环：process_dialogue_turn() 一键串联 retrieval → record → infer → apply
- 新增 dialogue_turn.py CLI
- scene_service 已支持 close_scene() 和 archive_scene()
- retrieval 已拒绝对非 active 场景的检索请求
- retrieval package 已支持预算裁剪（max_memories / max_relations / max_states）
- retrieval package 已新增 recent_changes 近期变更上下文
- snapshot 已支持 replay_patches_after_snapshot() 回滚后重放
- snapshot CLI 已新增 replay 子命令
- 当前本地全量测试通过：122 passed

Phase 4-7 追加能力（本阶段新增）：

- LLM adapter 抽象（mock/anthropic/openai_compat），核心路径不依赖任何 SDK
- 统一候选中间层（identity_candidates/event_candidates/facet_candidates/relation_clues/group_clues）
- fusion_service：candidate → persons/relations；低置信冲突自动开 local_branch
- LLM 驱动的 narration 抽取（`llm_extraction_service.extract_candidates_from_text`）
- SkillRuntime 协议 + prompt_composer + Claude/OpenAI 双适配器
- chat REPL：retrieval → SkillRequest → LLM → 落图谱
- person facets 按 scene_type 投影（work/life/persona/style/boundary）
- relation 漂移、state 衰减、记忆综合相关性分
- branch 自动解决器；scene 转换推荐器
- self-activation：无输入时的内心独白事件
- 微信 CSV importer 原型（复用 WeChatMsg 导出格式）
- 工程基建：ruff + mypy + e2e_smoke + bench + GitHub Actions CI
- Society C demo 数据集（seed_demo.py）
- 当前本地全量测试通过：201 passed

### Phase 8-12（2026-04-18 v0.8.0 收尾）

- 图谱活化：多场景并发激活 / 记忆凝练 / persona drift / 自发 pair 交互 / 跨场景 echo / 冷记忆归档
- 宿主生态：`SkillRequest.tools` + agent loop + `.weskill.zip` 打包 + 4 个新 adapter（飞书 / LangChain / Coze / MCP）
- 真实世界：iMessage / 微信 db / MBOX / VLM image / 社交 JSON importer + evidence 去重
- 联邦：`external_person_refs` migration 0008 + 本地事件总线 + 裁决 mini-console + 多租户路由
- 硬化：结构化日志 + Prometheus metrics + toml 配置 + schema 漂移检测 + `bench_large.py`
- 当前本地全量测试通过：281 passed
- 详见 [`docs/CHANGELOG.md`](docs/CHANGELOG.md) 与 ADR 0004-0009

### Phase 13-17（2026-04-18 v0.9.0 收尾）

见 CHANGELOG v0.9.0 条目 — 产品化 / eval / 时间维度 / what-if teaser / EXT 收口
- 当前本地全量测试通过：318 passed

### Phase 18-21（2026-04-19 v0.10.0 收尾）

- **生态对接真实化**：MCP stdio server（Claude Code 接入）/ 飞书 bot 绑 `chat_service` / PyPI 发布工程 / Docker CI / Obsidian 双向同步
- **多模态深化**：audio / video / PDF+DOCX / screenshot series importer + pHash / audio fingerprint 近似去重
- **社会模拟完整版**：conflict_predictor / scene_scripter / retire_person / era_evolution（SM-2~5 全落地）
- **Eval 扩展**：condenser eval + persona drift eval + 4 个新 benchmark（condense / persona_drift / society_d / society_work）
- 当前本地全量测试通过：349 passed
- 详见 [`docs/CHANGELOG.md`](docs/CHANGELOG.md) 与 ADR 0015-0019

### Phase 22-24（2026-04-19 v0.11.0 收尾）

- **联邦与互操作**：federation_fetcher（真拉远端） / NATS+Redis 事件总线真后端 / hot_reload 骨架 / CSV+Notion+Signal 迁移 importer / canonical JSON 图谱导入导出 / 联邦协议 RFC
- **真集成 + 生产级**：tests/integration/ 端到端真跑链 / agent_runner tool_use 真多轮循环 / chat_service 支持 tools 参数 / StreamingSkillResponse / wheel 隔离安装验证 / 完整 CI workflow + pre-commit
- **图谱叙事深度**：migration 0011 narrative_arcs + 0012 perceived_memory / narrative_service LLM 聚合章节 / perceived_memory 多视角 / graph_analytics（度/密度/孤立） / associative_recall stub / narrate + analyze CLI
- 当前本地全量测试通过：392 passed
- 详见 [`docs/CHANGELOG.md`](docs/CHANGELOG.md) 与 ADR 0020-0023 + 联邦 RFC

### Phase 25-27（2026-04-19 v0.12.0 收尾）

- **真 LLM 集成**：Anthropic/OpenAI `chat_with_tools` 原生 tool_use / `chat_stream` 流式；agent_runner 自动切 native；observability llm_hooks
- **向量化图谱**：`EmbeddingClient` Protocol + OpenAI / sentence-transformers；migration 0013 embedding 三表；`vector_similarity` 纯 Python cosine/top_k；`associate_by_embedding` 替代 LLM stub；`embed_backfill` CLI
- **规模与真生产**：v0.12.0 wheel 隔离验证；`.github/workflows/publish.yml` tag-push 自动发 PyPI；WAL 模式；Coverage 首版 **90%**；optional extras 扩展（embedding/nats/redis）
- 当前本地全量测试通过：**410 passed**，Coverage 90%
- 详见 [`docs/CHANGELOG.md`](docs/CHANGELOG.md) 与 ADR 0024-0027

### Phase 28-32（2026-04-19 v0.13.0 收尾）

- **向量索引 & 规模化**：`VectorIndex(flat_python)` + 层级 filter / `EmbeddingLRUCache` 批级 dedup / `db/backends.py` SQLite + PG 抽象 / NATS drain 真实现 / `runtime/sqlite_retrieval` 接 `query_text + embedding_client` rerank / cluster embedding-first + Jaccard fallback
- **多智能体社会**：`agents/PersonAgent.from_db / speak / decide_speak`，按 `is_shared + owner_id` 过滤 private vs shared / `turn_taking.next_speaker + orchestrate_multi_agent_turn`（共享底层图谱真理，不变式 #17）
- **主动图谱**：migration 0014 `proactive_prefs` / `proactive_agent` Trigger 三类（anniversary/silence/conflict）+ Intent generate+execute + `check_budget` 预算 + `set_mute/set_consent` 偏好（不变式 #18）
- **元认知**：`contradiction_detector` 两阶段（embedding 配对 + LLM 判定，**只读不写**）+ `eval/contradiction_eval` (P/R) + `benchmarks/contradiction_groundtruth.json`
- **多模态原生**（teaser）：`MultimodalEmbeddingClient` Protocol + `MockMultimodalClient` + `CLIPStubClient`（延迟 import）+ `cross_modal_similarity` top-k
- 当前本地全量测试通过：**436 passed**，ADR 0028-0033
- 详见 [`docs/CHANGELOG.md`](docs/CHANGELOG.md) 与 [`docs/superpowers/plans/2026-04-19-phase-28-32-mega-plan.md`](docs/superpowers/plans/2026-04-19-phase-28-32-mega-plan.md)

### Phase 33-37（2026-04-19 v0.14.0 收尾）

- **真 Skill 宿主（B 支柱提至 8/10）**：SkillRuntime v1 schema 冻结（`SKILL_SCHEMA_VERSION="1"` + `from_dict` 校验）/ MCP server 补齐 resources + prompts 全协议 / OpenAI Assistants demo / verify_skill_package
- **持续演化 Tick 闭环（C 支柱提至 7/10）**：`time_simulator.run_tick / simulate` 编排 decay + drift + proactive + self_activation / tick 后自动 snapshot（不变式 #20）/ `tick_sanity.evaluate` 合理性 / `simulate_week.py` CLI
- **媒体资产落盘**：migration 0015 `media_assets` + `media_refs` / `media_asset_service` hash dedup + visibility / `ocr_service.ocr_to_memory + transcribe_to_event` / `import_image.py` CLI
- **规模化 & 债务清理**：service-inventory（60+ 服务审计，3 条 recall / 3 条 relation 职责不重叠）/ migration-audit / VectorIndex 扩展 `sqlite_vec / faiss` 延迟 import / `bench_scale.py` 10k+ 压测
- 不变式 18 → **20**（新增 #19 schema 版本化 / #20 tick 可回滚）
- 当前本地全量测试通过：**477 passed**，ADR 0034-0039
- 详见 [`docs/CHANGELOG.md`](docs/CHANGELOG.md) 与 [`docs/superpowers/plans/2026-04-19-phase-33-37-mega-plan.md`](docs/superpowers/plans/2026-04-19-phase-33-37-mega-plan.md)

### Phase 38-43（2026-04-19 v0.15.0 收尾）

- **消费就绪（B 9.5/10）**：`scripts/dashboard.py` HTML + `/metrics` Prometheus / `scripts/skill_host_smoke.py` e2e / 三路宿主接入文档 `docs/hosts/{claude-desktop,claude-code,openai-assistants}.md` / `docs/getting-started.md` 5 分钟路径
- **Tick 真归档**：`simulate_week.py --archive` / 首份 baseline `benchmarks/tick_runs/2026-04-18T19-37-40Z.json` / `services/tick_cost_tracker` / `scripts/rollback_tick.py` / `docs/tick-scheduling.md`（crontab + k8s + NATS）
- **神经网格式激活（vision 兑现）**：migration 0016 `activation_traces` / `services/activation_trace_service` (record / query_path / multi_hop_activation BFS+decay / apply_plasticity) / `scripts/activation_path.py` introspection
- **遗忘 + 拆分（对称可逆）**：`services/forgetting_service` (Ebbinghaus 曲线 + archive ↔ reactivate 对称) / `services/entity_unmerge_service` (unmerge_person + 留痕 events)
- **联邦 MVP Read-Only**：`docs/superpowers/specs/federation-protocol-v1.md` / `scripts/federation_http_server.py` + `services/federation_client.py`
- 不变式 20 → **22**（+ #21 激活可 introspect / + #22 写入对称撤销）
- 当前本地全量测试通过：**521 passed**，ADR 0040-0045
- 详见 [`docs/CHANGELOG.md`](docs/CHANGELOG.md) 与 [`docs/superpowers/plans/2026-04-19-phase-38-43-mega-plan.md`](docs/superpowers/plans/2026-04-19-phase-38-43-mega-plan.md)

### Phase 44-50（2026-04-19 v0.16.0 收尾）

- **Plugin / Extension 架构**：`src/we_together/plugins/` 4 Protocol（Importer/Service/Provider/Hook）+ entry_points 发现 + `docs/plugins/authoring.md`（不变式 #23）
- **图谱时间 + 自修复**：migration 0017 `graph_clock` / `services/graph_clock` (fallback datetime.now) / `integrity_audit` / `self_repair`（policy: report_only/propose/auto，仅 safe fix auto）/ `scripts/simulate_year.py`（不变式 #24）
- **多 Agent REPL**：`services/multi_agent_dialogue`（互听 + 打断 + 私聊 + transcript→event）/ `scripts/multi_agent_chat.py`
- **规模化 50-500 人**：`scripts/seed_society_m/l.py`，50 人 retrieval p95 < 1500ms 性能基线
- **联邦安全 v1.1**：Bearer token + rate limit + PII 自动脱敏（email/phone mask）+ `is_exportable` visibility（不变式 #25）
- **i18n + 时序观测**：`runtime/prompt_i18n` (zh/en/ja) / `observability/time_series_svg` SVG sparkline / `observability/webhook_alert`
- 不变式 22 → **25**（#23 plugin registry / #24 graph_clock / #25 跨图谱出口 PII mask）
- 当前本地全量测试通过：**594 passed**，ADR 0046-0052
- 详见 [`docs/CHANGELOG.md`](docs/CHANGELOG.md) 与 [`docs/superpowers/plans/2026-04-19-phase-44-50-mega-plan.md`](docs/superpowers/plans/2026-04-19-phase-44-50-mega-plan.md)

### Phase 51-57（2026-04-19 v0.17.0 收尾）

**维度跃迁**（非加功能）：

- **世界建模升维（C 支柱提至 9.5）**：migration 0018 `objects` + 0019 `places` + 0020 `projects` / `services/world_service` 含 register_object/place/project + active_world_for_scene / 跨类 entity_links / `scripts/world_cli.py`（不变式 #26 世界对象时间范围）
- **AI Agent 元能力**：migration 0021 `agent_drives` + `autonomous_actions` / `services/autonomous_agent` 5 类 drive（connection/curiosity/resolve/obligation/rest）+ decide_action + record 强制来源 / `services/dream_cycle` 压缩 + insight 生成 + learning（不变式 #27 自主可解释）
- **质量与韧性（A 支柱提至 9.8）**：`observability/otel_exporter` NoOp-safe / property-based (Hypothesis optional) + fuzz / `.github/workflows/nightly.yml`
- **社区就绪（B 支柱提至 9.8）**：CONTRIBUTING/COC/SECURITY/GOVERNANCE 四件套 / 3 份对比文档（vs Mem0/Letta/LangMem）/ mkdocs + GitHub 模板 / 20 条 Good First Issues
- **差异化能力**：`services/working_memory` per-scene 短时 buffer / `services/derivation_rebuild` insight + activation 可重建验证（不变式 #28 派生可重建）
- **发布准备**：PyPI checklist / Claude Skills 提交材料 / `scripts/release_prep.py` 自检
- 不变式 25 → **28**（#26 世界对象时间 / #27 Agent 可解释 / #28 派生可重建）
- 当前本地全量测试通过：**638 passed, 2 skipped**，ADR 0053-0059
- 详见 [`docs/CHANGELOG.md`](docs/CHANGELOG.md) 与 [`docs/superpowers/plans/2026-04-19-phase-51-57-mega-plan.md`](docs/superpowers/plans/2026-04-19-phase-51-57-mega-plan.md)

当前核心设计文档：

- [`docs/superpowers/vision/2026-04-05-product-mandate.md`](docs/superpowers/vision/2026-04-05-product-mandate.md)
- [`docs/superpowers/specs/2026-04-05-we-together-core-design.md`](docs/superpowers/specs/2026-04-05-we-together-core-design.md)
- [`docs/superpowers/state/current-status.md`](docs/superpowers/state/current-status.md)
- [`docs/superpowers/specs/2026-04-05-runtime-activation-and-flow-design.md`](docs/superpowers/specs/2026-04-05-runtime-activation-and-flow-design.md)
- [`docs/superpowers/specs/2026-04-05-unified-importer-contract.md`](docs/superpowers/specs/2026-04-05-unified-importer-contract.md)
- [`docs/superpowers/specs/2026-04-05-sqlite-schema-design.md`](docs/superpowers/specs/2026-04-05-sqlite-schema-design.md)
- [`docs/superpowers/specs/2026-04-05-patch-and-snapshot-design.md`](docs/superpowers/specs/2026-04-05-patch-and-snapshot-design.md)
- [`docs/superpowers/specs/2026-04-05-identity-fusion-strategy.md`](docs/superpowers/specs/2026-04-05-identity-fusion-strategy.md)
- [`docs/superpowers/specs/2026-04-05-runtime-retrieval-package-design.md`](docs/superpowers/specs/2026-04-05-runtime-retrieval-package-design.md)
- [`docs/superpowers/specs/2026-04-05-scene-and-environment-enums.md`](docs/superpowers/specs/2026-04-05-scene-and-environment-enums.md)

这意味着：

- 仓库现在适合被公开为 **项目基线与设计仓库**
- 但不应宣称所有采集器、图谱运行时、多人共演都已经完成

---

## 设计目标

`we together` 的目标不是做另一个“单人物蒸馏器”，而是做一个 **可运行、可演化、可追踪** 的社会图谱 Skill。

它最终希望具备以下能力：

- 从多种材料中导入多个人物
- 自动识别跨平台身份并融合成统一人物
- 构建人物之间的工作、生活、亲密、家庭、冲突、合作等多层关系
- 构建群体、场景、事件、记忆、状态等社会化对象
- 在 Skill 对话中支持多人共同回应
- 在新的对话和新导入数据中持续演化图谱
- 以留痕、快照、可逆合并的方式保持工程可控

一句话概括：

> **把“单个数字人格”升级为“一个有关系、有历史、有上下文的小型数字社会”。**

---

## 为什么要做这个

现有很多人物 Skill 都很强，但它们大多停留在“一个人”这一层。

问题在于，真实的人类社会并不是这样工作的：

- 一个人在工作里、亲密关系里、家庭里并不是同一种表现
- 人与人的关系会改变说话方式、决策方式、边界和冲突模式
- 很多记忆并不是“个人记忆”，而是“共享记忆”
- 很多状态并不是“这个人怎么了”，而是“这段关系怎么了”或者“这个群体现在怎么了”

所以 `we together` 不想把人做成孤立节点，而是想从一开始就把：

- 人物
- 关系
- 群体
- 场景
- 事件
- 记忆
- 当前状态

全部放在同一套图谱内核里。

---

## 核心架构

`we together` 当前的核心设计是五层：

### 1. 导入层

负责接入异构数据源，例如：

- 微信
- iMessage
- 飞书
- 钉钉
- Slack
- 邮件
- 图片 / 截图
- 用户口述 / 粘贴文本

### 2. 蒸馏层

负责把原始材料蒸馏为稳定结构，统一吸收以下已有思想：

- `Work`
- `Self Memory`
- `Persona`
- `Relationship Pattern`

### 3. 社会图谱内核

当前已确定的核心对象包括：

- `Person`
- `IdentityLink`
- `Relation`
- `Group`
- `Scene`
- `Event`
- `Memory`
- `State`

### 4. 运行层

负责 Skill 运行时的行为路由：

- 现在该由谁说话
- 哪些人物面应被激活
- 哪些关系、记忆、状态应参与当前回应
- 是否需要多人共同回应

### 5. 演化层

负责图谱的自动更新：

- 对话先写事件
- 再由事件推理 patch
- patch 归并到当前图谱
- 生成快照与历史留痕

---

## 核心设计原则

目前已经确定的工程原则如下：

- **统一图谱内核**：不做“工作系统”和“亲密系统”的双拼架构
- **默认自动化**：默认自动导入、自动匹配、自动入图谱
- **默认可逆**：激进自动融合允许，但必须可拆分、可回滚
- **事件优先**：所有演化先写事件，再改图谱
- **局部分支**：只对未决歧义做局部分支，不做整图分叉
- **摘要是派生视图**：自然语言摘要不能取代结构化主存储

---

## 规划中的数据来源

第一阶段规划支持的输入类型包括：

### 消息与聊天

- 微信聊天记录
- iMessage
- 飞书群聊 / 私聊
- 钉钉消息
- Slack 消息

### 文档与知识材料

- 飞书文档 / Wiki / 多维表格
- 钉钉文档 / 表格
- 邮件 `.eml` / `.mbox`
- Markdown / TXT / PDF

### 视觉与口述材料

- 图片 / 截图
- 直接口述
- 用户补充描述

### 关键区别

与单人物 Skill 不同，`we together` 在导入时不仅要“抽取内容”，还要做：

- **身份对齐**
- **人物融合**
- **关系推理**
- **共享记忆归属**
- **事件影响传播**

---

## 第一阶段路线图

### Phase 0：设计基线

- [x] 建立核心设计文档
- [x] 建立文档目录骨架
- [x] 确定核心实体与演化原则

### Phase 1：图谱内核

- [ ] 明确核心实体的具体存储格式
- [ ] 明确对象连接规则与更新流转
- [ ] 明确局部分支与快照模型
- [ ] 明确运行时检索契约

### Phase 2：统一导入器契约

- [ ] 定义 importer interface
- [ ] 复用参考项目中的现有导入器
- [ ] 统一归一化输出格式
- [ ] 引入身份匹配与人物融合

### Phase 3：Skill 运行时

- [ ] 支持单场景图谱装载
- [ ] 支持多人物回应路由
- [ ] 支持事件先行的自动演化
- [ ] 支持快照和局部分支落盘

### Phase 4：图谱增强

- [ ] 群体长期记忆
- [ ] 共享事件链
- [ ] 关系漂移建模
- [ ] 多源冲突归并

---

## 目前仓库结构

当前仓库重点是文档和设计基线：

```text
.
├── README.md
├── docs/
│   └── superpowers/
│       ├── README.md
│       ├── architecture/
│       ├── decisions/
│       ├── importers/
│       ├── specs/
│       │   └── 2026-04-05-we-together-core-design.md
│       ├── state/
│       │   └── current-status.md
│       └── vision/
└── .gitignore
```

后续实现会围绕这个文档结构推进，而不是把设计继续散落在聊天记录里。

---

## 本地开发启动

当前仓库已经具备最小可运行的 Phase 1 内核骨架。

### 1. 创建虚拟环境

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pytest
```

### 2. 初始化数据库与运行目录

```bash
.venv/bin/python scripts/bootstrap.py
```

执行后会创建：

- `db/main.sqlite3`
- 基础枚举 seed
- `data/raw/`
- `data/derived/`
- `data/snapshots/`
- `data/runtime/`

### 3. 运行测试

```bash
.venv/bin/python -m pytest -q
```

### 4. 运行最小端到端链路

```bash
.venv/bin/python scripts/bootstrap.py --root .
.venv/bin/python scripts/create_scene.py --root . --scene-type private_chat --summary "night chat" --location-scope remote --channel-scope private_dm --visibility-scope mutual_visible --participant person_demo
.venv/bin/python scripts/import_narration.py --root . --text "小王和小李以前是同事，现在还是朋友。" --source-name manual-note
.venv/bin/python scripts/import_text_chat.py --root . --source-name chat.txt --transcript $'2026-04-06 23:10 小王: 今天好累\n2026-04-06 23:11 小李: 早点休息\n'
.venv/bin/python scripts/import_auto.py --root . --source-name auto.txt --text $'2026-04-06 23:10 小王: 今天好累\n2026-04-06 23:11 小李: 早点休息\n'
.venv/bin/python scripts/import_email_file.py --root . --file ./sample.eml
.venv/bin/python scripts/import_file_auto.py --root . --file ./sample.txt
.venv/bin/python scripts/build_retrieval_package.py --root . --scene-id <scene_id> --cache-ttl 3600
.venv/bin/python scripts/record_dialogue.py --root . --scene-id <scene_id> --user-input "你好" --response-text "你好呀" --speaker person_demo
.venv/bin/python scripts/dialogue_turn.py --root . --scene-id <scene_id> --user-input "你好" --response-text "你好呀" --speaking-person-ids person_demo
.venv/bin/python scripts/merge_duplicates.py --root .
.venv/bin/python scripts/snapshot.py --root . list
.venv/bin/python scripts/snapshot.py --root . rollback --snapshot-id <snapshot_id>
.venv/bin/python scripts/snapshot.py --root . replay --snapshot-id <snapshot_id>
.venv/bin/python scripts/graph_summary.py --root .
```

---

## 参考项目与工具

`we together` 的方向并不是凭空提出的，它明确受以下项目启发，并计划复用其中可迁移的导入与蒸馏能力。

### 核心参考项目

- [`titanwings/colleague-skill`](https://github.com/titanwings/colleague-skill)
  - 提供了“工作能力 + 人物性格”的双层思路
  - 提供了飞书 / 钉钉 / Slack / 邮件等工作型导入能力

- [`notdog1998/yourself-skill`](https://github.com/notdog1998/yourself-skill)
  - 提供了“自我记忆 + 人格模型”的双层思路
  - 提供了微信、QQ、图片、社交内容、自我口述等个人型材料处理思路

- [`titanwings/ex-skill`](https://github.com/titanwings/ex-skill)
  - 提供了“关系人格建模”的强关系视角
  - 提供了微信 / iMessage / 关系行为模式 / 冲突链等强情境建模思路

### 可能会用到的数据提取参考工具

以下工具不是本项目代码的一部分，但很可能继续作为导入链路中的参考或兼容目标：

- [`LC044/WeChatMsg`](https://github.com/LC044/WeChatMsg)
  - 微信聊天记录导出

- [`xaoyaoo/PyWxDump`](https://github.com/xaoyaoo/PyWxDump)
  - 微信数据库解密与导出

- [`greyovo/留痕`](https://github.com/greyovo/留痕)
  - macOS 微信聊天记录导出

- `Feishu MCP / Feishu Open Platform`
  - 飞书文档、Wiki、消息、表格读取

- `DingTalk Open Platform`
  - 钉钉文档、用户、表格等导入

- `Slack SDK / Slack API`
  - Slack 消息与用户信息导入

### 参考原则

`we together` 会尽量复用这些项目和工具的“可迁移能力”，但不会直接把三套单人物架构粗暴拼接。  
本项目的重点是把它们统一到一个 **社会图谱内核** 之上。

---

## 项目状态说明

如果你现在来到这个仓库，请把它理解为：

- 一个已经有明确架构方向的项目
- 一个正在建立工程化基线的仓库
- 一个准备从“单人物 Skill”走向“多人社会图谱 Skill”的起点

但不要把它误解为：

- 所有功能已经实现
- 所有导入器已经接通
- 多人共演运行时已经完成

---

## 写在最后

“数字人格”这件事走到最后，真正难的从来不是让一个人说得像不像。  
真正难的是：

- 让一个人放到不同关系里依然像他自己
- 让几个人放在一起时，彼此之间的历史和张力都成立
- 让这个系统在新的对话里持续变化，而不是每次都从头演戏

`we together` 想做的，就是这一步。

不是一个人。

是**一群彼此有关联的人，作为一个可运行的数字社会，一起存在。**
