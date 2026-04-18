---
adr: 0058
title: Phase 56 — 发布准备（PyPI / Claude Skills checklist）
status: Accepted
date: 2026-04-19
---

# ADR 0058: Phase 56 — 发布准备

## 状态
Accepted — 2026-04-19

## 背景
v0.16 已能 build wheel + tag，但**从未提交 PyPI / Claude Skills**。B 支柱"真被消费"的最后一英里需要**固化发布流程**：checklist、dry-run、release_prep 自检脚本。

## 决策

### D1. PyPI Checklist
`docs/release/pypi_checklist.md`：
- 前置：tag 存在 / pytest 绿 / CHANGELOG / wheel 验证
- `twine check dist/*` 元数据自检
- TestPyPI dry-run → 隔离 venv 安装
- 正式 PyPI upload + 安装回验
- 故障排查

### D2. Claude Skills 提交材料
`docs/release/claude_skills_submission.md`：
- Skill metadata JSON
- 支持的 host（Claude Desktop / Claude Code / OpenAI）
- tool / resource / prompt 清单
- PII + visibility 合规声明
- 打包 + 验证流程
- **不代表已提交**，由 Core Maintainer 决定

### D3. release_prep.py 自检
`scripts/release_prep.py --version X.Y.Z`：
- pyproject.toml / cli.py VERSION 一致性
- CHANGELOG entry 存在
- release_notes 文件存在
- git tag 存在
- wheel artifact 存在
- 输出 JSON 报告 + 下一步命令

任何 ok=False → 返回 exit 1，阻挡错误发布。

### D4. 不做的事
- 不自动上传 PyPI（必须人工触发 + token）
- 不自动提交 Claude Skills marketplace（外部流程）
- 不修改 GitHub Actions release workflow（留在已有 publish.yml）

## 版本锚点
- 新文件: `docs/release/pypi_checklist.md` / `docs/release/claude_skills_submission.md` / `scripts/release_prep.py`
- 无新 migration / service
- 无新不变式

## 拒绝的备选
- 全自动发布：token 被 leak 风险
- 引入 twine 为硬依赖：它是 optional（release 才用）
- 代 CLI 填 token：违反 SECURITY.md
