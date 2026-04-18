# 教程：给家庭成员建图谱

**场景**：你想让自己的 Claude/Codex agent 记住"谁是谁、谁跟谁什么关系、最近家里发生了什么"。

**时间**：15 分钟。

## 1. 初始化

```bash
git clone <repo> wt && cd wt
python -m venv .venv && source .venv/bin/activate
pip install -e .
python scripts/bootstrap.py --root .
```

## 2. 创建人物 + 场景

```bash
# 给家里 4 人各建一个 person
python -c "
import sqlite3
conn = sqlite3.connect('db/main.sqlite3')
for pid, name in [
    ('p_dad', '爸爸'), ('p_mom', '妈妈'),
    ('p_me', '我'), ('p_sis', '妹妹'),
]:
    conn.execute(
        \"INSERT INTO persons(person_id, primary_name, status, confidence, \"
        \"metadata_json, created_at, updated_at) VALUES(?, ?, 'active', 0.95, \"
        \"'{}', datetime('now'), datetime('now'))\",
        (pid, name),
    )
conn.commit()
"
```

## 3. 创建一个"家庭晚餐"场景

```bash
python scripts/create_scene.py --scene-type family_dinner \
  --participants p_dad p_mom p_me p_sis
```

## 4. 导入一段叙述

```bash
python scripts/import_narration.py --scene <scene_id> \
  --text "今晚爸爸做了他最拿手的糖醋排骨。妹妹期末考了第一名，我们都很开心。"
```

## 5. 看图谱

```bash
python scripts/dashboard.py --port 7780
# 浏览器访问 http://127.0.0.1:7780
```

应能看到 4 个 person，1 个 scene，若干 event / memory。

## 6. 跑一次对话

```bash
python scripts/chat.py
# > 爸爸昨天做了什么菜？
```

Skill 会检索家庭图谱并回答。

## 7. 让图谱自演化一周

```bash
python scripts/simulate_week.py --ticks 7 --budget 3 --archive
```

归档在 `benchmarks/tick_runs/*.json`。

## 8. 跑梦循环

```bash
python scripts/dream_cycle.py --root . --lookback 30
```

应看到图谱自动压缩旧 memory + 产出一条 insight 记忆。

## 9. 进阶

- `scripts/world_cli.py register-object --name "爸爸的乐高模型" --owner-id p_dad`
- `scripts/world_cli.py register-place --name "家" --scope venue`
- `scripts/multi_agent_chat.py --scene <scene_id> --turns 3` 让多个家庭成员同时发言

## 10. 接入 Claude Code

见 [`docs/hosts/claude-code.md`](../hosts/claude-code.md)。
