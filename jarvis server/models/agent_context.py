from dataclasses import dataclass

from models import ChatMessage, Capability

from typing import Dict

@dataclass
class AgentContext:
    messages: list[ChatMessage]
    semantic_memories: list[dict]
    episodic_memories: list[dict]
    devices: Dict[str, dict]  # [{"device_id": str, "name": str, ...}]
    capabilities: dict[str, list[Capability]] # {"device_id": [Capability]}
    final_answer: bool # when true agent needs to return final answer, not tool calls

    def to_dict(self) -> dict:
        return {
            "messages": [msg.to_dict() for msg in self.messages],
            "devices": self.devices,
            "capabilities": {device_id: [cap.to_dict() for cap in caps] for device_id, caps in self.capabilities.items()},
            "gender": self.gender,
            "location": self.location,
            "final_answer": self.final_answer,
        }