from dataclasses import dataclass
from typing import Any

@dataclass
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]
