"""SkillRuntime 协议：把社会图谱 retrieval_package 与 user 输入 抽象为与宿主无关的请求/响应。

原则：
- 不依赖任何 LLM SDK
- 不依赖任何 Skill 宿主 API 形状
- 所有字段可序列化（dict / JSON）
- adapters/ 目录下的具体适配器负责把 SkillRequest 翻译为各宿主所需格式
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SkillRequest:
    system_prompt: str
    messages: list[dict]  # [{role, content}]
    retrieval_package: dict
    scene_id: str
    user_input: str
    metadata: dict = field(default_factory=dict)
    tools: list[dict] = field(default_factory=list)  # [{name, description, input_schema}]

    def to_dict(self) -> dict:
        return {
            "system_prompt": self.system_prompt,
            "messages": list(self.messages),
            "retrieval_package": self.retrieval_package,
            "scene_id": self.scene_id,
            "user_input": self.user_input,
            "metadata": dict(self.metadata),
            "tools": [dict(t) for t in self.tools],
        }


@dataclass
class SkillResponse:
    text: str
    speaker_person_id: str | None = None
    supporting_speakers: list[str] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "speaker_person_id": self.speaker_person_id,
            "supporting_speakers": list(self.supporting_speakers),
            "usage": dict(self.usage),
            "raw": dict(self.raw),
        }
