from dataclasses import dataclass
from typing import Any

from models import ToolCall, ToolResult


@dataclass
class ChatMessage:
    role: str

    text: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_result: ToolResult | None = None

    timestamp: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "text": self.text,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls] if self.tool_calls else None,
            "tool_result": self.tool_result.to_dict() if self.tool_result else None,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChatMessage":
        return cls(
            role=data["role"],
            text=data.get("text"),
            tool_calls=[ToolCall.from_dict(tc) for tc in data.get("tool_calls", [])] if data.get("tool_calls") else None,
            tool_result=ToolResult.from_dict(data["tool_result"]) if data.get("tool_result") else None,
            timestamp=data["timestamp"],
        )