"""MCP (Model Context Protocol) adapter：把 we-together 暴露为 MCP server tool schema。

MCP tool schema 与 Anthropic tool schema 形状相近：
  {
    name, description, inputSchema (JSON Schema)
  }

这里只提供转换函数 build_mcp_tools()，把已有 SkillRequest tools 或内部工具集合翻译过去。
实际 MCP server 启动（stdio / SSE）留给后续实现；当前保持纯数据。
"""
from __future__ import annotations


WE_TOGETHER_MCP_TOOLS = [
    {
        "name": "we_together_run_turn",
        "description": "Run a scene-aware conversation turn.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scene_id": {"type": "string"},
                "input": {"type": "string"},
            },
            "required": ["scene_id", "input"],
        },
    },
    {
        "name": "we_together_graph_summary",
        "description": "Return graph summary for a scene.",
        "inputSchema": {
            "type": "object",
            "properties": {"scene_id": {"type": "string"}},
            "required": ["scene_id"],
        },
    },
]


def build_mcp_tools(extra: list[dict] | None = None) -> list[dict]:
    return list(WE_TOGETHER_MCP_TOOLS) + list(extra or [])
