"""Agent tool-use 运行器（真接 adapter）：让 chat_service.run_turn 能在 tools
非空时走 tool_call → tool_result → respond 的真循环。

与 `services/agent_loop_service` 对比：
  - agent_loop_service：独立 loop，不走 adapter；用 LLM.chat_json 驱动
  - agent_runner（本模块）：挂在 chat_service 流程内，能 reuse retrieval_package +
    SkillRequest 的所有字段（system_prompt/messages/tools）

为了兼容 mock-first 测试，驱动协议仍是 LLM.chat_json，action schema：
  {"action": "tool_call", "tool": str, "args": dict}
  {"action": "respond", "text": str}
这让未来真 Claude tool_use content_block 转换只需在 adapter 层加 parse。
"""
from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from we_together.db.connection import connect
from we_together.llm.client import LLMClient, LLMMessage
from we_together.runtime.skill_runtime import SkillRequest, SkillResponse


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _log_event(db_path: Path | None, scene_id: str, event_type: str, summary: str) -> str | None:
    if db_path is None:
        return None
    eid = f"evt_{event_type}_{uuid.uuid4().hex[:10]}"
    conn = connect(db_path)
    conn.execute(
        """INSERT INTO events(event_id, event_type, source_type, scene_id, timestamp,
           summary, visibility_level, confidence, is_structured,
           raw_evidence_refs_json, metadata_json, created_at)
           VALUES(?, ?, 'agent_runner', ?, ?, ?, 'visible', 0.7, 1, '[]', '{}', ?)""",
        (eid, event_type, scene_id, _now(), summary, _now()),
    )
    conn.commit()
    conn.close()
    return eid


@dataclass
class AgentRunResult:
    response: SkillResponse
    steps: list[dict]
    event_ids: list[str]


def run_tool_use_loop(
    request: SkillRequest,
    *,
    llm_client: LLMClient,
    tool_dispatcher: dict[str, Callable[[dict], str]],
    db_path: Path | None = None,
    max_iters: int = 3,
    adapter_name: str = "openai_compat",
) -> AgentRunResult:
    """真 tool-use loop：兼容已有 chat_json 的 MockLLMClient。

    未来真 Anthropic tool_use：adapter 层在 parse_response 时把 content_block
    of type 'tool_use' 翻译为 {"action": "tool_call", ...}，本函数保持不变。
    """
    messages: list[LLMMessage] = [LLMMessage(role="system", content=request.system_prompt)]
    for m in request.messages:
        messages.append(LLMMessage(role=m["role"], content=m["content"]))

    steps: list[dict] = []
    event_ids: list[str] = []

    for _ in range(max_iters):
        try:
            payload = llm_client.chat_json(
                messages,
                schema_hint={"action": "tool_call|respond",
                              "tool": "str?", "args": "obj?", "text": "str?"},
            )
        except Exception as exc:
            final = f"[agent error] {exc}"
            return AgentRunResult(
                response=SkillResponse(text=final, raw={"adapter": adapter_name, "error": True}),
                steps=steps + [{"type": "error", "text": final}],
                event_ids=event_ids,
            )

        action = payload.get("action", "respond")
        if action == "tool_call":
            tool = str(payload.get("tool", ""))
            args = payload.get("args") or {}
            steps.append({"type": "tool_call", "tool": tool, "args": args})
            eid = _log_event(db_path, request.scene_id, "tool_use_event",
                              f"call {tool} args={args}")
            if eid: event_ids.append(eid)

            if tool not in tool_dispatcher:
                result = f"[unknown tool {tool}]"
                is_error = True
            else:
                try:
                    result = tool_dispatcher[tool](args)
                    is_error = False
                except Exception as exc:
                    result = f"[tool error] {exc}"
                    is_error = True
            steps.append({"type": "tool_result", "tool": tool, "result": result,
                           "is_error": is_error})
            eid2 = _log_event(db_path, request.scene_id, "tool_result_event",
                               f"result {tool}={result[:80]} err={is_error}")
            if eid2: event_ids.append(eid2)
            messages.append(LLMMessage(role="assistant", content=f"tool_call {tool}"))
            messages.append(LLMMessage(role="user",
                                         content=f"tool_result: {result}" +
                                                 (" [ERROR]" if is_error else "")))
            continue

        text = str(payload.get("text", "") or "").strip()
        steps.append({"type": "respond", "text": text})
        policy = request.retrieval_package.get("response_policy", {})
        resp = SkillResponse(
            text=text,
            speaker_person_id=policy.get("primary_speaker"),
            supporting_speakers=list(policy.get("supporting_speakers", [])),
            raw={"adapter": adapter_name, "tool_use": True, "step_count": len(steps)},
        )
        return AgentRunResult(response=resp, steps=steps, event_ids=event_ids)

    # max_iters 用光
    final = "[agent exhausted max_iters]"
    return AgentRunResult(
        response=SkillResponse(text=final, raw={"adapter": adapter_name,
                                                 "exhausted": True}),
        steps=steps + [{"type": "exhausted", "text": final}],
        event_ids=event_ids,
    )
