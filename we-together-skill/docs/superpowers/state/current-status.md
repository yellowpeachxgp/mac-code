# 当前状态

日期：2026-04-18

当前已完成：

- 已确立产品最高约束：严格工程化、通用型 Skill、数字赛博生态圈目标
- 明确项目定位为 Skill-first 的社会图谱系统
- 选定第一阶段锚点场景为 `C：混合小社会`
- 确定采用统一社会图谱内核，而不是工作/亲密双系统拼接
- 确定关系模型为“核心维度固定 + 自定义扩展 + 自然语言摘要”
- 确定导入策略为默认全自动、自动入图谱
- 确定身份融合策略为激进自动融合，但必须可逆、可追溯
- 确定演化策略为“先写事件，再归并入图谱”
- 确定留痕模型为 Git 式混合结构
- 确定第一阶段只支持局部分支，不支持整图分叉
- 确定运行时采用“有界激活传播模型”
- 确定环境参数采用“核心维度固定 + 自定义扩展”
- 确定主存储采用 SQLite 与文件系统的混合模型
- 确定 importer 采用“统一证据层 + 候选层”的输出契约
- 确定 SQLite 为规范主对象与留痕对象的核心存储层
- 确定 Event / Patch / Snapshot 为第一阶段的标准演化链
- 确定默认激进融合、底层可逆的 identity 融合策略
- 确定运行时采用固定结构的检索包
- 确定 Scene 与环境参数采用“核心枚举 + 自定义扩展”
- 已补齐启动与迁移方案
- 已补齐 importer 复用矩阵
- 已写入 Phase 1 架构基线 ADR
- 已生成 Phase 1 implementation plan
- 已落地首批 Python 工程骨架
- 已落地 SQLite 主库迁移执行器与基础 schema
- 已接入基础枚举 seed 初始化
- `bootstrap` 已能对空白外部 `--root` 自动补齐内置 migrations / seeds，并保持 seed 装载幂等
- 已落地 narration importer、patch 构造器、identity 融合评分基线与 runtime retrieval package 基线
- 已落地最小 CLI 端到端链路：bootstrap / create_scene / import_narration / build_retrieval_package
- 已接通群组创建与目录级导入 CLI，可直接构建 group 并批量扫描 `.txt` / `.md` / `.eml`
- narration 导入已能自动抽取简单人物与关系并落图谱
- 已接通 text_chat importer，可从通用聊天文本中抽取人物、事件与基础关系
- text_chat 导入已能为每条消息写入 `event_participants`
- 已接通 auto import 入口，可在 narration 与 text_chat 之间自动判别
- 已接通 email importer，可从 `.eml` 文件中抽取发件人、主题、正文并落图谱
- 已接通文件级 auto import，可对文本文件与 `.eml` 自动分流
- narration / text_chat / email 导入已开始落地 identity_links
- retrieval package 已能回填参与者姓名并带出场景下已知关系
- narration / text_chat 导入已能沉淀共享记忆并写入 retrieval package
- email 导入现在也通过推理 patch 生成共享 memory，并把发件人链接到该 memory
- 已落地最小 patch applier，可统一应用 memory/state 类 patch
- text_chat 导入已能生成更具体的互动关系摘要
- retrieval package 已能回填关系参与者、`current_states` 与群组场景下的 `latent` 激活成员
- 运行时 `response_policy` 已由静态 scene participant 推断升级为基于显性/潜伏激活的有界收敛
- shared memory 已可在非 group 场景下触发额外 `latent` 激活
- active relation 已可在非 group 场景下触发额外 `latent` 激活，且 `strict` activation barrier 会阻断派生激活
- event participants 已可触发额外 `latent` 激活，并纳入 activation budget 统计
- retrieval package 已开始输出可解释的 `activation_budget` / `propagation_depth` / `source_weights` / `event_decay_days` 信息
- retrieval package 现已按 `relation/event/group/memory` 输出来源级 used / blocked 统计
- create_local_branch 已可同时写入 branch_candidates
- patch applier 已扩到 `link_entities`、`unlink_entities`、`create_local_branch`、`resolve_local_branch`、`mark_inactive`
- unsupported patch operation 已会落痕为 `failed`
- narration 导入已开始通过推理出的结构化 patch 落 `create_memory` / `link_entities`
- text_chat 导入现已通过推理 patch 构建共享 memory 与 relation link
- narration / text_chat / email 导入现已可通过推理 patch 落部分 `update_state`
- 运行时 `current_states` 已可读到导入阶段推理出的 person / relation 状态
- `auto` / `file` 路由已继承上述 state inference 行为
- runtime 已会忽略被标记为 `inactive` 的 relation / memory
- runtime `safety_and_budget` 已暴露 open local branch 风险数量、branch id 列表与候选总数
- narration / text_chat / email 导入现已开始写入 `snapshot_entities`
- runtime retrieval 已支持按 `scene + input_hash` 写入和命中 `retrieval_cache`，并在 scene / patch 变更后失效
- build_retrieval_package CLI 已支持 `--input-hash`
- group 相关变更也会触发 retrieval cache 失效
- retrieval build 现已同步刷新 `scene_active_relations`
- retrieval package CLI 在 scene 不存在时已能干净失败并输出明确错误
- 文件/目录导入服务已具备清晰失败路径，并会返回 `skipped_count` / `skipped_files`
- 文件/目录导入 CLI 在目标路径缺失时已能干净失败并输出明确错误
- graph summary 已可展示 snapshot/cache/runtime 派生计数
- retrieval cache 已支持默认 TTL（DEFAULT_CACHE_TTL_SECONDS = 3600），不传 TTL 时自动使用默认值
- build_retrieval_package CLI 已支持 `--cache-ttl` 参数
- graph summary 已扩展 memory_count、state_count、patch_count 与 candidate_status_distribution 字段
- resolve_local_branch 已可读取 selected candidate 的 payload_json 中的 effect_patches，并逐个应用到主图谱
- ingestion 共用 SQL 已抽取为 ingestion_helpers.py（persist_import_job / persist_raw_evidence / persist_patch_record / persist_snapshot_with_entities）
- ingestion_service.py 和 email_ingestion_service.py 已调用共用 helper，消除重复代码
- retrieval package 的 participants 已丰富 persona_summary / style_summary / boundary_summary 人物摘要
- 对话演化循环已闭合：dialogue_service.record_dialogue_event() 将对话写为 dialogue_event + snapshot
- infer_dialogue_patches() 从对话内容推理 scene mood state 和多人共享 memory
- 对话 → Event → Patch → Graph State 的完整演化链已可运行
- snapshot 已支持 list_snapshots() 历史遍历和 rollback_to_snapshot() 回滚
- rollback 会标记后续 patch 为 rolled_back、删除后续 states 和 snapshots、清空 retrieval cache
- patch applier 已支持 update_entity，可对 person/relation/group/memory 做字段级增量更新
- 新增 record_dialogue.py CLI（记录对话事件）和 snapshot.py CLI（list / rollback）
- patch applier 已支持 merge_entities，可迁移 identity_links / event_participants / memory_owners / scene_participants / group_members 并标记源 person 为 merged
- identity_fusion_service 已新增 find_and_merge_duplicates()，可自动发现同名重复人物并合并
- 新增 merge_duplicates.py CLI（自动合并重复人物）
- 对话端到端闭环：process_dialogue_turn() 一键串联 retrieval → record_event → infer_patches → apply
- 新增 dialogue_turn.py CLI（一键对话处理）
- scene_service 已支持 close_scene() 和 archive_scene()，场景可关闭和归档
- retrieval 已拒绝对非 active 场景的检索请求（抛出 ValueError）
- retrieval package 已支持预算裁剪：max_memories / max_relations / max_states 参数
- build_retrieval_package CLI 已新增 --max-memories / --max-relations / --max-states
- retrieval package 已新增 recent_changes 字段，展示最近已应用的 patch 摘要
- retrieval package 已新增 max_recent_changes 参数控制返回条数
- snapshot 已支持 replay_patches_after_snapshot() 回滚后重放
- snapshot CLI 已新增 replay 子命令
- 当前本地全量测试通过：122 passed

