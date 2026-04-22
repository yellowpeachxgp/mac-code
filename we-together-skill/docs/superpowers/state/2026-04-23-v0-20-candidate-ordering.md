# v0.20 Candidate Ordering

**Date**: 2026-04-23  
**Basis**: local `v0.19.0` state, `761 passed / 4 skipped`, ADR 0073, release-prep green

## 判断前提

当前本地 `v0.19.0` 已经满足：

- version / CLI / wheel / local tag 一致
- vector backend 真接入 + compare 归档完成
- federation 写路径 + production smoke 完成
- `simulate_year` usage/cost/monthly artifact 骨架完成
- tenant CLI 覆盖面已很广，基本形成多租户基线

因此 `v0.20` 不应再把精力放在“把旧计划里的 stub 补成代码”这类工作上，而应转向：

1. **外部条件才能完成的工作**
2. **当前已铺开的能力的深化**
3. **对外发布和真实使用**

## 推荐阶段顺序

### Phase 72 — Real LLM Operationalization

目标：

- 真 provider 7-day run
- 真 provider 30-day run
- usage/cost 月报样本
- dream_cycle 真 insight 生成

为什么先做：

- 这是当前 `v0.19` 最明显还停留在“框架已就位，证据未落”的方向。
- 一旦能跑出小预算真实样本，后面无论是对外发布还是 v0.20 叙述都会更有说服力。

### Phase 73 — Release Externalization

目标：

- GitHub Release
- PyPI 正式发布
- release checklist 与发布流程的真实演练

为什么排第二：

- 本地 release-prep 已经全绿，剩下的主要是外部动作。
- 如果先不走真实发布，很多发布工程只能停留在“理论上没问题”。

### Phase 74 — Tenant/World Isolation Deepening

目标：

- cross-tenant leakage 更系统的负向测试
- world namespace / tenant namespace contract
- tenant-aware RBAC 接线起步

为什么排第三：

- 当前 tenant 路由已经足够广，继续补 `--tenant-id` 的收益快速下降。
- 下一步应该从“能跑”提升到“更强隔离语义”。

### Phase 75 — Performance Regression CI

目标：

- benchmark contract 明确化
- nightly compare 更系统
- 性能回退告警 / 基线对比

为什么排第四：

- 100k / 1M 证据已经有了，下一步自然是把这些证据变成长期守门规则。
- 这一步会直接提升后续所有大规模演进的信心。

### Phase 76 — Narrative / Task Decomposition Intelligence

目标：

- narrative_v2
- agent task decomposition
- 更强的多 agent 协作目标完成

为什么排第五：

- 这是有价值但不紧急的“深化差异化”工作。
- 需要建立在真实运行、发布和性能守门都更稳之后做，性价比更高。

## 明确不建议优先做的事

- 再大规模补 tenant 参数
  - 当前已经超过“可用”阈值，边际收益很低。
- 再做更多纯本地打磨
  - 当前最缺的是外部证据，不是本地再多 20 个脚本支持。
- 立即推进多 world 大重构
  - 现在更适合先做 namespace contract 和负向测试，而不是一口气改架构。

## 一句话结论

如果按工程价值排序，`v0.20` 最应该优先做的是：

`真 LLM 小预算实跑 -> 真实发布 -> tenant/world 隔离深化 -> 性能回退 CI -> narrative/decomposition 深化`
