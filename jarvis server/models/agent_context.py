from dataclasses import dataclass

from models import ChatMessage, Connection, Capability

@dataclass
class AgentContext:
    messages: list[ChatMessage]
    current_steps: int
    connections: list[Connection]
    tool_calls: list[dict]
    capabilities: dict[str, Capability]