## Phase 4 — 让蒸馏变真（已完成）

- 新增 migration 0006：identity_candidates / event_candidates / facet_candidates / relation_clues / group_clues
- candidate_store 统一写入 API，confidence 分层（high/medium/low）
- LLM adapter 抽象（`src/we_together/llm/`）：Protocol + mock/anthropic/openai_compat providers
- factory 按 `WE_TOGETHER_LLM_PROVIDER` 切换；核心路径不直接 import SDK
- fusion_service：candidate → persons / identity_links / relations，所有变更走 patch
- 低置信 identity 冲突自动开 local_branch（含 merge/new 两候选），不直接合并
- llm_extraction_service：LLM 驱动的 narration 候选抽取（内部创建 evidence + candidates）
- ADR 0002 定稿 LLM-in-the-loop 五个决策

## Phase 5 — 让 Skill 变通用（已完成）

- runtime/skill_runtime.py：SkillRequest / SkillResponse 数据结构（平台无关）
- runtime/prompt_composer.py：retrieval_package → {system, messages}（含参与者/关系/记忆/状态/recent_changes/policy 七段）
- adapters/claude_adapter + adapters/openai_adapter：两套宿主语义等价
- chat_service.run_turn：端到端 retrieval → adapter → LLM → 图谱演化
- scripts/chat.py REPL，支持 /who /pkg /switch /exit

