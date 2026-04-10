# 当前状态

日期：2026-04-09

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
- retrieval package CLI 在 scene 不存在时已能干净失败并输出明确错误
- 文件/目录导入服务已具备清晰失败路径，并会返回 `skipped_count` / `skipped_files`
- 文件/目录导入 CLI 在目标路径缺失时已能干净失败并输出明确错误
- 当前本地全量测试通过：92 passed

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

下一步建议：

- 继续扩展运行时世界引擎，把 group / memory / relation 的传播做成更系统的 bounded activation
- 扩 patch applier 与 event->patch 链，补齐更多结构化变更类型和失败状态留痕
- 在保持严格工程化的前提下，逐步接真实平台 importer 与宿主适配层
