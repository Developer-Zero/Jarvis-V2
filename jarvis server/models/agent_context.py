from dataclasses import dataclass

from models import ChatMessage, Connection

@dataclass
class AgentContext:
    messages: list[ChatMessage]
    semantic_memories: list[dict]
    episodic_memories: list[dict]
    connections: list[dict]  # [{"device_id": str, "name": str, ...}]
    capabilities: dict[str, list[dict]] # {"device_id": [Capability]}
    gender: str = "male"
    location: str | None = None
    final_answer: bool # when true agent needs to return final answer, not tool calls

    def to_dict(self) -> dict:
        return {
            "messages": [msg.to_dict() for msg in self.messages],
            "connections": [conn.__dict__ for conn in self.connections],
            "capabilities": {name: [cap.to_dict() for cap in caps] for name, caps in self.capabilities.items()},
            "gender": self.gender,
            "location": self.location,
            "final_answer": self.final_answer,
        }