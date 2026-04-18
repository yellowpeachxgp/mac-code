# 飞书机器人 示例

把 we-together-skill 作为飞书机器人的后端：飞书 webhook → feishu_adapter → SkillRequest → chat_service → 回复。

## 启动

```bash
we-together bootstrap --root ~/.we-together
we-together create-scene --root ~/.we-together --type work_discussion --summary "飞书群"
# 假设得到 scene_id = scene_abcd

python examples/feishu-bot/server.py --root ~/.we-together --scene-id scene_abcd --port 7000
```

## 反向代理（开发时）

使用 ngrok / cloudflared 把本地端口暴露给公网：

```bash
ngrok http 7000
# 把返回的 https URL + "/" 填到飞书开放平台的事件订阅
```

## 签名验证

设置环境变量以启用：

```bash
export FEISHU_SIGNING_SECRET=xxxxxxxxxx
python examples/feishu-bot/server.py --root ~/.we-together --scene-id scene_abcd
```

未设置时，服务器跳过签名校验（仅开发用）。

## 支持的事件

- `url_verification`（飞书首次订阅时的握手）
- `im.message.receive_v1`（接到用户消息）

消息体会被 `feishu_adapter.parse_webhook_payload` 转换为 SkillRequest，用户文本从 `message.content.text`（JSON 字符串）提取。

## 扩展方向

- 把当前的 "echo 回复" 替换为实际 `chat_service.run_turn`（需要传 LLM client）
- 加多租户 `--tenant-id`（Phase 11 能力）
- 绑定到 `branch-console` 的 8765 端口，在对话中 human-in-the-loop 解决冲突
