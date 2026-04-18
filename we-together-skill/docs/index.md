# we-together

> Skill-first 的社会 + 世界图谱运行时——不是给 LLM 加一层 memory，而是给 LLM 一个**可演化的数字社会**。

**当前版本**: v0.16.0（tests 594 passed / ADR 52 条 / 不变式 25 条）

## 为什么这个项目

现有 LLM memory 方案（Mem0 / Letta / LangMem）都把 memory 当**键值或向量**。
但真正的"数字赛博生态圈"需要：

- **社会结构**：人 + 关系 + 群 + 场景
- **世界结构**：物 + 地 + 项目
- **时间演化**：tick + drift + decay + unmerge + dream
- **多 agent 互动**：互听 + 打断 + 私聊
- **Agent 自主**：内在驱动力 + 梦循环 + 学习
- **可逆 + 可审计**：事件 → patch → snapshot → rollback

we-together 把这些做到一个 **SQLite-based Skill runtime**。

## 三支柱

- **A 严格工程化**：55 条 ADR / 27 条不变式 / 90% 测试覆盖
- **B 通用型 Skill**：3 路宿主（Claude / OpenAI / MCP）+ 4 类 plugin + 联邦 v1.1
- **C 数字赛博生态圈**：tick + 神经网格 + 遗忘 + 多 agent + 世界建模 + Agent 元能力

## 开始

1. [5 分钟快速上手](getting-started.md)
2. [接入 Claude](hosts/claude-code.md)
3. [写一个 plugin](plugins/authoring.md)
4. [跑一周自演化](tick-scheduling.md)

## 对比

- [vs Mem0](comparisons/vs_mem0.md)
- [vs Letta / MemGPT](comparisons/vs_letta.md)
- [vs LangMem](comparisons/vs_langmem.md)

## 项目状态

参见 [当前状态](superpowers/state/current-status.md)。

## 贡献

欢迎 PR / issue。见 [CONTRIBUTING.md](https://github.com/example/we-together/blob/main/CONTRIBUTING.md)。

## 许可

MIT
