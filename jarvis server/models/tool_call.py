from dataclasses import dataclass
from typing import Any
import time

@dataclass
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]