## Phase 6 — 让图谱变活（已完成）

- patch_applier 新增 upsert_facet，复用现有 person_facets 表
- retrieval 按 scene.scene_type 投影 facets（SCENE_FACET_POLICY）
- relation_drift_service：按 event 窗口重算 strength（+/-0.03..0.05），落 update_entity patch
- state_decay_service：linear/exponential/step/none 四种 decay_policy，低置信标记 deactivated
- _build_relevant_memories：综合分 = type_weight × relevance × confidence × recency × overlap × scene_match
- branch_resolver_service：显著占优的 branch 自动 resolve
- scene_transition_service：给出下一场景候选（切 type / 扩 group / 引入关系对方）

## Phase 7 — 生态自转（进行中）

- importers/wechat_text_importer.py：CSV → candidate 层，fusion 后创建 persons/relations
- self_activation_service：无输入时生成 self_reflection_event，受 daily_budget 约束

## 工程基建

- pyproject.toml 加入 ruff + mypy；scripts/lint.sh 本地工程化检查
- scripts/e2e_smoke.sh：10 步端到端链路（bootstrap→seed→retrieve→turn→snapshot→drift→decay→merge→summary）
- scripts/bench.py：build_retrieval cold/warm + apply_state_patch 延迟百分位
- .github/workflows/ci.yml：install + ruff + mypy + pytest + e2e smoke
- scripts/seed_demo.py：Society C 小社会（8 人 × 8 关系 × 3 场景）

- 当前本地全量测试通过：216 passed

## Phase 7 收尾增补（2026-04-18）

- person_activity_service：聚合 person 近期活动（persona/facets/events/relations/memories/scenes）为单份 profile，供 debug / skill 展示（Slice C1）
- runtime_retrieval 新增 `debug_scores` 开关，memory 附带 `score_breakdown` 暴露 base_type / relevance / confidence / recency / overlap / scene_factor 中间量；debug 模式跳过缓存读写（Slice W2）
- relation_conflict_service：按窗口内 relation 相关 events 做 sentiment 分析，统计 ± 反转次数，识别"正负情绪反复震荡"的冲突关系；emit_memory=True 时生成 `conflict_signal` 低置信 memory（Slice U2）
- `docs/superpowers/importers/2026-04-18-importer-status-matrix.md`：已实现层 importer 契约矩阵（8 类 importer 的 patch 类型、是否直接落主图、fuse_all 升级路径、retrieval 可见性差异）

