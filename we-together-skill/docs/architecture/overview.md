# Architecture Overview（v0.9.0）

## 层级

```
┌──────────────────────────────────────────────────────────────────┐
│                        we-together CLI                           │
│           (src/we_together/cli.py dispatch → scripts/)           │
└───────┬───────────────────────────┬──────────────────────────────┘
        │                           │
┌───────▼─────────┐     ┌───────────▼──────────────┐
│  runtime / adapter │    │  importers (文本/邮件/图片) │
│  claude / openai / │    │                          │
│  feishu / lc /     │    │  narration / text_chat /  │
│  coze / mcp        │    │  email / wechat_db /      │
└───────┬────────────┘    │  imessage / mbox / image /│
        │                 │  social / llm_extraction  │
┌───────▼─────────┐       └───────────┬──────────────┘
│ chat_service +  │                   │
│ agent_loop_svc  │                   │
└───────┬─────────┘                   │
        │                             │
┌───────▼──────────────────────────────▼──────────────────┐
│                  Services (演化核心)                     │
│ patch_applier  / fusion_service / candidate_store /     │
│ identity_fusion / relation_drift / state_decay /        │
│ memory_cluster / memory_condenser / persona_drift /     │
│ persona_history / relation_history / event_causality /  │
│ memory_recall / memory_archive / relation_conflict /    │
│ self_activation / scene_service / dialogue_service /    │
│ federation / event_bus / rbac / tenant_router           │
└───────┬──────────────────────────────────────────────────┘
        │
┌───────▼─────────┐   ┌────────────────────┐   ┌──────────────┐
│   DB (SQLite)   │   │  Runtime retrieval │   │ observability │
│ migrations      │   │ sqlite_retrieval + │   │ logger /      │
│ 0001-0010       │   │ cross_scene_echoes+│   │ metrics /     │
│ + cold_memories │   │ multi_scene /      │   │ sinks         │
│ + external_refs │   │ as_of              │   │               │
└─────────────────┘   └────────────────────┘   └──────────────┘

Eval：groundtruth → relation_inference / llm_judge → regression
Simulation：what_if (读图谱 + LLM)
Packaging：skill_packager → .weskill.zip
```

## 关键契约

1. **Skill-first**: 所有对话通过 `SkillRequest/SkillResponse`，不绑定宿主
2. **Patch-only**: 图谱所有结构性变更必须走 patch_applier
3. **Event-first**: 任何演化先写 event，再推 patch
4. **Cache-invalidation**: patch 成功 → retrieval_cache 失效
5. **Cold path**: long-inactive memory → cold_memories；as_of 查询不改 cache

## 数据库 schema 组块（migrations 0001-0010）

- 0001 核心实体（persons/identity_links/relations/memories/events/scenes）
- 0002 连接表（event_participants/event_targets/scene_participants/memory_owners）
- 0003 trace + evolution（patches/snapshots/local_branches/branch_candidates）
- 0004 索引与约束
- 0005 runtime_cache（retrieval_cache）
- 0006 candidate 中间层（identity/event/facet/relation_clues/group_clues）
- 0007 cold_memories + cold_memory_owners
- 0008 external_person_refs（联邦）
- 0009 persona_history（时间维度）
- 0010 event_causality（因果链）

## 与三条 vision 约束的对齐

| 约束 | 对应实现 |
|---|---|
| A 严格工程化 | migrations / ADR / current-status / eval / CHANGELOG / schema_version |
| B 通用型 Skill | SkillRequest/Response + 6 个宿主 adapter + `.weskill.zip` + CLI |
| C 可自演化生态圈 | neural mesh（multi_scene / condenser / drift / pair / echo / causality / recall） |

## 依赖

核心路径零运行时依赖（只用 stdlib）。optional：

- `anthropic>=0.34` (LLM 接入)
- `openai>=1.40` (OpenAI-compat)
- `pytest/ruff/mypy` (dev)
