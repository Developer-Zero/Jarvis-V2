from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Message:
    device_id: str
    type: str # hello, input, tool_call, final_answer, event, heartbeat, error
    request_id: str
    timestamp: int
    payload: Any
    encoding: str | None # text, wav, json
    metadata: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "type": self.type,
            "payload": self.payload,
            "encoding": self.encoding,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            device_id=data["device_id"],
            type=data["type"],
            request_id=data["request_id"],
            timestamp=data["timestamp"],
            payload=data.get("payload"),
            encoding=data.get("encoding", "text"),
            metadata=data.get("metadata"),
        )

    