当前主设计稿：

- [2026-04-05-we-together-core-design.md](../specs/2026-04-05-we-together-core-design.md)
- [2026-04-05-runtime-activation-and-flow-design.md](../specs/2026-04-05-runtime-activation-and-flow-design.md)
- [2026-04-05-unified-importer-contract.md](../specs/2026-04-05-unified-importer-contract.md)
- [2026-04-05-sqlite-schema-design.md](../specs/2026-04-05-sqlite-schema-design.md)
- [2026-04-05-patch-and-snapshot-design.md](../specs/2026-04-05-patch-and-snapshot-design.md)
- [2026-04-05-identity-fusion-strategy.md](../specs/2026-04-05-identity-fusion-strategy.md)
- [2026-04-05-runtime-retrieval-package-design.md](../specs/2026-04-05-runtime-retrieval-package-design.md)
- [2026-04-05-scene-and-environment-enums.md](../specs/2026-04-05-scene-and-environment-enums.md)
- [2026-04-05-phase-1-bootstrap-and-migrations.md](../architecture/2026-04-05-phase-1-bootstrap-and-migrations.md)
- [2026-04-05-importer-reuse-matrix.md](../importers/2026-04-05-importer-reuse-matrix.md)
- [2026-04-05-phase-1-kernel-implementation.md](../plans/2026-04-05-phase-1-kernel-implementation.md)
- [0001-phase-1-architecture-baseline.md](../decisions/0001-phase-1-architecture-baseline.md)
- [2026-04-05-product-mandate.md](../vision/2026-04-05-product-mandate.md)

## Phase 8 — 图谱活化（Neural Mesh，已完成）

- runtime/multi_scene_activation.build_multi_scene_activation 聚合多个 active scene 的 activation_map（NM-1）
- memory_cluster_service.cluster_memories + memory_condenser_service.condense_memory_clusters：LLM 驱动的记忆聚类与凝练（NM-2）
- persona_drift_service.drift_personas：窗口 events → LLM 重新蒸馏 persona/style_summary（NM-3）
- self_activation_service.self_activate_pair_interactions：pair 自发交互事件 + 双人 shared_memory（NM-4）
- runtime_retrieval 新增 cross_scene_echoes：其他 active scene 的高权重事件回响（NM-5）
- migration 0007 cold_memories / cold_memory_owners + memory_archive_service：归档 + 恢复（NM-6）
- daily_maintenance.py 扩展至 6 步（原 4 步 + persona_drift + memory_condense），--skip-llm 开关
- ADR 0004 定稿 Phase 8 六个决策
- 当前本地全量测试通过：234 passed

## Phase 9 — 宿主生态（Host Ecosystem，已完成）

- SkillRequest.tools 跨宿主抽象；Claude 透传、OpenAI 翻译为 function schema（HE-1）
- agent_loop_service.run_turn_agent：tool_call→tool_result 循环，每步落 events 表（HE-2）
- packaging/skill_packager：pack/unpack .weskill.zip + manifest（HE-3）
- 四个新宿主 adapter（纯函数，无 SDK）：飞书（+ 签名校验）/ LangChain / Coze / MCP（HE-4/5/6/7）
- scripts/agent_chat.py 内置 graph_summary / retrieval_pkg 工具示例
- ADR 0005 定稿 Phase 9 四个决策
- 当前本地全量测试通过：254 passed

## Phase 10 — 真实世界数据化（Real-world Ingestion，已完成）

