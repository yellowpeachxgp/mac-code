"""多人共演对话编排服务：串联 retrieval + SkillRuntime + LLM + dialogue_turn。

这是 Skill 运行时的主入口。REPL 仅作薄层封装。
"""
from __future__ import annotations

from pathlib import Path

from we_together.llm.client import LLMClient
from we_together.runtime.adapters import ClaudeSkillAdapter, OpenAISkillAdapter
from we_together.runtime.prompt_composer import build_skill_request
from we_together.runtime.skill_runtime import SkillResponse
from we_together.runtime.sqlite_retrieval import (
    build_runtime_retrieval_package_from_db,
)
from we_together.services.dialogue_service import (
    record_dialogue_event,
)
from we_together.services.patch_applier import apply_patch_record
from we_together.services.patch_service import infer_dialogue_patches

ADAPTERS = {
    "claude": ClaudeSkillAdapter,
    "openai": OpenAISkillAdapter,
    "openai_compat": OpenAISkillAdapter,
}


def get_adapter(name: str):
    cls = ADAPTERS.get(name.lower())
    if cls is None:
        raise ValueError(f"Unknown adapter: {name}")
    return cls()


def run_turn(
    db_path: Path,
    scene_id: str,
    user_input: str,
    *,
    llm_client: LLMClient,
    adapter_name: str = "claude",
    history: list[dict] | None = None,
    speaking_person_ids: list[str] | None = None,
    max_recent_changes: int | None = 5,
    tools: list[dict] | None = None,
    tool_dispatcher: dict | None = None,
    max_tool_iters: int = 3,
) -> dict:
    """执行一轮完整对话：
    1) 拉取 retrieval_package
    2) 组装 SkillRequest
    3) 通过 adapter + llm_client 生成回复（tools 非空时走 agent_runner tool-use loop）
    4) 把对话落盘（record + infer + apply）
    """
    # Phase 12 trace_id 注入
    try:
        from we_together.observability.logger import bind_trace_id
        bind_trace_id()
    except Exception:
        pass

    package = build_runtime_retrieval_package_from_db(
        db_path=db_path,
        scene_id=scene_id,
        max_recent_changes=max_recent_changes,
    )
    request = build_skill_request(
        retrieval_package=package,
        user_input=user_input,
        scene_id=scene_id,
        history=history,
    )
    if tools:
        request.tools = list(tools)

    agent_steps: list[dict] = []
    agent_event_ids: list[str] = []
    if tools and tool_dispatcher:
        from we_together.runtime.agent_runner import run_tool_use_loop
        agent_result = run_tool_use_loop(
            request, llm_client=llm_client, tool_dispatcher=tool_dispatcher,
            db_path=db_path, max_iters=max_tool_iters, adapter_name=adapter_name,
        )
        response: SkillResponse = agent_result.response
        agent_steps = agent_result.steps
        agent_event_ids = agent_result.event_ids
    else:
        adapter = get_adapter(adapter_name)
        response = adapter.invoke(request, llm_client=llm_client)

    # 落图谱
    event_result = record_dialogue_event(
        db_path=db_path,
        scene_id=scene_id,
        user_input=user_input,
        response_text=response.text,
        speaking_person_ids=speaking_person_ids,
    )
    patches = infer_dialogue_patches(
        source_event_id=event_result["event_id"],
        scene_id=scene_id,
        user_input=user_input,
        response_text=response.text,
        speaking_person_ids=speaking_person_ids,
    )
    for p in patches:
        apply_patch_record(db_path=db_path, patch=p)

    return {
        "request": request.to_dict(),
        "response": response.to_dict(),
        "event_id": event_result["event_id"],
        "snapshot_id": event_result["snapshot_id"],
        "applied_patch_count": len(patches),
        "agent_steps": agent_steps,
        "agent_event_ids": agent_event_ids,
    }
