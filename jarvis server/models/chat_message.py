from dataclasses import dataclass
from typing import Any, Dict

from models import ToolCall


@dataclass
class ChatMessage:
    role: str
    content: str | ToolCall
    timestamp: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=data["timestamp"],
        )

    
