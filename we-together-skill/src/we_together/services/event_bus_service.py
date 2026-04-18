"""事件广播总线：scene-to-scene / skill-to-skill 的轻量本地 jsonl 队列。

实现原则：
  - 无外部依赖，仅标准库
  - 发布者 publish_event(bus_dir, topic, payload) → 写一行 jsonl
  - 订阅者 drain_events(bus_dir, topic, handler, *, checkpoint_file) → 读未读行
  - checkpoint 以 sidecar 文件 {topic}.cursor 保存最后消费偏移

这保证无共享网络时也能在一台机器上做多 skill 实例协同。
"""
from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable


def _topic_file(bus_dir: Path, topic: str) -> Path:
    return bus_dir / f"{topic}.jsonl"


def _cursor_file(bus_dir: Path, topic: str) -> Path:
    return bus_dir / f"{topic}.cursor"


def publish_event(bus_dir: Path, topic: str, payload: dict) -> str:
    bus_dir.mkdir(parents=True, exist_ok=True)
    event_id = f"bus_{uuid.uuid4().hex[:12]}"
    line = json.dumps({
        "event_id": event_id,
        "topic": topic,
        "published_at": datetime.now(UTC).isoformat(),
        "payload": payload,
    }, ensure_ascii=False)
    with _topic_file(bus_dir, topic).open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return event_id


def drain_events(
    bus_dir: Path, topic: str, handler: Callable[[dict], None],
) -> int:
    f = _topic_file(bus_dir, topic)
    if not f.exists():
        return 0
    cursor = _cursor_file(bus_dir, topic)
    start = 0
    if cursor.exists():
        try:
            start = int(cursor.read_text() or "0")
        except ValueError:
            start = 0
    processed = 0
    with f.open("r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i < start:
                continue
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except json.JSONDecodeError:
                continue
            handler(evt)
            processed += 1
    new_offset = start + processed
    cursor.write_text(str(new_offset))
    return processed


def peek_events(bus_dir: Path, topic: str, *, limit: int = 10) -> list[dict]:
    f = _topic_file(bus_dir, topic)
    if not f.exists():
        return []
    out: list[dict] = []
    with f.open("r", encoding="utf-8") as fh:
        lines = fh.readlines()
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


# --- Backend protocol（NATS / Redis Stream 可作为 drop-in 替换） ---

class BusBackend:
    """Bus backend Protocol."""
    def publish(self, topic: str, payload: dict) -> str: ...
    def drain(self, topic: str, handler) -> int: ...


class LocalFileBackend:
    """默认 backend：写本地 jsonl。等同上面的模块级函数。"""
    name = "local_file"

    def __init__(self, bus_dir: Path):
        self.bus_dir = bus_dir

    def publish(self, topic: str, payload: dict) -> str:
        return publish_event(self.bus_dir, topic, payload)

    def drain(self, topic: str, handler) -> int:
        return drain_events(self.bus_dir, topic, handler)


class NATSStubBackend:
    """NATS stub：接口占位，真实实现延迟到有 nats-py 依赖时接入。

    当前只记录 publish 调用，drain 返回 0。
    """
    name = "nats_stub"

    def __init__(self, *, server_url: str | None = None):
        self.server_url = server_url
        self.published: list[tuple[str, dict]] = []

    def publish(self, topic: str, payload: dict) -> str:
        self.published.append((topic, dict(payload)))
        return f"nats_stub_{len(self.published)}"

    def drain(self, topic: str, handler) -> int:
        return 0
