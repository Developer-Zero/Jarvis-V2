from dataclasses import dataclass
from typing import Any

@dataclass
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "args": self.args,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolCall":
        return cls(
            id=data["id"],
            name=data["name"],
            args=data.get("args", {}),
        )

@dataclass
class ToolResult:
    id: str
    status: str # "ok", "error"
    content: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "content": self.content,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolResult":
        return cls(
            id=data["id"],
            status=data["status"],
            content=data["content"],
        )