- imessage_importer（macOS chat.db 只读）/ wechat_db_importer（明文 sqlite）/ mbox_importer（RW-1/2/3）
- vision provider + image_importer（VLM 图片描述链路，含 AnthropicVisionClient 延迟 SDK）（RW-4）
- social_importer（通用 JSON dump: 关注/被关注/帖子/@提及）（RW-5）
- evidence_dedup_service + evidence_hash_registry 辅助表（RW-6）
- ADR 0006 定稿 Phase 10 四个决策
- 当前本地全量测试通过：260 passed

## Phase 11 — 联邦与协同（Federation，已完成）

- migration 0008 external_person_refs + federation_service（register/list/eager）（FE-1）
- event_bus_service: jsonl 队列 + cursor，publish/drain/peek 无外部依赖（FE-2）
- scripts/branch_console.py: stdlib http.server，GET /branches + POST /resolve + bearer token（FE-3）
- tenant_router: db_path 按 tenant_id 路由，default 保持向后兼容（FE-4）
- ADR 0007 定稿 Phase 11 四个决策
- 当前本地全量测试通过：268 passed

## Phase 12 — 生产化硬化（Hardening，已完成）

- observability/logger: stdlib + contextvars trace_id + JSON 格式（HD-1）
- observability/metrics: 内存 counter/gauge + Prometheus 文本导出（HD-2）
- config/loader: `we_together.toml` + env 两级合并，WeTogetherConfig dataclass（HD-3）
- errors.py: WeTogetherError 六级层级（HD-4）
- scripts/bench_large.py: 批量 person 插入 + 冷/热检索延迟 p50/p95（HD-5）
- db/schema_version: bootstrap 预检漂移 → SchemaVersionError（HD-6）
- services/patch_batch: apply_patches_bulk 顺序批处理（HD-8）
- services/cache_warmer: warm_retrieval_cache 预热 active scenes（HD-9）
- ADR 0008 定稿 Phase 12 九个决策
- ADR 0009 综合架构总结 + 未来不变式（5 条）
- docs/CHANGELOG.md 首版 + v0.8.0 条目
- docs/superpowers/plans/2026-04-18-phase-8-12-mega-plan.md 归档
- scripts/README.md CLI 索引
- 当前本地全量测试通过：281 passed

## Phase 13 — 产品化与 Onboarding（已完成）

- pyproject: 完整 metadata + 4 个 optional deps 分组 + console_scripts entry_point
- src/we_together/cli.py 统一 CLI 入口，20+ 子命令 dispatch
- docker/Dockerfile 多阶段 + docker-compose.yml (app + metrics:9100 + branch-console:8765) + .dockerignore + docker/README.md
- services/onboarding_flow 5 步状态机 + scripts/onboard.py --dry-run
- examples/claude-code-skill/（SKILL.md 专版 + use_cases.md + README）+ examples/feishu-bot/（stdlib webhook server + 签名校验 + url_verification challenge）
- docs/quickstart.md: 5 分钟从零到跑
- ADR 0010 定稿 Phase 13 五个决策
- 当前本地全量测试通过：288 passed

## Phase 14 — 评估与质量（已完成）

- benchmarks/society_c_groundtruth.json（8 人 / 4 期望关系 / 3 期望场景）
- src/we_together/eval/：groundtruth_loader / metrics / relation_inference / llm_judge / regression
- scripts/eval_relation.py + --save-baseline + --baseline 回归门禁（exit 3 on regression）
- ADR 0011 定稿 Phase 14 六个决策
- 当前本地全量测试通过：298 passed

下一步建议：

- 接真实平台 importer 的生产级版本（飞书/Slack/iMessage/邮件 MBOX 批处理）
- 图片/截图 OCR 抽取链路
- LLM 驱动的 facet 增量更新（目前 upsert_facet 走规则）
- 神经单元网格式：多 scene 并发自激活 + 人物间的自发交互事件
- 多图谱联邦（一个 skill 引用另一个 skill 的 person/relation）
- 宿主适配层扩展（Coze / LangChain / 飞书机器人）
